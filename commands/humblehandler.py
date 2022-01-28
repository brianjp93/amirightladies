from .general import GeneralHandler, general_command


@general_command
class HandleHumble(GeneralHandler):
    pats = [
        r'.*you.*best.*',
        r'.*you.*so.*good.*',
        r'.*i.*am.*the.*best.*',
        r'.*i.?m.*the.*best.*',
        r'.*[(i.*am)|(i.?m)].*a.*genius.*',
    ]
    case_insensitive = True

    async def handle(self):
        return (['Wow it is really humbling that you would say that.'], {})
