import settings
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

auth = SpotifyClientCredentials(client_id=settings.SPOTIFY_ID, client_secret=settings.SPOTIFY_SECRET)
api = spotipy.Spotify(auth_manager=auth)

def get_playlist_tracks(q: str):
    """Only retrieves first page of playlist.
    """
    playlist_id = None
    if match := re.search(r'playlist/([\w\d]+)', q):
        playlist_id = match.groups()[0]
    elif match := re.match(r'[\w\d]+', q):
        playlist_id = q

    if playlist_id:
        r = api.playlist(playlist_id)
        if r:
            return (item['track'] for item in r['tracks']['items'])
