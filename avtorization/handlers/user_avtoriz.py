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

from filters.chat_types import ChatTypeFilter
from avtorization.utils.states import FSMAdmin
from keyboards import reply

user_login_router = Router()
user_login_router.message.filter(ChatTypeFilter(["private"]))


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()




@user_login_router.message(FSMAdmin.phone)
async def cmd_is(message: types.Message, state: FSMContext):
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    
    if message.contact:
        if message.contact.phone_number == '+7777777777':
            await state.clear()
            await message.reply(f"Вы успешно авторизованы! Ваш номер телефона: {message.contact.phone_number}, ваш ID: {chat_member.user.id}")
            await message.answer("Выберите тип обращения.", reply_markup=reply.main)
    elif message.text == '+77777777777':
        await state.clear()
        await message.reply(f"Вы успешно авторизованы!! Ваш номер телефона: {message.text}, ваш ID: {chat_member.user.id}")
        await message.answer("Выберите тип обращения.", reply_markup=reply.main)
    else:
        await message.reply("Ошибка авторизации. Пожалуйста, отправьте свой контактный номер телефона.")
