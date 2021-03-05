import logging

from aiogram import types

from app.bot.bot import dp, bot
from app.data_models.models import (
    POLLING_QUEUE,
    GET_QUEUE,
    JobInfo,
    GetInfo,
    CommandsForPolling,
    CommandsForGet,
)

logger = logging.getLogger(__name__)
ERROR_MESSAGE_FOR_POLLING = "Используйте следующий формат: /polling [start, stop, setting] [2d 2m 2s]"
ERROR_MESSAGE_FOR_GET = "Используйте следующий формат: [picture, text, all]"

LOW_OPTION_FOR_COMMAND_TEXT = "Слишком мало опция для данной команды\n"
MANY_OPTION_FOR_COMMAND_TEXT = "Слишком много опция для этой команды\n"
WRONG_OPTION_FOR_COMMAND_TEXT = "Не правильная команда для этой операции\n"


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply(
        f'Привет, {message.from_user.full_name}.\n'
        f'Чтобы узнать все доступные команды. Введи команду /help\n'
    )


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply(f'''
    /start - Начало работы с ботом\n
    /help - Показать все команды\n
    /polling [start, stop, names, delay] [время в формате: 2d 2m 2s] - запустить полинг в чатике\n
    /get [picture, text, all] - Получить картинку, текст или и то и другое\n
    ''')


@dp.message_handler(commands=['polling'])
async def start_polling(message: types.Message):
    command_split = message.text.split(' ', maxsplit=2)
    chat_id = message.chat.id

    optional = None
    command = None
    if len(command_split) < 2:
        await bot.send_message(chat_id, LOW_OPTION_FOR_COMMAND_TEXT + ERROR_MESSAGE_FOR_POLLING)
        return
    if len(command_split) == 2:
        _, command = command_split
    elif len(command_split) == 3:
        _, command, optional = command_split
    elif len(command_split) > 3:
        await bot.send_message(chat_id, MANY_OPTION_FOR_COMMAND_TEXT + ERROR_MESSAGE_FOR_POLLING)
        return

    if command == CommandsForPolling.START:
        POLLING_QUEUE.put(
            JobInfo(chat_id=chat_id, repeat_delay=optional, command=CommandsForPolling.START, names=None)
        )
    elif command == CommandsForPolling.STOP:
        POLLING_QUEUE.put(
            JobInfo(chat_id=chat_id, repeat_delay=None, command=CommandsForPolling.STOP, names=None)
        )
    elif command == CommandsForPolling.NAMES:
        POLLING_QUEUE.put(
            JobInfo(chat_id=chat_id, repeat_delay=None, command=CommandsForPolling.NAMES, names=optional)
        )
    elif command == CommandsForPolling.DELAY:
        POLLING_QUEUE.put(
            JobInfo(chat_id=chat_id, repeat_delay=optional, command=CommandsForPolling.NAMES, names=None)
        )
    else:
        await bot.send_message(chat_id, WRONG_OPTION_FOR_COMMAND_TEXT + ERROR_MESSAGE_FOR_POLLING)
        return

    logger.warning(f"command: {command}, replay_delay: {optional}")


@dp.message_handler(commands=['get'])
async def get(message: types.Message):
    command_split = message.text.split(' ', maxsplit=1)
    chat_id = message.chat.id
    first_name = message.from_user.full_name

    command = None
    if len(command_split) < 2:
        await bot.send_message(chat_id, LOW_OPTION_FOR_COMMAND_TEXT + ERROR_MESSAGE_FOR_GET)
        return
    if len(command_split) == 2:
        _, command = command_split
    elif len(command_split) > 2:
        await bot.send_message(chat_id, MANY_OPTION_FOR_COMMAND_TEXT + ERROR_MESSAGE_FOR_GET)
        return

    if command == CommandsForGet.PICTURE:
        GET_QUEUE.put(
            GetInfo(chat_id=chat_id, command=CommandsForGet.PICTURE, first_name=first_name)
        )
    elif command == CommandsForGet.TEXT:
        GET_QUEUE.put(
            GetInfo(chat_id=chat_id, command=CommandsForGet.TEXT, first_name=first_name)
        )
    elif command == CommandsForGet.ALL:
        GET_QUEUE.put(
            GetInfo(chat_id=chat_id, command=CommandsForGet.ALL, first_name=first_name)
        )
    else:
        await bot.send_message(chat_id, WRONG_OPTION_FOR_COMMAND_TEXT + ERROR_MESSAGE_FOR_GET)
        return
