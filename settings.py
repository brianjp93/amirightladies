from dotenv import load_dotenv
import os
load_dotenv()

TOKEN: str = os.environ['TOKEN']
CLIENT_ID: str = os.environ['CLIENT_ID']
INVITE_LINK: str = f'https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&scope=bot&permissions=355328'

CLIENT_SECRET: str = os.environ['CLIENT_SECRET']
PUBLIC_KEY: str = os.environ['PUBLIC_KEY']

TWITTER_API_KEY: str = os.environ['TWITTER_API_KEY']
TWITTER_API_SECRET: str  = os.environ['TWITTER_API_SECRET']
TWITTER_API_TOKEN: str = os.environ['TWITTER_API_TOKEN']
TWITTER_ACCESS_TOKEN: str = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_SECRET: str = os.environ['TWITTER_ACCESS_SECRET']

DB_URL: str = os.environ['DB_URL']
