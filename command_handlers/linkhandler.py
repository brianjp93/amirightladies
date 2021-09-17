from .general import CommandHandler
import settings

class HandleLink(CommandHandler):
    pat = r'link'

    async def handle(self):
        assert self.match
        return ([settings.INVITE_LINK], {})
