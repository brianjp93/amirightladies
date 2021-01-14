import discord
from dotenv import load_dotenv
import os
import random
from resources import amirightladies as ladies
load_dotenv()


TOKEN = os.getenv('TOKEN')
INVITE_LINK = f'https://discord.com/oauth2/authorize?client_id={os.getenv("CLIENT_ID", "")}&scope=bot&permissions=355328'
print(INVITE_LINK)


class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if str(message.channel) == 'am-i-right-ladies':
            if self.user != message.author:
                await self.write_cool_message(message.channel)

    async def write_cool_message(self, channel):
        await channel.send(random.choice(ladies.MESSAGE_LIST))


client = Client()
client.run(TOKEN)
