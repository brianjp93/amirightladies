import random
import re
import settings
from typing import Union
from typing import Dict

import discord
from discord.ext import tasks
from discord.message import Message as DMessage
from discord.channel import TextChannel, DMChannel, GroupChannel
from resources import amirightladies as ladies
from resources import tweet
from resources import spotify
from orm.models import Member
import command_handlers as ch
import app


PREFIX = '.'
HUMBLING_PHRASES = set([
    re.compile(r'you.*best'),
    re.compile(r'you.*so.*good'),
    re.compile(r'i.*am.*the.*best'),
    re.compile(r'i.?m.*the.*best'),
    re.compile(r'[(i.*am)|(i.?m)].*a.*genius'),
])


class Client(discord.Client):
    def __init__(self, *args, **kwargs):
        self.avatar_channel = None
        super().__init__(*args, **kwargs)
        self.set_up()
        self.vc_by_guild: Dict[int, discord.VoiceClient] = {}

        # general message parsing
        self.GENERALCOMMANDS = {
            'shit': [
                re.compile(r'(.*)?(\W|^)shit(\W|$)(.*)?'),
                self.handle_shit
            ],
        }

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

            if content.startswith(PREFIX):
                await self.handle_command(message)

            await self.handle_general_mesage(message)
            await self.handle_if_humbled(message)

    async def handle_general_mesage(self, message):
        content = message.content.lower().strip()
        for key, (pat, handler) in self.GENERALCOMMANDS.items():
            if match := pat.match(content):
                print(match)
                send_message = await handler(message, match)
                if send_message and (send_message[0] or send_message[1]):
                    await message.channel.send(*send_message[0], **send_message[1])

    async def handle_shit(self, *args):
        return [['💩'], {}]

    async def handle_command(self, message: DMessage) -> None:
        for handler in ch.all_commands:
            h = handler(message)
            if h.is_match():
                send_message = await h.handle()
                if send_message and (send_message[0] or send_message[1]):
                    await message.channel.send(*send_message[0], **send_message[1])

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

    async def write_cool_message(
        self,
        channel: Union[TextChannel, DMChannel, GroupChannel]
    ) -> None:
        await channel.send(random.choice(ladies.MESSAGE_LIST))


if __name__ == '__main__':
    app.build_all()
    client = Client()
    settings.use_sentry(
        client,
        dsn=settings.SENTRY_URI,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0
    )
    client.run(settings.TOKEN)
