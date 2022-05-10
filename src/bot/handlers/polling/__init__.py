import argparse
import logging
from functools import partial
from typing import List

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiohttp.web import Application

from src.bot.handlers.polling import pause, setup, start, stop

logger = logging.getLogger(__name__)


def setup(app: Application, dp: Dispatcher) -> None:
    pause.setup(app, dp)
    setup.setup(app, dp)
    start.setup(app, dp)
    stop.setup(app, dp)