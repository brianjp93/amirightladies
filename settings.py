from dotenv import load_dotenv
import os
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

OPEN_WEATHER_KEY: str = os.environ['OPEN_WEATHER_KEY']

DB_URL: str = os.environ['DB_URL']
