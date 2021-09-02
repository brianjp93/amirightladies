from dotenv import load_dotenv
import os
import sentry_sdk


load_dotenv()

TOKEN: str = os.environ['TOKEN']
CLIENT_ID: str = os.environ['CLIENT_ID']
INVITE_LINK: str = f'https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&permissions=157307235904&redirect_uri=https%3A%2F%2Fdiscord.com%2Fapi%2Fwebhooks%2F880631007366225981%2Fib2gYaWlfdphCFst0bEwNxTJBx15RheQajxhZ9II5uVKenIaeRYeAb9oJGx4ddMb5fG9&scope=bot'

CLIENT_SECRET: str = os.environ['CLIENT_SECRET']
PUBLIC_KEY: str = os.environ['PUBLIC_KEY']

TWITTER_API_KEY: str = os.environ['TWITTER_API_KEY']
TWITTER_API_SECRET: str  = os.environ['TWITTER_API_SECRET']
TWITTER_API_TOKEN: str = os.environ['TWITTER_API_TOKEN']
TWITTER_ACCESS_TOKEN: str = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_SECRET: str = os.environ['TWITTER_ACCESS_SECRET']

SENTRY_URI: str = os.environ['SENTRY_URI']

RAPIDAPI_HOST: str = os.environ['RAPIDAPI_HOST']
RAPIDAPI_KEY: str = os.environ['RAPIDAPI_KEY']

OPEN_WEATHER_KEY: str = os.environ['OPEN_WEATHER_KEY']

DB_URL: str = os.environ['DB_URL']

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

