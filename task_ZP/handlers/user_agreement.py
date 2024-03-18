import os
from aiogram import F, types, Router, Bot,Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.formatting import as_list, as_marked_section, Bold,Spoiler #Italic, as_numbered_list и тд 
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from filters.chat_types import ChatTypeFilter

from task_ZP.utils.states import taskZP
from keyboards import reply
from task_ZP.keyboards.inline import get_callback_btns
from task_ZP.callbacks.callback_task_ZP import agreement_ZP

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()


@user_private_router.message(taskZP.current_amount)
async def cmd_post(message: Message, state: FSMContext):
    await state.update_data(current_amount=message.text)
    data = await state.get_data()
    current_amount_change = data.get('current_amount_changed')
    if current_amount_change == True:  
        await agreement_ZP(message, state)
        await state.update_data(current_amount_changed=False)
    else:  
        await message.answer(
            "Введите <b>предлагаемую сумму</b>",
            reply_markup=reply.cancel
        )
        await state.update_data(proposed_amount_changed=False)
        await state.set_state(taskZP.proposed_amount)


@user_private_router.message(taskZP.proposed_amount)
async def cmd_division(message: Message, state: FSMContext):
    await state.update_data(proposed_amount=message.text)
    user_data = await state.get_data()
    proposed_amount_change = user_data.get('proposed_amount_changed')
    if proposed_amount_change == True:  
        await agreement_ZP(message, state)
        await state.update_data(proposed_amount_changed=False)
    else: 
        await message.answer(
            "Введите <b>причину перевода</b>",
              reply_markup=reply.cancel
        )
        await state.update_data(reasons_changed=False)
        await state.set_state(taskZP.reasons)

@user_private_router.message(taskZP.reasons)
async def cmd_is(message: Message, state: FSMContext):
    await state.update_data(reasons=message.text)
    user_data = await state.get_data()
    reasons_change = user_data.get('reasons_changed')
    if reasons_change == True: 
        await agreement_ZP(message, state)
        await state.update_data(reasons_change=False)
    else: 

        await agreement_ZP(message, state)

