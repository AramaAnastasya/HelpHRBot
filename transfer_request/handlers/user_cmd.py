import os
from aiogram import F, types, Router, Bot,Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list, as_marked_section, Bold,Spoiler #Italic, as_numbered_list и тд 
from aiogram.types import Message

from filters.chat_types import ChatTypeFilter
from keyboards import reply

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()

@user_private_router.message(CommandStart())
async def start_cmd(message:Message, state: FSMContext):
    # Получить информацию о члене чата (пользователе, отправившем сообщение)
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)

    # Вывести имя пользователя
    await bot.send_message(message.chat.id, 
            f"Добрый день, <b>{chat_member.user.first_name}</b>! Я виртуальный HR-помощник.\nВыберите тип обращения.",
            reply_markup=reply.main        
            )
    await state.clear()

@user_private_router.message(Command(commands=["cancel"]))
@user_private_router.message(F.text.lower() == "отмена заявки")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=reply.main
    )
    await message.answer(
        text="Выберите тип обращения"
    )
