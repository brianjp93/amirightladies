from .general import CommandHandler
import discord
import re
import settings
from sqlmodel import select

from asyncio import sleep
from datetime import datetime
from typing import Optional
from orm.models import Song, Guild, HistorySong
from app import session
from resources.yt import Yt

yt = Yt()


async def play_songs(vc: discord.VoiceClient, message: discord.Message):
    if guild := Guild.get_from_discord_guild(message.guild):
        session.refresh(guild)
        while guild.songs:
            song = guild.songs[0]
            vc.play(discord.FFmpegPCMAudio(executable='ffmpeg', source=song.file))

            hs = HistorySong(
                song_id=song.id,
                guild_id=guild.id,
                created_at=int(datetime.now().timestamp()),
            )
            session.add(hs)
            session.commit()
            guild.history.append(hs)
            session.commit()

            if message:
                await message.channel.send(f'Playing song: {song.title}')
            while vc.is_playing():
                await sleep(.5)
            session.refresh(guild)
            guild.songs.remove(song)
            session.commit()



class HandleEmptyPlay(CommandHandler):
    pat = r'play'

    async def handle(self):
        assert self.match
        assert self.message.guild
        assert isinstance(self.message.author, discord.Member)
        if guild := Guild.get_from_discord_guild(self.message.guild):
            songs = session.exec(
                select(Song).where(Song.guilds.contains(guild))
            ).fetchmany(10)
            if songs:
                try:
                    assert self.message.author.voice is not None
                    vc = await self.message.author.voice.channel.connect()
                    settings.vc_by_guild[self.message.guild.id] = vc
                    await play_songs(vc, self.message)
                except discord.ClientException as e:
                    print(e)
                    vc = settings.vc_by_guild.get(self.message.guild.id)
                    if vc:
                        await play_songs(vc, self.message)
            else:
                return (['The queue is empty.'], {})


class HandlePlay(CommandHandler):
    pat = r'play (.*)'

    async def handle(self):
        assert self.match is not None
        if content := self.match.groups()[0]:
            if re.match(r'(.*)?youtube.com(.*)?', content):
                return await self.handle_general(yt.get_with_url)
            elif re.match(r'(.*)?spotify(.*)?playlist/([\w\d]+)(.*)?', content):
                pass
                # spotify.add_playlist_to_queue(content)
            else:
                return await self.handle_general(yt.get_with_search)

    async def handle_general(self, handler):
        assert self.message.guild
        content = self.message.content.lower().strip()
        try:
            voice_channel = self.message.author.voice.channel
        except:
            voice_channel = None
            await self.message.channel.send("Couldn't find voice channel.")
        if isinstance(voice_channel, discord.VoiceChannel):
            song: Optional[Song]
            if song := await handler(content):
                if guild := Guild.get_from_discord_guild(self.message.guild):
                    session.refresh(guild)
                    guild.songs.append(song)
                    session.commit()
                    await self.message.channel.send(f'Added to queue: {song.title}')
                    try:
                        vc = await voice_channel.connect()
                        settings.vc_by_guild[self.message.guild.id] = vc
                        await play_songs(vc, self.message)
                    except discord.ClientException as e:
                        print(e)
                        vc = settings.vc_by_guild.get(self.message.guild.id)
                        if vc:
                            await play_songs(vc, self.message)
            else:
                await self.message.channel.send('Could not find song')
        return [[], {}]


class HandleSkip(CommandHandler):
    pat = r'(?:(?:skip)|(?:next))'

    async def handle(self):
        assert self.match
        assert self.message.guild
        if vc := settings.vc_by_guild.get(self.message.guild.id):
            vc.stop()
            if guild := Guild.get_from_discord_guild(self.message.guild):
                session.refresh(guild)
                if guild.songs:
                    song = guild.songs[0]
                    guild.songs.remove(song)
                    session.commit()
                    if guild.songs:
                        await play_songs(vc, self.message)
                    else:
                        await self.message.channel.send('No more songs.')


class HandleQueue(CommandHandler):
    pat = r'queue'

    async def handle(self):
        assert self.match
        assert self.message.guild
        if guild := Guild.get_from_discord_guild(self.message.guild):
            songs = session.exec(
                select(Song).where(Song.guilds.contains(guild))
            ).fetchmany(10)
            embed = discord.Embed()
            output = []
            for i, x in enumerate(songs):
                title = x.title[:30]
                if len(x.title) > 30:
                    title += '...'
                output.append(f'{i + 1}. [{title}]({x.url})')
            output = '\n'.join(output)
            embed.add_field(name='Queue', value=output)
            return [[], {'embed': embed}]


class HandleHistory(CommandHandler):
    pat = r'history'

    async def handle(self):
        assert self.match
        if guild := Guild.get_from_discord_guild(self.message.guild):
            hs = session.exec(
                select(HistorySong).where(
                    HistorySong.guild==guild
                ).order_by(HistorySong.created_at.desc())
            ).fetchmany(10)
            embed = discord.Embed()
            output = []
            for i, x in enumerate(hs):
                if x.song:
                    title = x.song.title[:30]
                    if len(x.song.title) > 30:
                        title += '...'
                    output.append(f'{i + 1}. [{title}]({x.song.url})')
            output = '\n'.join(output)
            embed.add_field(name='History', value=output)
            return [[], {'embed': embed}]


class HandleDisconnect(CommandHandler):
    pat = r'(?:dc|stop)'

    async def handle(self):
        assert self.match
        assert self.message.guild
        if vc := settings.vc_by_guild.get(self.message.guild.id):
            if vc.is_playing():
                vc.stop()
            await vc.disconnect()
