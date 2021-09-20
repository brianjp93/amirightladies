import settings
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
from itertools import count

auth = SpotifyClientCredentials(client_id=settings.SPOTIFY_ID, client_secret=settings.SPOTIFY_SECRET)
api = spotipy.Spotify(auth_manager=auth)


def get_playlist_tracks(q: str, full=False):
    """Only retrieves first page of playlist.
    """
    playlist_id = None
    if match := re.search(r'playlist/([\w\d]+)', q):
        playlist_id = match.groups()[0]
    elif match := re.match(r'[\w\d]+', q):
        playlist_id = q

    tracks = []
    limit = 100
    if playlist_id:
        for i in count():
            if r := api.playlist_tracks(playlist_id, offset=i*limit):
                items = r.get('items')
                if not items:
                    break
                output = [item['track'] for item in items]
                tracks.extend(output)
                if not full:
                    break
                if not r['next']:
                    break
    return tracks


def get_track(q: str):
    track_id = None
    if match := re.search(r'track/([\w\d]+)', q):
        track_id = match.groups()[0]
    elif match := re.match(r'[\w\d]+', q):
        track_id = q

    if track_id:
        r = api.track(track_id)
        return r
