import asyncio
from telegram import Bot
from code.settings import *


async def second():
    bot = Bot(TOKEN)
    async with bot:
        await bot.send_message(408831767, "")


asyncio.run(second())
