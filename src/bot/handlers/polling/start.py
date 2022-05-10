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
        partial(polling_start_handler, app), commands=["polling_start"]
    )


async def polling_start_handler(app: Application, message: types.Message) -> None:
    sender: Sender = app["sender"]

    try:
        sender.start_polling(str(message.chat.id))
    except JobNotFoundError:
        pass
    

    await message.reply("The polling task started successfully.\nTo stop it type /polling_stop")
