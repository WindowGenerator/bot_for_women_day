import argparse
import logging
from functools import partial
from typing import List

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiohttp.web import Application

logger = logging.getLogger(__name__)


def setup(app: Application, dp: Dispatcher) -> None:
    dp.register_message_handler(
        partial(cancel_handler, app), state="*", commands=["cancel", "c"]
    )
    dp.register_message_handler(partial(start_handler, app), commands=["start", "s"])
    dp.register_message_handler(partial(help_handler, app), commands=["help", "h"])


async def cancel_handler(message: types.Message, state: FSMContext):
    """Allow user to cancel action via /cancel command"""

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply("Cancelled.")


async def start_handler(app: Application, message: types.Message) -> None:
    await message.reply(
        f"Привет, {message.from_user.full_name}.\n"
        f"Чтобы узнать все доступные команды. Введи команду /help\n"
    )


async def help_handler(app: Application, message: types.Message) -> None:
    await message.reply(
        f"""
    /start - Начало работы с ботом\n
    /help - Показать все команды\n
    /polling [start, stop, names, delay] [время в формате: 2d 2m 2s] - запустить полинг в чатике\n
    /get [picture, text, all] - Получить картинку, текст или и то и другое\n
    """
    )
