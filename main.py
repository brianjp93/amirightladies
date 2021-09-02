from datetime import datetime
import pytz
import random
import re
import settings
from typing import Union
from aiohttp import ClientSession

import discord
from discord.ext import tasks
from discord.message import Message as DMessage
from discord.member import Member as DMember
from discord.channel import TextChannel, DMChannel, GroupChannel
from discord.embeds import Embed
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
BULLET = '•'
weather = Weather(settings.OPEN_WEATHER_KEY)

DICTIONARYURL = 'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'

class Client(discord.Client):
    def __init__(self, *args, **kwargs):
        self.avatar_channel = None
        super().__init__(*args, **kwargs)
        self.set_up()

        # commands which start with PREFIX only
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
            'define': [
                re.compile(r'def(?:ine)? (.*)'),
                self.handle_define
            ],
        }

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
                if send_message[0] or send_message[1]:
                    await message.channel.send(*send_message[0], **send_message[1])

    async def handle_shit(self, *args):
        return [['💩'], {}]

    async def handle_command(self, message: DMessage) -> None:
        content = message.content[1:].lower().strip()

        for key, (pat, handler) in self.COMMANDS.items():
            if match := pat.match(content):
                print(match)
                send_message = await handler(message, match)
                if send_message[0] or send_message[1]:
                    await message.channel.send(*send_message[0], **send_message[1])

    async def handle_link(self, *args) -> list:
        return [[settings.INVITE_LINK], {}]

    async def handle_define(self, message: DMessage, match: re.Match):
        word = match.groups()[0].strip()
        print(f'Trying to define word: {word}')
        async with ClientSession() as session:
            async with session.get(DICTIONARYURL.format(**{'word': word})) as response:
                print(response)
                if response.status == 404:
                    return [[f'Couldn\'t find a definition for {word}'], {}]
                data = await response.json()
                embed = Embed()
                embed.title = f'Definitions for: {word}'
                embed.description = f''
                for result in data:
                    origin = 'Origin: ' + result.get('origin', '?NA?')
                    embed.add_field(name=f"__{result['word']}__", value=f'{origin}', inline=False)
                    for pos in result['meanings']:
                        definitions = []
                        for x in pos['definitions']:
                            out = [f'{BULLET} {x["definition"]}']
                            if example := x.get('example'):
                                out.append(f'\t{BULLET} {BULLET} **Example**: *{example}*')
                            definitions.append('\n'.join(out))

                        embed.add_field(name=pos['partOfSpeech'], value='\n\n'.join(definitions))
                return [[], {'embed': embed}]


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
        if json['cod'] == '404':
            return [['That city could not be found.'], {}]
        return self.verbose_weather_response(json)

    async def handle_weather_zip(self, message: DMessage, match: re.Match):
        print(match.groups())
        zip = match.groups()[0]
        data = await weather.get_current_weather(zip=zip)
        json = data['json']
        if json['cod'] == '404':
            return [['That city could not be found.'], {}]
        return self.verbose_weather_response(json)

    def short_weather_response(self, data: dict) -> str:
        name = data["name"]
        country = data["sys"]["country"]
        temp = weather.to_f(data['main']['temp'])
        weather_desc = data['weather'][0]['description']
        return f'{name}, {country} - {temp}F {weather_desc}'

    def verbose_weather_response(self, data: dict) -> list:
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        map_url = f'https://www.google.com/maps/@{lat},{lon},15.00z'
        city = data['name']
        country = data['sys']['country']
        temp = weather.to_f(data['main']['temp'])
        temp_min = weather.to_f(data['main']['temp_min'])
        temp_max = weather.to_f(data['main']['temp_max'])
        # weather_main = data['weather'][0]['main']
        weather_desc = data['weather'][0]['description']
        feels_like = weather.to_f(data['main']['feels_like'])
        pressure = data['main']['pressure']
        humidity = data['main']['humidity']
        visibility = float(data['visibility']) / 1000
        tz_offset = int(data['timezone'])
        sunrise = datetime.fromtimestamp(
            int(data['sys']['sunrise']) + tz_offset,
            tz=pytz.UTC
        ).strftime('%-I:%M %p')
        sunset = datetime.fromtimestamp(
            int(data['sys']['sunset']) + tz_offset,
            tz=pytz.UTC
        ).strftime('%-I:%M %p')
        embed = Embed()
        embed.add_field(
            name='Temperature',
            value=f'{temp}F\n{temp_max} hi / {temp_min} lo\nFeels like: {feels_like}F',
        )
        embed.add_field(
            name='Other',
            value=f'Humidity: {humidity}%\nPressure: {pressure}hPa\nVisibility: {visibility:.1f}km'
        )
        embed.add_field(
            name='Sunrise / Sunset',
            value=f'{sunrise} / {sunset}',
        )
        embed.description = f'{weather_desc}\n[google maps]({map_url})'
        embed.title = f'{city}, {country} - {temp}F'
        embed.set_author(
            name='OpenWeather',
            url=f'https://openweathermap.org/find?q={city.replace(" ", "%20")},{country}'
        )
        return [[], {'embed': embed}]

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
