from .general import CommandHandler
from aiohttp import ClientSession
from discord import Embed
import settings


class HandleDefine(CommandHandler):
    pat = r'def(?:ine)? (.*)'

    async def handle(self):
        assert self.match
        word = self.match.groups()[0].strip()
        print(f'Trying to define word: {word}')
        async with ClientSession() as client_session:
            async with client_session.get(settings.DICTIONARYURL.format(**{'word': word})) as response:
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
                            out = [f'{settings.BULLET} {x["definition"]}']
                            if example := x.get('example'):
                                out.append(f'\t{settings.BULLET} {settings.BULLET} **Example**: *{example}*')
                            definitions.append('\n'.join(out))

                        embed.add_field(name=pos['partOfSpeech'], value='\n\n'.join(definitions))
                return [[], {'embed': embed}]


class HandleUrban(CommandHandler):
    pat = r'urban (.*)'

    async def handle(self):
        assert self.match
        word = self.match.groups()[0].strip()
        print(f'Trying to define word: {word}')
        url = 'https://mashape-community-urban-dictionary.p.rapidapi.com/define'
        headers = {
            'x-rapidapi-host': settings.RAPIDAPI_HOST,
            'x-rapidapi-key': settings.RAPIDAPI_KEY,
        }
        async with ClientSession() as client_session:
            async with client_session.get(url=url, params={'term': word}, headers=headers) as response:
                print(response)
                data = await response.json()
                print(data)
                embed = Embed()
                embed.title = f'Urban Dictionary: __{word}__'
                definitions = []
                if len(data['list']) == 0:
                    return [[f'Could not find a definition for {word} on urban dictionary.'], {}]
                data['list'].sort(key=lambda x: -x['thumbs_up'])
                for item in data['list'][:3]:
                    defi = item['definition']
                    defi = defi.replace('[', '').replace(']', '')
                    if len(defi) > 100:
                        defi = defi[:100] + '...'
                    out = [f'{settings.BULLET} {defi}']
                    if example := item['example']:
                        example = example.replace('[', '').replace(']', '')
                        if len(example) > 100:
                            example = f'{example[:100]}...'
                        out.append(f'{settings.BULLET} {settings.BULLET} Example: *{example}*')
                    definitions.append('\n'.join(out))
                embed.add_field(name='Definitions', value='\n\n'.join(definitions), inline=False)
                embed.url = f'https://www.urbandictionary.com/define.php?term={word}'
                return [[], {'embed': embed}]
