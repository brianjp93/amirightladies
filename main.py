import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os
import random
from resources import amirightladies as ladies
from resources import tweet
load_dotenv()


TOKEN = os.getenv('TOKEN')
INVITE_LINK = f'https://discord.com/oauth2/authorize?client_id={os.getenv("CLIENT_ID", "")}&scope=bot&permissions=355328'
print(INVITE_LINK)


class Client(discord.Client):
    def __init__(self, *args, **kwargs):
        self.avatar_channel = None
        super().__init__(*args, **kwargs)
        self.set_up()

    def set_up(self):
        self.send_avatar_message.start()

    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        channel_name = str(message.channel)
        if self.user != message.author:
            if channel_name == 'am-i-right-ladies':
                await self.write_cool_message(message.channel)

            if channel_name == 'watch-avatar-lisa':
                self.avatar_channel = message.channel.id
                url = tweet.get_avatar_tweet_url()
                await message.channel.send(url)

    @tasks.loop(hours=1)
    async def send_avatar_message(self):
        if self.avatar_channel:
            channel = self.get_channel(self.avatar_channel)
            url = tweet.get_avatar_tweet_url()
            message = f'Hello Lisa, this is your hourly reminder to watch avatar.\n{url}'
            await channel.send(message)


    async def write_cool_message(self, channel):
        await channel.send(random.choice(ladies.MESSAGE_LIST))


client = Client()
client.run(TOKEN)
