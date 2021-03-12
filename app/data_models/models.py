import queue
from typing import NamedTuple, Optional, List
from enum import Enum

ChatID = str


class CommandsForGet(str, Enum):
    PICTURE = 'picture'
    TEXT = 'text'
    ALL = 'all'


class CommandsForPolling(str, Enum):
    START = 'start'
    STOP = 'stop'
    NAMES = 'names'
    DELAY = 'delay'


class JobInfo(NamedTuple):
    chat_id: ChatID
    command: CommandsForPolling
    repeat_delay: Optional[str]
    names: Optional[str]


class GetInfo(NamedTuple):
    chat_id: ChatID
    command: CommandsForGet
    first_name: str


GET_QUEUE = queue.Queue()
POLLING_QUEUE = queue.Queue()
