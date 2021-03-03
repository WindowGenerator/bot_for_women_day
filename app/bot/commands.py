import logging

from aiogram import types

from app.bot.bot import dp, bot
from app.logic.sender import CHAT_TO_JOB

logger = logging.getLogger(__name__)


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
        /test - Я тут чета тещу
    ''')


@dp.message_handler(commands=['start_polling'])
async def start_polling(message: types.Message):
    chat_id = message.chat.id
    CHAT_TO_JOB[chat_id] = {'repeat': 5 * 60}
    logger.warning(chat_id)
    await bot.send_message(chat_id, "Дарова это тестик")


@dp.message_handler(commands=['stop_polling'])
async def stop_polling(message: types.Message):
    chat_id = message.chat.id
    logger.warning(chat_id)
    await bot.send_message(chat_id, "Дарова это тестик")


@dp.message_handler(commands=['setting_polling'])
async def setting_polling(message: types.Message):
    chat_id = message.chat.id
    logger.warning(chat_id)
    await bot.send_message(chat_id, "Дарова это тестик")



