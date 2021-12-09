from .general import CommandHandler, prefix_command
import discord
import re
import settings
from sqlmodel import select

from asyncio import sleep
from datetime import datetime
from typing import Optional
from orm.models import Song, Guild, HistorySong, DeferSong
from app import session
from resources.yt import Yt
import traceback
from resources import spotify

yt = Yt()


async def play_songs(vc: discord.VoiceClient, message: discord.Message):
    if guild := Guild.get_from_discord_guild(message.guild):
        session.refresh(guild)
        if vc.is_paused():
            await message.channel.send('Resuming.')
            vc.resume()
            return
        while guild.defersongs:
            defersong = guild.defersongs[0]
            song = Optional[Song]
            if not defersong.song:
                if song := await import_from_query(defersong.query):
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
                    while vc.is_playing() or vc.is_paused():
                        await sleep(.5)
                    session.refresh(guild)
                    try:
                        guild.defersongs.remove(defersong)
                        session.commit()
                    except ValueError:
                        print('could not remove song.')
                else:
                    await message.channel.send(f'Could not find a song for the query: {defersong.query}.')
                    guild.defersongs.remove(defersong)
                    session.commit()


@prefix_command
class HandleEmptyPlay(CommandHandler):
    pat = r'^play$'

    async def handle(self):
        assert self.match
        assert self.message.guild
        assert isinstance(self.message.author, discord.Member)
        if guild := Guild.get_from_discord_guild(self.message.guild):
            songs = session.exec(
                select(DeferSong).where(DeferSong.guild == guild)
            ).fetchmany(10)
            if songs:
                try:
                    assert self.message.author.voice is not None
                    vc = await self.message.author.voice.channel.connect()
                    settings.vc_by_guild[self.message.guild.id] = vc
                    if vc.is_paused() or not vc.is_playing():
                        await play_songs(vc, self.message)
                except discord.ClientException as e:
                    print(e)
                    vc = settings.vc_by_guild.get(self.message.guild.id)
                    if vc:
                        if vc.is_paused() or not vc.is_playing():
                            await play_songs(vc, self.message)
            else:
                return (['The queue is empty.'], {})


@prefix_command
class HandlePlay(CommandHandler):
    pat = r'play (.*)'
    vars = ['query']

    async def handle(self):
        if query := self.groups.get('query', None):
            assert self.message.guild
            try:
                voice_channel = self.message.author.voice.channel
            except:
                voice_channel = None
                await self.message.channel.send("Couldn't find voice channel.")
            if isinstance(voice_channel, discord.VoiceChannel):
                if guild := Guild.get_from_discord_guild(self.message.guild):
                    session.refresh(guild)
                    tracks = None
                    if re.match(r'(.*)?spotify(.*)?playlist/([\w\d]+)(.*)?', query):
                        tracks = spotify.get_playlist_tracks(query, full=True)
                    elif match := re.match(r'(?:.*)?spotify(?:.*)?album/([\w\d]+)(?:.*)?', query):
                        tracks = spotify.api.album_tracks(match.groups()[0])['items']
                    if tracks:
                        tracks = list(tracks)
                        await self.message.channel.send(f'Adding {len(tracks)} songs to the queue.')
                        for track in tracks:
                            name = track['name']
                            artist = []
                            for a in track['artists']:
                                artist.append(a['name'])
                            artist = ', '.join(artist)
                            df = DeferSong(
                                query=f'{name} {artist}',
                                guild=guild,
                                created_at=int(datetime.now().timestamp()),
                            )
                            session.add(df)
                    elif re.match(r'(.*)youtube.com/playlist?(.*)', query):
                        queries = await yt.get_queries_from_playlist(query)
                        for q in queries:
                            df = DeferSong(query=q, guild=guild, created_at=int(datetime.now().timestamp()))
                            session.add(df)
                        await self.message.channel.send(f'Adding {len(queries)} songs to queue.')
                    else:
                        df = DeferSong(query=query, guild=guild, created_at=int(datetime.now().timestamp()))
                        session.add(df)
                        await self.message.channel.send(f'Added 1 song to queue.')
                    session.commit()
                    vc = None
                    try:
                        vc = await voice_channel.connect()
                        settings.vc_by_guild[self.message.guild.id] = vc
                    except discord.ClientException as e:
                        traceback.print_exc()
                        vc = settings.vc_by_guild.get(self.message.guild.id)
                    if vc:
                        if not vc.is_connected():
                            await vc.voice_connect()
                        if not vc.is_playing():
                            await play_songs(vc, self.message)
            return [[], {}]


