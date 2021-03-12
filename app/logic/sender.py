import asyncio
import logging
from typing import Dict, NamedTuple, List
from dataclasses import dataclass
from aiohttp import ClientSession
from pytimeparse import parse as time_parse
import json
from app.bot.bot import bot
from app.config import configuration
from app.data_models.models import (
    ChatID, JobInfo, GetInfo, GET_QUEUE, CommandsForGet, POLLING_QUEUE,
    CommandsForPolling,
)
from app.logic.parser import parse
from app.tasks import run_forever, run_background_task, cancel_and_stop_task

logger = logging.getLogger(__name__)


@dataclass
class SenderJob:
    repeat_delay: int
    names: List[str]


STANDARD_REPLAY_DELAY = '15m'
REPEAT_DELAY = configuration['callbacks_checker_delay']


class SenderCongratulationsMessage:
    def __init__(self, session: ClientSession):
        self._session = session
        self._callback_task = None

        self.chat_to_job: Dict[ChatID, asyncio.Future] = dict()
        self.chat_to_setting: Dict[ChatID, SenderJob] = dict()

    async def start(self):
        self._callback_task = run_background_task(
            self.callback_checker(), 'sender_task'
        )

    async def stop(self):
        task = self._callback_task
        self._callback_task = None
        if task is not None:
            await cancel_and_stop_task(task)

    @run_forever(repeat_delay=REPEAT_DELAY)
    async def callback_checker(self):
        await self._polling()
        await self._get()

    async def _polling(self):
        if not POLLING_QUEUE.empty():
            job_info: JobInfo = POLLING_QUEUE.get()

            chat_id = job_info.chat_id
            command = job_info.command

            if command == CommandsForPolling.START:
                await self._start_task(job_info)
            elif command == CommandsForPolling.STOP:
                await self._stop_task(chat_id)
            elif command == CommandsForPolling.NAMES:
                await self._names(chat_id, names=job_info.names)
            elif command == CommandsForPolling.DELAY:
                await self._repeat_delay(chat_id, repeat_delay=job_info.repeat_delay)

    async def _start_task(self, job_info: JobInfo) -> None:
        chat_id = job_info.chat_id

        repeat_delay = job_info.repeat_delay or STANDARD_REPLAY_DELAY
        repeat_delay = time_parse(repeat_delay)

        if chat_id in self.chat_to_job or chat_id in self.chat_to_setting:
            return

        task = run_background_task(
            self.sender(chat_id=chat_id), f'sender_{chat_id}'
        )
        self.chat_to_job[chat_id] = task
        self.chat_to_setting[chat_id] = SenderJob(repeat_delay=repeat_delay, names=[])

    async def _stop_task(self, chat_id: ChatID) -> None:
        if chat_id not in self.chat_to_job or chat_id not in self.chat_to_setting:
            return
        task = self.chat_to_job[chat_id]
        del self.chat_to_job[chat_id]
        del self.chat_to_setting[chat_id]

        await cancel_and_stop_task(task)

    async def _names(self, chat_id: str, names: str):
        try:
            names = json.loads(names)

            if not isinstance(names, list):
                raise ValueError
        except (json.decoder.JSONDecodeError, ValueError):
            await bot.send_message(chat_id, "При пасинге имен произолша ошибка")
            logger.warning(f"При пасинге имен произолша ошибка: {names}, type: {type(names)}")
            return

        if chat_id not in self.chat_to_job or chat_id not in self.chat_to_setting:
            return

        logger.warning(f"names debug: {names}, type: {type(names)}")
        self.chat_to_setting[chat_id].names = names

    async def _repeat_delay(self, chat_id: str, repeat_delay: str):
        if chat_id not in self.chat_to_job or chat_id not in self.chat_to_setting:
            return

        repeat_delay = repeat_delay or STANDARD_REPLAY_DELAY
        repeat_delay = time_parse(repeat_delay)

        self.chat_to_setting[chat_id].repeat_delay = repeat_delay

    async def _get(self):
        if not GET_QUEUE.empty():
            get_info: GetInfo = GET_QUEUE.get()

            chat_id = get_info.chat_id
            command = get_info.command
            first_name = get_info.first_name

            send_only_picture = False
            send_only_text = False
            if command == CommandsForGet.PICTURE:
                send_only_picture = True
            elif command == CommandsForGet.TEXT:
                send_only_text = True

            await self._send(
                chat_id, name=first_name, send_only_picture=send_only_picture, send_only_text=send_only_text
            )

    async def sender(self, chat_id: str):
        logger.debug('Запуск бесконечной задачи')

        local_names_iter = None
        while True:
            replay_delay = 5
            try:
                if chat_id not in self.chat_to_setting:
                    raise asyncio.CancelledError()

                replay_delay = self.chat_to_setting[chat_id].repeat_delay
                names = self.chat_to_setting[chat_id].names

                logger.error(names)
                if local_names_iter is None:
                    local_names_iter = iter(names)
                else:
                    name = local_names_iter.__next__()
                    logger.error(name)

                    await self._send(chat_id, name)

            except asyncio.CancelledError:
                logger.debug('Бесконечная задача отменена')
                raise

            except StopIteration:
                local_names_iter = None

            except Exception as err:
                logger.exception(f'Неожиданная ошибка во время работы бесконечной задачи ({err}):')
            finally:
                await asyncio.sleep(replay_delay)

    async def _send(
            self,
            _chat_id: str,
            name: str = None,
            send_only_picture: bool = False,
            send_only_text: bool = False
    ) -> None:
        if name is None:
            name = 'Безымянная'

        image_bytes, text = await parse(self._session, name)

        if not send_only_text:
            await bot.send_photo(_chat_id, image_bytes)
        if not send_only_picture:
            await bot.send_message(_chat_id, text)
