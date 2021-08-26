from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Session
from discord.member import Member as DMember
from discord.guild import Guild as DGuild
from db import engine


class Guild(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exid: int
    members: List["Member"] = Relationship(back_populates="guild")


class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exid: int
    name: str
    nick: Optional[str]
    discriminator: str
    bot: bool = False

    guild_id: Optional[int] = Field(default=None, foreign_key="guild.id")
    guild: Optional[Guild] = Relationship(back_populates="members")

    @staticmethod
    def create_from_member(member: DMember) -> 'Member':
        with Session(engine) as session:
            guild: DGuild = member.guild
            new_guild = Guild(exid=guild.id)
            session.add(new_guild)
            session.commit()

            new_member = Member(
                exid=member.id,
                name=member.name,
                discriminator=member.discriminator,
                bot=member.bot,
                nick=member.nick,
                guild_id=new_guild.id,
            )
            session.add(new_member)
            session.commit()
        return new_member
