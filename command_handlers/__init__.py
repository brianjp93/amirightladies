from .linkhandler import HandleLink
from .musichandler import (
    HandlePlay, HandleSkip, HandleQueue,
    HandleHistory, HandleDisconnect, HandleEmptyPlay,
)
from .dictionaryhandler import HandleUrban, HandleDefine
from .weatherhandler import HandleWeatherZip, HandleWeatherCityState

all_commands = [
    HandleLink,
    HandlePlay,
    HandleSkip,
    HandleQueue,
    HandleHistory,
    HandleDisconnect,
    HandleEmptyPlay,
    HandleUrban,
    HandleDefine,
    HandleWeatherCityState,
    HandleWeatherZip,
]
__version__ = '1.0'
