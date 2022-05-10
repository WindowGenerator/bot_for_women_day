import argparse
import logging
from functools import partial
from typing import List

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiohttp.web import Application

from src.bot.models import PollingSettings
from src.bot.logic.sender import Sender

logger = logging.getLogger(__name__)


ABOUT_CANCEL = "If you want to complete the setup, type /cancel."
WRONG_FORMAT = "Wrong format."
SEND_NAMES_INFO = "Send me the names of the girls you want to congratulate, separated by a space."
SEND_DELAY_INFO = "Now send me the delay between congratulations in seconds."
SETUP_SUCCESS_COMPLETED = "Setting up the congratulations task has been successfully completed!"


class Form(StatesGroup):
    names = State()
    delay = State()


def setup(app: Application, dp: Dispatcher) -> None:
    dp.register_message_handler(
        partial(polling_setup_handler, app), commands=["polling_setup"]
    )
    dp.register_message_handler(partial(process_names, app), state=Form.names)
    dp.register_message_handler(partial(process_delay, app), state=Form.delay)


async def polling_setup_handler(app: Application, message: types.Message) -> None:
    bot: Bot = app["bot"]

    await Form.names.set()
    await message.reply(
        f"{SEND_NAMES_INFO}\n{ABOUT_CANCEL}"
    )


async def process_names(app: Application, message: types.Message, state: FSMContext):
    if "/" in message.text:
        await message.reply(
            f"{WRONG_FORMAT}\n{SEND_NAMES_INFO}\n{ABOUT_CANCEL}"
        )
        await Form.names.set()
        return

    names = message.text.strip().split(" ")

    await state.set_data({"names": names})

    await Form.delay.set()
    await message.reply(
        f"{SEND_DELAY_INFO}\n{ABOUT_CANCEL}"
    )


async def process_delay(app: Application, message: types.Message, state: FSMContext):
    try:
        delay = int(message.text.strip())
    except ValueError:
        await message.reply(
            f"{WRONG_FORMAT}\n{SEND_DELAY_INFO}\n{ABOUT_CANCEL}"
        )
        await Form.delay.set()
        return
    
    names = (await state.get_data())["names"]

    sender: Sender = app["sender"]

    sender.setup_polling(str(message.chat.id), PollingSettings(names, delay))

    await state.finish()
    await message.reply(SETUP_SUCCESS_COMPLETED)
