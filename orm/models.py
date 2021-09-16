from typing import Optional, List, Union
from sqlmodel import SQLModel, Field, Relationship, select
from sqlalchemy import Column, VARCHAR
from discord.member import Member as DMember
from discord.user import User as DUser
from discord.guild import Guild as DGuild
from app import session


class MemberGuildLink(SQLModel, table=True):
    guild_id: Optional[int] = Field(
        default=None, foreign_key="guild.id", primary_key=True
    )
    member_id: Optional[int] = Field(
        default=None, foreign_key="member.id", primary_key=True
    )


class HistorySong(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    song_id: Optional[int] = Field(foreign_key='song.id')
    song: Optional['Song'] = Relationship()
    created_at: int

    guild_id: Optional[int] = Field(foreign_key='guild.id')
    guild: Optional['Guild'] = Relationship(back_populates='history')


class GuildSongLink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    song: Optional[int] = Field(
        default=None, foreign_key="song.id"
    )
    guild: Optional[int] = Field(
        default=None, foreign_key="guild.id"
    )
    sort_int: int = 0


class Guild(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exid: int

    members: List["Member"] = Relationship(back_populates="guilds", link_model=MemberGuildLink)
    songs: List['Song'] = Relationship(back_populates='guilds', link_model=GuildSongLink)
    history: List['HistorySong'] = Relationship(back_populates='guild')


class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exid: int
    name: str
    nick: Optional[str]
    discriminator: str
    bot: bool = False

    guilds: List[Guild] = Relationship(back_populates="members", link_model=MemberGuildLink)

    @staticmethod
    def create_from_member(member: Union[DMember, DUser]) -> Union['Member', None]:
        """Creates / Updates Member and associated Guild.
        """
        member_id = member.id
        guild: Union[DGuild, None] = getattr(member, 'guild')
        new_guild = None
        if guild:
            statement = select(Guild).where(Guild.exid == guild.id)
            print('Searching for existing guild.')
            new_guild = session.exec(statement).first()
            if not new_guild:
                print('Creating new guild.')
                new_guild = Guild(exid=guild.id)
            session.add(new_guild)
            session.commit()

        new_member = session.exec(
            select(Member).where(Member.exid == member_id)
        ).first()
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

        if new_member and new_guild:
            new_member.guilds.extend([new_guild] or [])
        session.add(new_member)
        session.commit()
        return new_member


class Song(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # video_id
    stream_id: str = Field(sa_column=Column('stream_id', VARCHAR, unique=True))
    title: str
    url: str
    file: str
    guilds: List[Guild] = Relationship(back_populates="songs", link_model=GuildSongLink)
