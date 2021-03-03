from aiogram import Bot, Dispatcher

from app.config import configuration

bot = Bot(configuration['token'])
dp = Dispatcher(bot)


