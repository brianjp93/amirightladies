from .general import CommandHandler, prefix_command
from config.settings import get_settings
settings = get_settings()

@prefix_command
class HandleLink(CommandHandler):
    pat = r'link'

    async def handle(self):
        assert self.match
        return ([settings.INVITE_LINK], {})
