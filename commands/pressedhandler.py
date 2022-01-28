from .general import GeneralHandler, general_command


@general_command
class HandlePressed(GeneralHandler):
    pats = [
        r'.*i.*m.*so.*mad.*',
        r'.*irritating.*',
        r'.*is.*a.*joke.*',
        r'.*shut.*up.*',
    ]
    case_insensitive = True

    async def handle(self):
        return (['bruh I am just so pressed rn.'], {})
