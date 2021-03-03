from aiohttp import ClientSession
from app.bot.bot import bot
from app.logic.parser import parse
from app.tasks import run_forever, run_background_task, cancel_and_stop_task
from typing import Dict

ChatId = int
CHAT_TO_JOB: Dict[ChatId, Dict] = dict()

REPEAT_DELAY = 5


class SenderCongratulationsMessage:
    def __init__(self, session: ClientSession):
        self._session = session

        self._sender_task = None
        self.chat_id = 1646852743

    async def start(self):
        self._sender_task = run_background_task(
            self.sender(), 'sender_task'
        )

    async def stop(self):
        task = self._sender_task
        self._sender_task = None
        if task is not None:
            await cancel_and_stop_task(task)

    @run_forever(repeat_delay=REPEAT_DELAY)
    async def sender(self):
        image_bytes, text = await parse(self._session, "test")
        await bot.send_photo(self.chat_id, image_bytes)
        await bot.send_message(self.chat_id, text)
