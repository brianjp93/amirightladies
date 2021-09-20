from .general import GeneralHandler, general_command


@general_command
class HandleShit(GeneralHandler):
    pats = [
        r'(.*)?(\W|^)shit(\W|$)(.*)?',
    ]

    async def handle(self):
        return (['💩'], {})

    def get_message(self):
        return super().get_message().lower()
