from datetime import datetime
import random
import re

import discord
import settings

from discord.ext import tasks
from discord.message import Message as DMessage
from discord.member import Member as DMember
from discord.channel import TextChannel
from resources import amirightladies as ladies
from resources import tweet
from resources.weather import Weather
from orm.models import Member, Guild
import app

PREFIX = '~'
COMMANDS = {
    'link': 'link',
}
HUMBLING_PHRASES = set([
    re.compile(r'you.*best'),
    re.compile(r'you.*so.*good'),
    re.compile(r'i.*am.*the.*best'),
    re.compile(r'i.?m.*the.*best'),
    re.compile(r'[(i.*am)|(i.?m)].*a.*genius'),
])
weather = Weather(settings.OPEN_WEATHER_KEY)

class Client(discord.Client):
    def __init__(self, *args, **kwargs):
        self.avatar_channel = None
        super().__init__(*args, **kwargs)
        self.set_up()
        self.COMMANDS = {
            'link': [
                re.compile(r'link'),
                self.handle_link
            ],
            'weather (city/state)': [
                re.compile(r'weather ([A-z\s]+),?\s?([A-z]+)?'),
                self.handle_weather_city_state
            ],
            'weather (zip)': [
                re.compile(r'weather (\d{5})'),
                self.handle_weather_zip
            ],
            'shit': [
                re.compile(r'(\W|^)shit(\W|$)'),
                self.handle_shit
            ]
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

            if message.content.startswith(PREFIX):
                await self.handle_command(message)

            await self.handle_if_humbled(message)

    def handle_shit(self, message: DMessage, match: re.Match):
        return '💩'

    async def handle_command(self, message: DMessage) -> None:
        content = message.content[1:].lower().strip()

        for key, (pat, handler) in self.COMMANDS.items():
            if match := pat.match(content):
                print(match)
                send_message = await handler(message, match)
                if send_message:
                    await message.channel.send(send_message)

    async def handle_link(self, *args):
        return settings.INVITE_LINK

    async def handle_weather_city_state(self, message: DMessage, match: re.Match):
        group = match.groups()
        print(group)
        city = state = None
        if len(group) == 1:
            city = group[0]
        elif len(group) == 2:
            city, state = group
        data = await weather.get_current_weather(city=city, state=state)
        json = data['json']
        return self.verbose_weather_response(json)

    async def handle_weather_zip(self, message: DMessage, match: re.Match):
        print(match.groups())
        zip = match.groups()[0]
        data = await weather.get_current_weather(zip=zip)
        json = data['json']
        return self.verbose_weather_response(json)

    def short_weather_response(self, data: dict) -> str:
        name = data["name"]
        country = data["sys"]["country"]
        temp = weather.to_f(data['main']['temp'])
        weather_desc = data['weather'][0]['description']
        return f'{name}, {country} - {temp}F {weather_desc}'

    def verbose_weather_response(self, data: dict) -> str:
        temp = weather.to_f(data['main']['temp'])
        temp_min = weather.to_f(data['main']['temp_min'])
        temp_max = weather.to_f(data['main']['temp_max'])
        weather_main = data['weather'][0]['main']
        weather_desc = data['weather'][0]['description']
        feels_like = weather.to_f(data['main']['feels_like'])
        pressure = data['main']['pressure']
        humidity = data['main']['humidity']
        visibility = data['visibility']
        sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%I:%M %p')
        sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%I:%M %p')
        lines = [
            '```',
            f'{data["name"]}, {data["sys"]["country"]}',
            f'{temp}F --- {temp_min}/{temp_max}F',
            f'{weather_main}, {weather_desc}',
            f'Feels Like: {feels_like}',
            f'Humidity: {humidity}',
            f'Pressure: {pressure}',
            f'Visibility: {visibility}',
            f'Sunrise/Sunset: {sunrise} / {sunset}',
            '```',
        ]
        return '\n'.join(lines)

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

    async def write_cool_message(self, channel: TextChannel) -> None:
        await channel.send(random.choice(ladies.MESSAGE_LIST))


if __name__ == '__main__':
    app.build_all()
    client = Client()
    client.run(settings.TOKEN)
