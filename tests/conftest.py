import pytest

from aiogram import Bot, Dispatcher, types
from aiohttp.test_utils import TestClient
from typing import AsyncGenerator


async def _dummy_send_photo(
    chat_id: types.base.String, photo: types.base.InputFile
) -> types.Message:
    return types.Message(text="dummy_message")


async def _dummy_send_message(
    chat_id: types.base.String, text: types.base.String
) -> types.Message:
    return types.Message(text="dummy_message")


@pytest.fixture
@pytest.mark.asyncio
async def bot_ctx(token: str = "dummy_token") -> Bot:
    bot = Bot(token, validate_token=False)

    bot.send_photo = _dummy_send_photo
    bot.send_message = _dummy_send_message

    yield bot

    await bot.close()


@pytest.fixture
@pytest.mark.asyncio
async def http_client_session_ctx() -> AsyncGenerator:
    session = TestClient()

    yield session

    await session.close()
