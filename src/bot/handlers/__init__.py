from functools import partial

from aiogram import Dispatcher
from aiohttp.web import Application

from src.bot.handlers import common, polling, generate


def setup(app: Application, dp: Dispatcher) -> None:
    polling.setup(app, dp)
    common.setup(app, dp)
    generate.setup(app, dp)
