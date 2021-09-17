from .linkhandler import HandleLink
from .musichandler import HandlePlay, HandleSkip, HandleQueue, HandleHistory
from .dictionaryhandler import HandleUrban, HandleDefine
from .weatherhandler import HandleWeatherZip, HandleWeatherCityState

all_commands = [
    HandleLink,
    HandlePlay,
    HandleSkip,
    HandleQueue,
    HandleHistory,
    HandleUrban,
    HandleDefine,
    HandleWeatherCityState,
    HandleWeatherZip,
]
__version__ = '1.0'
