from __future__ import annotations
from discord.member import Member as DMember
from discord.user import User as DUser
from discord.guild import Guild as DGuild
from tortoise import models, fields
from tortoise.queryset import QuerySet


class HistorySong(models.Model):
    id = fields.IntField(pk=True)
    song = fields.ForeignKeyField('models.Song', on_delete=fields.CASCADE, null=False)
    guild = fields.ForeignKeyField('models.Guild', related_name='history', on_delete=fields.CASCADE, null=False)
    created_at = fields.DatetimeField(auto_now_add=True, null=False)


class Guild(models.Model):
    id = fields.IntField(pk=True)
    exid = fields.BigIntField(null=False)
    defersongs: QuerySet['DeferSong']

    @classmethod
    async def get_from_discord_guild(cls, dguild: DGuild | None):
        if not dguild:
            return
        return await cls.filter(exid=dguild.id).first()

    def get_playlist(self):
        return self.defersongs.all().order_by('sort_int')


class Member(models.Model):
    id = fields.IntField(pk=True)
    exid = fields.BigIntField()
    name = fields.CharField(max_length=128, null=False)
    nick = fields.CharField(max_length=64, null=True)
    discriminator = fields.CharField(max_length=64, null=False)
    bot = fields.BooleanField(default=False)
    guilds = fields.ManyToManyField(model_name="models.Guild", related_name="members")

    @staticmethod
    async def create_from_member(member: DMember | DUser) -> 'Member' | None:
        """Creates / Updates Member and associated Guild.
        """
        member_id = member.id
        guild: DGuild | None = getattr(member, 'guild')
        new_guild = None
        if guild:
            new_guild = await Guild.filter(exid=guild.id).first()
            print('Searching for existing guild.')
            if not new_guild:
                print('Creating new guild.')
                new_guild = Guild(exid=guild.id)
                await new_guild.save()

        new_member = await Member.filter(exid=member_id).first()
        update = {
            "name": member.name,
            "discriminator": member.discriminator,
            "bot": member.bot,
            "nick": getattr(member, 'nick', ''),
        }
        if new_member:
            print('Updating member.')
            for key, val in update.items():
                setattr(new_member, key, val)
        elif member_id:
            print('Creating new member.')
            new_member = Member(
                exid=member_id,
                **update,
            )
            await new_member.save()

        if new_member and new_guild:
            await new_member.guilds.add(new_guild)
        return new_member


class Song(models.Model):
    id = fields.IntField(pk=True)
    # video_id
    stream_id = fields.CharField(max_length=512, unique=True)
    title = fields.CharField(max_length=512)
    url = fields.CharField(max_length=512)
    file = fields.CharField(max_length=512)


class DeferSong(models.Model):
    id = fields.IntField(pk=True)
    query = fields.CharField(max_length=128, default='')
    song = fields.ForeignKeyField(model_name='models.Song', null=True)
    sort_int = fields.IntField(null=False, blank=True, default=0, index=True)
    guild = fields.ForeignKeyField(model_name='models.Guild', related_name='defersongs', default=None, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (('guild', 'sort_int'),)

    async def save(self, *args, **kwargs):
        # should use some subquery to update the sort_int inside the update I think
        if self.id is None:
            if ds := await DeferSong.filter(guild=self.guild).order_by('-sort_int').first():
                self.sort_int = ds.sort_int + 1
        await super().save(*args, **kwargs)

    @classmethod
    def last(cls, guild_id: int):
        return cls.playlist(guild_id).order_by('-sort_int').first()

    @classmethod
    def playlist(cls, guild_id: int):
        return cls.filter(guild=guild_id).order_by('sort_int')

    async def move_to_start(self):
        assert self.guild
        start = await self.playlist(self.guild.id).first()
        if start:
            start.sort_int = start.sort_int - 1
            await start.save()
            self.sort_int = start.sort_int + 1
            await self.save()
