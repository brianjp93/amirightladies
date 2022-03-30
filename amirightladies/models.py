from __future__ import annotations
from discord.member import Member as DMember
from discord.user import User as DUser
from discord.guild import Guild as DGuild
from prisma import get_client
from prisma import models
from prisma import types


async def get_from_discord_guild(dguild: DGuild | None):
    if not dguild:
        return
    return await models.Guild.prisma().find_first(where={"exid": dguild.id})


def get_playlist(guild_id: int, take: int | None=None, skip: int|None=None):
    return models.DeferSong.prisma().find_many(
        where={"guild_id": guild_id},
        order={"sort_int": "asc"},
        take=take,
        skip=skip,
    )

async def create_from_member(member: DMember | DUser):
    """Creates / Updates Member and associated Guild."""
    member_id = member.id
    guild: DGuild | None = getattr(member, "guild")
    new_guild = None
    if guild:
        new_guild = await models.Guild.prisma().find_first(where={"exid": guild.id})
        print("Searching for existing guild.")
        if not new_guild:
            print("Creating new guild.")
            new_guild = await models.Guild.prisma().create({"exid": guild.id})

    new_member = await models.Member.prisma().find_first(where={"exid": member_id})
    update: types.MemberUpsertInput = {
        "create": {
            "name": member.name,
            "discriminator": member.discriminator,
            "bot": member.bot,
            "nick": getattr(member, "nick", ""),
            "exid": member.id,
        },
        "update": {
            "name": member.name,
            "discriminator": member.discriminator,
            "bot": member.bot,
            "nick": getattr(member, "nick", ""),
        },
    }
    new_member = await models.Member.prisma().upsert(
        where={"exid": member_id}, data=update
    )
    if new_guild:
        await models.Guild.prisma().update(
            where={"id": new_guild.id},
            data={"members": {"connect": [{"id": new_member.id}]}},
        )
    return new_member


def last(guild_id: int):
    return models.DeferSong.prisma().find_first(
        where={"guild_id": guild_id}, order={"sort_int": "desc"}
    )


async def move_to_start(defersong_id: int):
    song1 = await models.DeferSong.prisma().find_first(where={"id": defersong_id})
    if not song1:
        return
    guild_id = song1.guild_id
    start = await models.DeferSong.prisma().find_first(where={'guild_id': guild_id}, order={"sort_int": "asc"})
    if start and start.id != song1.id:
        start.sort_int = start.sort_int - 1
        song1.sort_int = start.sort_int + 1
        async with get_client().batch_() as batcher:
            batcher.defersong.update(where={'id': start.id}, data={'sort_int': start.sort_int})
            batcher.defersong.update(where={'id': song1.id}, data={'sort_int': song1.sort_int})
