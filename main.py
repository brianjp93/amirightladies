import discord
from dotenv import load_dotenv
import os
import random
load_dotenv()


TOKEN = os.getenv('TOKEN')
INVITE_LINK = f'https://discord.com/oauth2/authorize?client_id={os.getenv("CLIENT_ID", "")}&scope=bot&permissions=355328'
print(INVITE_LINK)
MESSAGE_LIST = [
    'AM I RIGHT LADIES?',
    '✩  🎀  𝒶𝓂 𝐼 𝓇𝒾𝑔𝒽𝓉 𝓁𝒶𝒹𝒾𝑒𝓈¿  🎀  ✩',
    '🐔  🎀  𝒶𝓂 𝐼 𝓇𝒾𝑔𝒽𝓉 𝓁𝒶𝒹𝒾𝑒𝓈¿  🎀  🐔',
    '¸,ø¤º°`°º¤ø,¸¸,ø¤º°   🎀  𝒶𝓂 𝐼 𝓇𝒾𝑔𝒽𝓉 𝓁𝒶𝒹𝒾𝑒𝓈?  🎀   °º¤ø,¸¸,ø¤º°`°º¤ø,¸',
    'AM I?',
    '꧁༺ 𝓪𝓶 𝓲 𝓻𝓲𝓰𝓱𝓽 𝓵𝓪𝓭𝓲𝓮𝓼? ༻꧂',
    '▞▞▞▞▞▖🅰🅼 🅸 🆁🅸🅶🅷🆃 🅻🅰🅳🅸🅴🆂?▝▞▞▞▞▞',
    '(¯`’•.¸❤♫♪♥(◠‿◠)♥♫♪❤¸.•’´¯)am i right ladies?(¯`’•.¸❤♫♪♥(◠‿◠)♥♫♪❤¸.•’´¯)',
    '(🌘‿🌘) am i right ladies? (🌘‿🌘)',
    '(◉‿◉) am i right ladies? (◉‿◉)',
]

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if str(message.channel) == 'am-i-right-ladies':
            if self.user != message.author:
                await self.write_cool_message(message.channel)

    async def write_cool_message(self, channel):
        await channel.send(random.choice(MESSAGE_LIST))


client = Client()
client.run(TOKEN)
