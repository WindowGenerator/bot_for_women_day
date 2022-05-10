import asyncio

import aiohttp

API_PATH = "https://yandex.ru/lab/api/postcard?name="


async def parse(session: aiohttp.ClientSession, name: str):
    async with session.get(API_PATH + str(name)) as response:
        json = await response.json(encoding="utf-8")
    url_to_image = json["image"]
    text = json["text"]

    async with session.get(url_to_image) as image_response:
        image_bytes = await image_response.content.read()

    return image_bytes, text
