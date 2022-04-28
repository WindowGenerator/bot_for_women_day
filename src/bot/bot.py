from aiogram import Bot, Dispatcher

from src.config import configuration

bot = Bot(configuration["token"])
dp = Dispatcher(bot)
