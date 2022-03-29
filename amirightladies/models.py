from __future__ import annotations
from typing import cast
from discord.member import Member as DMember
from discord.user import User as DUser
from discord.guild import Guild as DGuild
from prisma import models
from prisma import types


class HistorySong(models.HistorySong):
    pass

class Guild(models.Guild):
    @classmethod
    async def get_from_discord_guild(cls, dguild: DGuild | None):
        if not dguild:
            return
        return await cls.prisma().find_first(where={'exid': dguild.id})

    @staticmethod
    def get_playlist(guild_id: int):
        return models.DeferSong.prisma().find_many(
            where={'guild_id': guild_id},
            order={'sort_int': 'asc'},
        )


class Member(models.Member):
    @classmethod
    async def create_from_member(cls, member: DMember | DUser) -> Member | None:
        """Creates / Updates Member and associated Guild.
        """
        member_id = member.id
        guild: DGuild | None = getattr(member, 'guild')
        new_guild = None
        if guild:
            new_guild = await Guild.prisma().find_first(where={'exid': guild.id})
            print('Searching for existing guild.')
            if not new_guild:
                print('Creating new guild.')
                new_guild = await Guild.prisma().create({
                    'exid': guild.id
                })

        new_member = await cls.prisma().find_first(where={'exid': member_id})
        update = {
            "name": member.name,
            "discriminator": member.discriminator,
            "bot": member.bot,
            "nick": getattr(member, 'nick', ''),
            "exid": member.id,
        }
        if new_member:
            print('Updating member.')
            update = cast(types.MemberUpdateInput, update)
            for key, val in update.items():
                setattr(new_member, key, val)
            new_member = await cls.prisma().update(where={'exid': member_id}, data=update)
        elif member_id:
            update = cast(types.MemberCreateInput, update)
            print('Creating new member.')
            new_member = await cls.prisma().create(
                data=update
            )

        if new_member and new_guild:
            new_member.guilds
            await cls.prisma().update(
                where={'id': new_member.id},
                data={
                    'guilds': {'push': [new_guild.id]}
                }
            )
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
