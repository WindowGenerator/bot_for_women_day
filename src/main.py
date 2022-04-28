import asyncio
import signal
from typing import AsyncGenerator

import aiohttp
from aiohttp.web import Application, run_app

from src.bot.bot import bot, dp
from src.bot.commands import *
from src.config import configuration
from src.logic.sender import SenderCongratulationsMessage
from src.tasks import cancel_and_stop_task, run_background_task

logger = logging.getLogger(__name__)
logger.setLevel(configuration["logging_level"])


async def bot_ctx(app: Application) -> AsyncGenerator:
    app["bot"] = run_background_task(dp.start_polling(), "bot task")

    yield

    dp.stop_polling()
    await dp.wait_closed()
    await bot.close()

    await cancel_and_stop_task(app["bot"])
    logger.info("Bot task is stopped")


async def http_client_session_ctx(app: Application) -> AsyncGenerator:
    app["session"] = aiohttp.ClientSession()

    yield

    await app["session"].close()


async def sender_congratulations_message_ctx(app: Application) -> AsyncGenerator:
    app["sender"] = SenderCongratulationsMessage(app["session"])
    await app["sender"].start()

    yield

    await app["sender"].stop()


def sig_handler(loop: asyncio.AbstractEventLoop, sig: str) -> None:
    logging.info(f"Receive interrupt signal: {sig}")
    loop.stop()


def main():
    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, sig_handler, loop, "SIGINT")
    loop.add_signal_handler(signal.SIGTERM, sig_handler, loop, "SIGTERM")

    app = Application(loop=loop)
    app.cleanup_ctx.append(bot_ctx)
    app.cleanup_ctx.append(http_client_session_ctx)
    app.cleanup_ctx.append(sender_congratulations_message_ctx)

    try:
        run_app(app, host="0.0.0.0", port=8080)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")
    finally:
        loop.stop()
    loop.close()

    logger.info("Shutdown :(")


if __name__ == "__main__":
    main()
