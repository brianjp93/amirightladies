import discord
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
    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        channel_name = str(message.channel)
        if self.user != message.author:
            if channel_name == 'am-i-right-ladies':
                await self.write_cool_message(message.channel)

            if channel_name == 'watch-avatar-lisa':
                url = tweet.get_avatar_tweet_url()
                await message.channel.send(url)


    async def write_cool_message(self, channel):
        await channel.send(random.choice(ladies.MESSAGE_LIST))


client = Client()
client.run(TOKEN)
