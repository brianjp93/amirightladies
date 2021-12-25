from pytube import Search, Stream, YouTube, Playlist
from amirightladies.models import Song
from typing import Optional


class Yt:
    async def get_with_search(self, q):
        qs = Search(q)
        stream: Optional[Stream] = None
        if qs.results:
            song: YouTube
            for song in qs.results:
                if stream := song.streams.filter(only_audio=True).order_by('abr').desc().first():
                    if not stream.is_live:
                        return await self.download_stream(stream, song)

    async def get_with_url(self, q):
        song = YouTube(q)
        stream = song.streams.filter(only_audio=True).order_by('abr').desc().first()
        if stream:
            return await self.download_stream(stream, song)

    async def download_stream(self, stream: Stream, source_song: YouTube):
        if song := await Song.filter(stream_id=source_song.video_id).first():
            return song
        else:
            file_path = stream.download('media')
            song = Song(
                stream_id=source_song.video_id, title=stream.title,
                url=source_song.watch_url, file=file_path
            )
            await song.save()
            return song

    async def get_queries_from_playlist(self, q: str):
        p = Playlist(q)
        return [video.watch_url for video in p.videos]
