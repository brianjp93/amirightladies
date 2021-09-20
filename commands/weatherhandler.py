from .general import CommandHandler, prefix_command
from datetime import datetime
from resources.weather import Weather
from discord import Embed
import pytz
import settings


weather = Weather(settings.OPEN_WEATHER_KEY)


@prefix_command
class HandleWeatherCityState(CommandHandler):
    pat = r'weather ([A-z\s]+),?\s?([A-z]+)?'
    vars = ['city', 'state']

    async def handle(self):
        assert self.match
        data = await weather.get_current_weather(city=self.groups['city'], state=self.groups['state'])
        json = data['json']
        if json['cod'] == '404':
            return [['That city could not be found.'], {}]
        return verbose_weather_response(json)


@prefix_command
class HandleWeatherZip(CommandHandler):
    pat = r'weather (\d{5})'
    vars = ['zipcode']

    async def handle(self):
        zip = self.groups['zipcode']
        data = await weather.get_current_weather(zip=zip)
        json = data['json']
        if json['cod'] == '404':
            return [['That city could not be found.'], {}]
        return verbose_weather_response(json)

def verbose_weather_response(data: dict):
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


def short_weather_response(data: dict) -> str:
    name = data["name"]
    country = data["sys"]["country"]
    temp = weather.to_f(data['main']['temp'])
    weather_desc = data['weather'][0]['description']
    return f'{name}, {country} - {temp}F {weather_desc}'
