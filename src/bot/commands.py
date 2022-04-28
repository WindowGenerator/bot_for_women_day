import argparse
import logging

from aiogram import types
from typing import List

from src.bot.bot import bot, dp
from src.bot.parsers import get_generate_parser, get_polling_parser, ParseError
from src.models import (
    GENERATE_QUEUE,
    POLLING_QUEUE,
    CommandsForGenerate,
    CommandsForPolling,
    GenerateInfo,
    PollingInfo,
    PollingStart,
    PollingStop,
    PollingSettings,
)

logger = logging.getLogger(__name__)

ERROR_MESSAGE_FOR_POLLING = (
    "Используйте следующий формат: /polling [start, stop, setting] [2d 2m 2s]"
)
ERROR_MESSAGE_FOR_GET = "Используйте следующий формат: [picture, text, all]"

LOW_OPTION_FOR_COMMAND_TEXT = "Слишком мало опций для данной команды\n"
MANY_OPTION_FOR_COMMAND_TEXT = "Слишком много опций для этой команды\n"
WRONG_OPTION_FOR_COMMAND_TEXT = "Не правильная команда для этой операции\n"


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message) -> None:
    await message.reply(
        f"Привет, {message.from_user.full_name}.\n"
        f"Чтобы узнать все доступные команды. Введи команду /help\n"
    )


@dp.message_handler(commands=["help"])
async def help_command(message: types.Message) -> None:
    await message.reply(
        f"""
    /start - Начало работы с ботом\n
    /help - Показать все команды\n
    /polling [start, stop, names, delay] [время в формате: 2d 2m 2s] - запустить полинг в чатике\n
    /get [picture, text, all] - Получить картинку, текст или и то и другое\n
    """
    )


@dp.message_handler(commands=["polling"])
async def start_polling(message: types.Message) -> None:
    chat_id = message.chat.id

    args = _get_command_args(message.text)

    parser = get_polling_parser()

    try:
        args = parser.parse(args)
    except ParseError as exc:
        await bot.send_message(chat_id, exc.help)
        return

    command = CommandsForPolling(args[0])

    if command == CommandsForPolling.START:
        command_info = PollingStart(when=args.when)
    elif command == CommandsForPolling.STOP:
        command_info = PollingStop(when=args.when)
    else:
        command_info = PollingSettings(names=args.names, delay=args.delay)

    POLLING_QUEUE.put(
        PollingInfo(
            chat_id=chat_id,
            command=CommandsForPolling.SETTINGS,
            command_info=command_info,
        )
    )


@dp.message_handler(commands=["generate"])
async def generate(message: types.Message):
    chat_id = message.chat.id
    first_name = message.from_user.full_name

    args = _get_command_args(message.text)

    parser = get_generate_parser()

    try:
        args = parser.parse(args)
    except ParseError as exc:
        await bot.send_message(chat_id, exc.help)
        return

    GENERATE_QUEUE.put(
        GenerateInfo(
            chat_id=chat_id, command=args.generate_command, first_name=first_name
        )
    )


def _get_command_args(command_and_args: str) -> List:
    args = command_and_args.split(" ", maxsplit=1)

    if len(args) == 1:
        return []

    return args[1].split(" ")
