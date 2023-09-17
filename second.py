import asyncio
from telegram import Bot
from code.settings import *
from code.data import Data


async def second():
    bot = Bot(TOKEN)

    data = Data()
    # async with bot:
    #     for stage in data.stagers.keys():
    #         for stager in data.stagers[stage]:
    #             await bot.send_message(stager.chat_id, 'Вы проводите ' + str(stager.stage_id) + ' этап: '
    #                                    + STAGE_NAMES[stager.stage_id] +
    #                                    '. Верно ли это? Пожалуйста, отправьте да/нет в ответ.')
    #     for arm_id in data.armenians.keys():
    #         for armenian in data.armenians[arm_id]:
    #             await bot.send_message(armenian.chat_id, 'Извиняюсь за спам. Ответьте пожалуйста.')
    #     for admin in data.admins:
    #         await bot.send_message(admin, 'Извиняюсь за спам. Ответьте пожалуйста.')


asyncio.run(second())
