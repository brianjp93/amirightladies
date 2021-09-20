from .general import GeneralHandler, general_command
from resources import amirightladies as ladies
import random


@general_command
class HandleLadies(GeneralHandler):
    pats = ['.*']
    channel_name = 'am-i-right-ladies'

    async def handle(self):
        return ([random.choice(ladies.MESSAGE_LIST)], {})
