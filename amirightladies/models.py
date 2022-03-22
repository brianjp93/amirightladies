from __future__ import annotations
from discord.member import Member as DMember
from discord.user import User as DUser
from discord.guild import Guild as DGuild
from tortoise import models, fields


class HistorySong(models.Model):
    id = fields.IntField(pk=True)
    song = fields.ForeignKeyField('models.Song', on_delete=fields.CASCADE, null=False)
    guild = fields.ForeignKeyField('models.Guild', related_name='history', on_delete=fields.CASCADE, null=False)
    created_at = fields.DatetimeField(auto_now_add=True, null=False)


class Guild(models.Model):
    id = fields.IntField(pk=True)
    exid = fields.IntField(null=False)

    @classmethod
    async def get_from_discord_guild(cls, dguild: DGuild | None):
        if not dguild:
            return
        return await cls.filter(exid=dguild.id).first()


class Member(models.Model):
    id = fields.IntField(pk=True)
    exid = fields.IntField()
    name = fields.CharField(max_length=64, null=False)
    nick = fields.CharField(max_length=64, null=True)
    discriminator = fields.CharField(max_length=64, null=False)
    bot = fields.BooleanField(default=False)
    guilds = fields.ManyToManyField(model_name="models.Guild", related_name="members")

    @staticmethod
    async def create_from_member(member: DMember | DUser) -> 'Member'| None:
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
    guild = fields.ForeignKeyField(model_name='models.Guild', related_name='defersongs', default=None, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
