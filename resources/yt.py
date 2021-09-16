from pytube import Search, Stream
from orm.models import Song
from sqlmodel import select
from typing import Optional
from app import session

class Yt:
    @staticmethod
    def get_stream_id(stream: Stream):
        return f'{stream.title}-{stream.filesize}'

    def get_with_search(self, q) -> Optional[Song]:
        qs = Search(q)
        stream: Optional[Stream] = None
        if qs.results:
            song = qs.results[0]
            stream = song.streams.filter(only_audio=True).order_by('abr').desc().first()

        if stream:
            stream_id = self.get_stream_id(stream)
            song = session.exec(
                select(Song).where(Song.stream_id==stream_id)
            ).first()
            if song:
                return song
            else:
                file_path = stream.download('media')
                song = Song(
                    stream_id=stream_id, title=stream.title,
                    url=stream.url, file=file_path
                )
                session.add(song)
                session.commit()
                return song
