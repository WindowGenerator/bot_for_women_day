import argparse
import logging
from functools import partial
from typing import List

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiohttp.web import Application
from src.bot.logic.sender import Sender, JobNotFoundError

logger = logging.getLogger(__name__)


def setup(app: Application, dp: Dispatcher) -> None:
    dp.register_message_handler(
        partial(polling_stop_handler, app), commands=["polling_stop"]
    )


async def polling_stop_handler(app: Application, message: types.Message) -> None:
    sender: Sender = app["sender"]

    sender.stop_polling(str(message.chat.id))

    await message.reply("The polling task stopped successfully.\nTo start it type /polling_start")
