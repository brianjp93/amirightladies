from typing import Tuple, Optional, List, Type, Dict
from functools import cached_property
from abc import abstractmethod, ABC
import discord
import re


class CommandHandler(ABC):
    """Commands which are prefixed."""
    message: discord.Message
    pat: str
    vars: List[str] = []

    def __init__(self, message: discord.Message):
        self.message = message

    @abstractmethod
    async def handle(self) -> Tuple[list, dict]:
        raise NotImplementedError

    def is_match(self) -> bool:
        return bool(re.match(self.pat, self.get_message()))

    @cached_property
    def match(self) -> Optional[re.Match]:
        return re.match(self.pat, self.get_message())

    def get_message(self):
        return self.message.content[1:]

    @cached_property
    def groups(self) -> Dict[str, str]:
        assert self.match
        vars = {}
        groups = self.match.groups()
        for i, name in enumerate(self.vars):
            try:
                vars[name] = groups[i]
            except IndexError:
                pass
        return vars


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

    @cached_property
    def match(self) -> Optional[re.Match]:
        for pat in self.pats:
            if match := re.match(pat, self.get_message()):
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
