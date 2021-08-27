import random
import re

import discord
import settings

from discord.ext import tasks
from discord.message import Message as DMessage
from discord.member import Member as DMember
from resources import amirightladies as ladies
from resources import tweet
from orm.models import Member, Guild

PREFIX = '~'
COMMANDS = {
    'link': 'link',
}
HUMBLING_PHRASES = set([
    re.compile(r'you.*best'),
    re.compile(r'you.*so.*good'),
    re.compile(r'i.*am.*the.*best'),
    re.compile(r'i.?m.*the.*best'),
    # re.compile(r'[(i.*am)|(i.?m).*a.*genius]'),
])

class Client(discord.Client):
    def __init__(self, *args, **kwargs):
        self.avatar_channel = None
        super().__init__(*args, **kwargs)
        self.set_up()

    def set_up(self):
        self.send_avatar_message.start()

    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message: DMessage):
        content = message.content.lower()
        print(f'Message from {message.author}: {message.content}')
        # create member / guild if they don't exist

        if not getattr(message.author, 'bot', None):
            Member.create_from_member(message.author)

        channel_name = str(message.channel)
        if self.user != message.author:
            if channel_name == 'am-i-right-ladies':
                await self.write_cool_message(message.channel)

            if channel_name == 'watch-avatar-lisa':
                self.avatar_channel = message.channel.id
                url = tweet.get_avatar_tweet_url()
                await message.channel.send(url)

            if message.content.startswith(PREFIX):
                await self.handle_command(message)

            await self.handle_if_humbled(message)

            if 'shit' in content:
                await message.channel.send('💩')

    async def handle_command(self, message: DMessage) -> None:
        content = message.content[1:].lower()

        if content.startswith('link'):
            await message.channel.send(settings.INVITE_LINK)

    async def handle_if_humbled(self, message: DMessage) -> None:
        content = message.content.lower()
        for pattern in HUMBLING_PHRASES:
            if pattern.search(content):
                await message.channel.send('Wow it is really humbling that you would say that.')
                break

    @tasks.loop(hours=1)
    async def send_avatar_message(self):
        if self.avatar_channel:
            channel = self.get_channel(self.avatar_channel)
            url = tweet.get_avatar_tweet_url()
            message = f'Hello Lisa, this is your hourly reminder to watch avatar.\n{url}'
            await channel.send(message) # type: ignore

    async def write_cool_message(self, channel):
        await channel.send(random.choice(ladies.MESSAGE_LIST))


client = Client()
client.run(settings.TOKEN)
