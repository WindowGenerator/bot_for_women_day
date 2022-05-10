import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, NamedTuple
import random
from functools import partial
from aiogram.bot import Bot
from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job

from src.config import configuration
from src.bot.logic.parser import parse
from src.bot.models import (
    ChatID,
    PollingSettings,
)
from src.tasks import cancel_and_stop_task, run_background_task, run_forever

logger = logging.getLogger(__name__)


class JobNotFoundError(Exception):
    pass


class JobAlreadyStarted(Exception):
    pass


class JobAlreadyPaused(Exception):
    pass


def paused(job: Job) -> bool:
    return bool(job.next_run_time)


class Sender:
    def __init__(self, session: ClientSession, bot: Bot):
        self._session = session
        self._bot = bot

        self._scheduler = AsyncIOScheduler()

    def start(self):
        self._scheduler.start()

    def stop(self):
        self._scheduler.shutdown(wait=True)

    def setup_polling(self, chat_id: ChatID, settings: PollingSettings):
        job = self._scheduler.get_job(chat_id)
        if job is not None:
            pass

        self._scheduler.add_job(
            partial(self.sender, chat_id, settings.names),
            "interval",
            seconds=settings.delay,
            id=chat_id,
            next_run_time=None,
        )

    def start_polling(self, chat_id: ChatID) -> None:
        job = self._scheduler.get_job(chat_id)

        if job is None:
            raise JobNotFoundError()
        
        if not paused(job):
            raise JobAlreadyStarted()

        job.resume()

    def pause_polling(self, chat_id: ChatID) -> None:
        job = self._scheduler.get_job(chat_id)

        if job is None:
            raise JobNotFoundError()
        
        if paused(job):
            raise JobAlreadyPaused()

        job.pause()
    
    def stop_polling(self, chat_id: ChatID) -> None:
        job = self._scheduler.get_job(chat_id)
        if job is None:
            raise JobNotFoundError()

        job.remove()

    async def generate(self, chat_id: str, first_name: str) -> None:
        await self._send(chat_id, name=first_name)

    async def sender(self, chat_id: str, names: List[str]) -> None:
        await self._send(chat_id, random.choice(names))

    async def _send(
        self,
        _chat_id: str,
        name: str
    ) -> None:

        image_bytes, text = await parse(self._session, name)

        await self._bot.send_photo(_chat_id, image_bytes)
        await self._bot.send_message(_chat_id, text)
