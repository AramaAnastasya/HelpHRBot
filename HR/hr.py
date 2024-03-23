import os
from aiogram import F, types, Router, Bot,Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.formatting import as_list, as_marked_section, Bold,Spoiler #Italic, as_numbered_list и тд 
from aiogram.types import Message
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

from filters.chat_types import ChatTypeFilter

from keyboards import reply


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()

@user_private_router.message((F.text.lower() == "актуальные задачи"))
async def transfer_cmd(message: types.Message, state:FSMContext):
    await state.update_data(request="актуальные задачи")
    await message.answer(
        "узнать актуальные задачи",
        reply_markup=reply.back
    )
    

@user_private_router.message((F.text.lower() == "новые задачи")) 
async def transfer_cmd(message: types.Message, state:FSMContext):
    await state.update_data(request="новые задачи")
    await message.answer(
        "узнать новые задачи",
        reply_markup=reply.back
    )
    

@user_private_router.message((F.text.lower() == "статистика")) 
async def transfer_cmd(message: types.Message, state:FSMContext):
    await state.update_data(request="статистика")
    await message.answer(
        "узнать статистику",
        reply_markup=reply.back
    )