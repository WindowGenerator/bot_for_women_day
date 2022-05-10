import argparse
import logging
from functools import partial
from typing import List

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiohttp.web import Application

from src.bot.logic.sender import Sender

logger = logging.getLogger(__name__)


def setup(app: Application, dp: Dispatcher) -> None:
    dp.register_message_handler(
        partial(generate_handler, app), commands=["generate", "g"]
    )


async def generate_handler(app: Application, message: types.Message) -> None:
    sender: Sender = app["sender"]
    await sender.generate(message.chat.id, message.chat.first_name)
