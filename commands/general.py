from typing import Tuple, Optional, List, Type
from abc import abstractmethod, ABC
import discord
import re


class CommandHandler(ABC):
    """Commands which are prefixed."""
    message: discord.Message
    pat: str

    def __init__(self, message: discord.Message):
        self.message = message

    @abstractmethod
    async def handle(self) -> Tuple[list, dict]:
        raise NotImplementedError

    def is_match(self) -> bool:
        return bool(re.match(self.pat, self.get_message()))

    @property
    def match(self) -> Optional[re.Match]:
        return re.match(self.pat, self.get_message())

    def get_message(self):
        return self.message.content[1:]


class GeneralHandler(ABC):
    """Commands which are not prefixed."""
    message: discord.Message
    pats: List[str]
    channel_name: Optional[str] = None

    def __init__(self, message: discord.Message):
        self.message = message

    @abstractmethod
    async def handle(self) -> Tuple[list, dict]:
        raise NotImplementedError

    def is_match(self) -> bool:
        if self.channel_name:
            if str(getattr(self.message.channel, 'name')) != self.channel_name:
                return False
        for pat in self.pats:
            if bool(re.match(pat, self.get_message())):
                return True
        return False

    @property
    def match(self) -> Optional[re.Match]:
        for pat in self.pats:
            if match := re.match(pat, self.message.content):
                return match
        return None

    def get_message(self):
        return self.message.content


all_commands: List[Type[CommandHandler]] = []
general_commands: List[Type[GeneralHandler]] = []


def prefix_command(cls: Type[CommandHandler]) -> Type[CommandHandler]:
    all_commands.append(cls)
    return cls

def general_command(cls: Type[GeneralHandler]) -> Type[GeneralHandler]:
    general_commands.append(cls)
    return cls
