from typing import Tuple, Optional
from abc import abstractmethod, ABC
import discord
import re


all_commands = []


class CommandHandler(ABC):
    message: discord.Message
    pat: str

    def __init__(self, message: discord.Message):
        self.message = message

    @abstractmethod
    async def handle(self) -> Tuple[list, dict]:
        raise NotImplementedError

    def is_match(self) -> bool:
        return bool(re.match(self.pat, self.message.content[1:]))

    @property
    def match(self) -> Optional[re.Match]:
        return re.match(self.pat, self.message.content[1:])


def prefix_command(cls):
    all_commands.append(cls)
    return cls
