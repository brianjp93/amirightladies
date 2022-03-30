from typing import Dict
from dotenv import load_dotenv
from pydantic import BaseSettings
from functools import lru_cache
import sentry_sdk
import discord

load_dotenv()

class Settings(BaseSettings):
    APP_NAME = 'Amirightladies'
    TOKEN: str
    CLIENT_ID: str = ''
    INVITE_LINK: str = f'https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&permissions=292446923888&redirect_uri=https%3A%2F%2Fdiscord.com%2Fapi%2Fwebhooks%2F880631007366225981%2Fib2gYaWlfdphCFst0bEwNxTJBx15RheQajxhZ9II5uVKenIaeRYeAb9oJGx4ddMb5fG9&response_type=code&scope=messages.read%20guilds.join%20guilds.members.read%20bot%20identify'

    CLIENT_SECRET: str
    PUBLIC_KEY: str

    TWITTER_API_KEY: str
    TWITTER_API_SECRET: str
    TWITTER_API_TOKEN: str
    TWITTER_ACCESS_TOKEN: str
    TWITTER_ACCESS_SECRET: str
    SENTRY_URI: str
    RAPIDAPI_HOST: str
    RAPIDAPI_KEY: str
    OPEN_WEATHER_KEY: str
    SPOTIFY_ID: str
    SPOTIFY_SECRET: str
    BULLET: str = '•'
    DICTIONARYURL = 'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
    vc_by_guild: Dict[int, discord.VoiceClient] = {}

    class Config:
        case_sensitive: bool = True


@lru_cache()
def get_settings():
    return Settings()


# https://github.com/RDIL/bluejay/blob/master/discord-sentry-reporting/discord_sentry_reporting/__init__.py
def use_sentry(client, **sentry_args):
    """
    Use this compatibility library as a bridge between Discord and Sentry.
    Arguments:
        client: The Discord client object (e.g. `discord.AutoShardedClient`).
        sentry_args: Keyword arguments to pass to the Sentry SDK.
    """
    sentry_sdk.init(**sentry_args)

    @client.event
    async def on_error(event, *args, **kwargs):
        """Don't ignore the error, causing Sentry to capture it."""
        raise