@prefix_command
class HandleSkip(CommandHandler):
    pat = r'^(?:(?:skip)|(?:next))\s?(\d+)?$'
    vars = ['count']

    async def handle(self):
        assert self.message.guild
        count = int(self.groups.get('count', 1))
        if vc := settings.vc_by_guild.get(self.message.guild.id):
            vc.stop()
            if guild := Guild.get_from_discord_guild(self.message.guild):
                session.refresh(guild)
                if guild.defersongs:
                    await self.message.channel.send(f'Skipping {count} {"songs" if count > 1 else "song"}.')
                    removesongs = [song for song in guild.defersongs[:count]]
                    for song in removesongs:
                        guild.defersongs.remove(song)
                    session.commit()
                    session.refresh(guild)
                    if guild.defersongs:
                        await play_songs(vc, self.message)
                    else:
                        await self.message.channel.send('No more songs.')


@prefix_command
class HandleQueue(CommandHandler):
    pat = r'^queue$'

    async def handle(self):
        assert self.match
        assert self.message.guild
        if guild := Guild.get_from_discord_guild(self.message.guild):
            if songs := session.exec(
                select(DeferSong).where(DeferSong.guild == guild)
            ).fetchmany(10):
                embed = discord.Embed()
                output = []
                for i, x in enumerate(songs):
                    title = x.query[:30]
                    if len(x.query) > 30:
                        title += '...'
                    output.append(f'{i + 1}. [{title}]')
                output = '\n'.join(output)
                embed.add_field(name='Queue', value=output)
                return [[], {'embed': embed}]
            else:
                return (['No songs in queue.'], {})


@prefix_command
class HandleHistory(CommandHandler):
    pat = r'^history$'

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


@prefix_command
class HandlePause(CommandHandler):
    pat = r'^pause$'

    async def handle(self):
        assert self.match
        if vc := settings.vc_by_guild.get(self.message.guild.id):
            if vc.is_playing():
                vc.pause()
                return (['Pausing.'], {})
            else:
                return (['Nothing currently playing.'], {})
        else:
            return (['Could not find voice channel connection.'], {})

@prefix_command
class HandleDisconnect(CommandHandler):
    pat = r'(?:dc|stop)'

    async def handle(self):
        assert self.match
        assert self.message.guild
        if vc := settings.vc_by_guild.get(self.message.guild.id):
            if vc.is_playing():
                vc.stop()
            await vc.disconnect()


@prefix_command
class HandleClear(CommandHandler):
    pat = r'^clear$'

    async def handle(self):
        assert self.match
        assert self.message.guild
        if guild := Guild.get_from_discord_guild(self.message.guild):
            guild.defersongs = []
            session.commit()
            return (['Clearing queue.'], {})


async def import_from_query(q: str):
    """Import song from a query or url.
    """
    song = None
    if re.match(r'(.*)?youtube.com(.*)?', q):
        song = await yt.get_with_url(q)
    elif re.match(r'(.*)?youtu\.be(.*)?', q):
        song = await yt.get_with_url(q)
    elif re.match(r'(.*)?spotify(.*)?playlist/([\w\d]+)(.*)?', q):
        pass
        # spotify.add_playlist_to_queue(content)
    elif re.match(r'(.*)?spotify(.*)?track/([\w\d]+)(.*)?', q):
        r = spotify.get_track(q)
        if r:
            name = r['name']
            artist = []
            for a in r['artists']:
                artist.append(a['name'])
            artist = ', '.join(artist)
            query = f'{name} {artist}'
            return await import_from_query(query)
    else:
        song = await yt.get_with_search(q)
    return song
