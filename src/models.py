import queue
from enum import Enum
from typing import List, NamedTuple, Optional, Union

ChatID = str


class CommandsForGenerate(str, Enum):
    PICTURE = "picture"
    TEXT = "text"
    ALL = "all"


class CommandsForPolling(str, Enum):
    START = "start"
    STOP = "stop"
    SETTINGS = "settings"


class PollingStart(NamedTuple):
    when: str


class PollingStop(NamedTuple):
    when: str


class PollingSettings(NamedTuple):
    names: List[str]
    delay: int


class PollingInfo(NamedTuple):
    chat_id: ChatID
    command: CommandsForPolling
    command_args: Union[PollingStart, PollingStop, PollingSettings]


class GenerateInfo(NamedTuple):
    chat_id: ChatID
    command: CommandsForGenerate
    first_name: str


GENERATE_QUEUE = queue.Queue()
POLLING_QUEUE = queue.Queue()
