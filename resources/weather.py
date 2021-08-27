import aiohttp
from typing import Union


URL = 'https://api.openweathermap.org/data'


class Weather:

    def __init__(self, key: str):
        self.key = key

    def to_f(self, kelvin: Union[int, float, str]):
        kelvin = float(kelvin)
        return round((kelvin - 273.15) * 9/5 + 32, 2)

    async def get_current_weather(
        self,
        city: str=None,
        state: str=None,
        zip: str=None,
        version: str='2.5',
    ):
        url = f'{URL}/{version}/weather'
        params = { 'appid': self.key }
        if city:
            q = [city]
            if state:
                q.append(state)
            params['q'] = ','.join(q)
        elif zip:
            params['zip'] = zip

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return {
                    'response': response,
                    'json': await response.json(),
                }
