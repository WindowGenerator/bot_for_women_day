from src.bot.logic.sender import Sender, JobAlreadyPaused, JobAlreadyStarted, JobNotFoundError
from aiogram import Bot

async def simple_start_sender_task(bot_ctx: Bot) -> None:
    sender = Sender()