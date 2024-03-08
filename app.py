import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from transfer_request.handlers import user_cmd, user_private
from transfer_request.callbacks import callback_transfer


from general_form.handlers import quest, bot_msg
from general_form.callbacks import callback_data

ALLOWED_UPDATES = ['message, edited_message']

bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()


dp.include_routers(
        user_cmd.user_private_router,
        user_private.user_private_router,
        callback_transfer.user_private_router,
        quest.router,
        callback_data.router,
        bot_msg.router
    )

async def main(): 
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


asyncio.run(main())