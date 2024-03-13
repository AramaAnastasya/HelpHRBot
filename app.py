import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from handlers import user_cmd

from avtorization.handlers import user_avtoriz

from transfer_request.handlers import user_private
from transfer_request.callbacks import callback_transfer

from task_ZP.handlers import user_agreement
from task_ZP.callbacks import callback_task_ZP

from general_form.handlers import quest
from general_form.callbacks import callback_data

from different_format.handlers import user_diff_format
from different_format.callbacks import callback_format

ALLOWED_UPDATES = ['message, edited_message']

bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()


dp.include_routers(
        user_cmd.user_private_router,
        user_avtoriz.user_login_router,
        user_private.user_private_router,
        callback_transfer.user_private_router,
        quest.router,
        callback_data.router,
        user_agreement.user_private_router,
        callback_task_ZP.user_private_router,
        user_diff_format.router,
        callback_format.router
    )

async def main(): 
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


asyncio.run(main())