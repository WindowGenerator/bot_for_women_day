import queue
from enum import Enum
from typing import List, NamedTuple, Optional, Union

ChatID = str


class PollingSettings(NamedTuple):
    names: List[str]
    delay: int
