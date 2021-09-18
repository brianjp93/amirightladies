from .general import CommandHandler, prefix_command
import settings


@prefix_command
class HandleLink(CommandHandler):
    pat = r'link'

    async def handle(self):
        assert self.match
        return ([settings.INVITE_LINK], {})
