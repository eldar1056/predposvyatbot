import asyncio
from telegram import Bot
from code.settings import *


async def second():
    bot = Bot(TOKEN)
    async with bot:
        await bot.send_message(624972316, )

#asyncio.run(second())
print(f'{"123":<30} 444')
