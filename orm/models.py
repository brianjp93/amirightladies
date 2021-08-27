from typing import Optional, List, Union
from sqlmodel import SQLModel, Field, Relationship, select, Session
from discord.member import Member as DMember
from discord.guild import Guild as DGuild
from db import engine


class MemberGuildLink(SQLModel, table=True):
    guild_id: Optional[int] = Field(
        default=None, foreign_key="guild.id", primary_key=True
    )
    member_id: Optional[int] = Field(
        default=None, foreign_key="member.id", primary_key=True
    )


class Guild(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exid: int
    members: List["Member"] = Relationship(back_populates="guilds", link_model=MemberGuildLink)


class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exid: int
    name: str
    nick: Optional[str]
    discriminator: str
    bot: bool = False

    guilds: List[Guild] = Relationship(back_populates="members", link_model=MemberGuildLink)

    @staticmethod
    def create_from_member(member: DMember) -> Union['Member', None]:
        """Creates / Updates Member and associated Guild.
        """
        member_id = getattr(member, 'id', None)
        with Session(engine) as session:
            guild: DGuild = member.guild
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
                "name": getattr(member, 'name', ''),
                "discriminator": getattr(member, 'discriminator', ''),
                "bot": getattr(member, 'bot', False),
                "nick": member.nick,
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

            if new_member:
                new_member.guilds.extend([new_guild] or [])
            session.add(new_member)
            session.commit()
        return new_member
