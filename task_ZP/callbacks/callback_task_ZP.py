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

from utils.states import Employee
from task_ZP.utils.states import taskZP
from keyboards import reply
from task_ZP.keyboards.inline import get_callback_btns

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()



async def agreement_ZP(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data.get('search_name')
    division = user_data.get('search_division')
    post = user_data.get('search_post')
    proposed = user_data.get('proposed_amount')
    current = user_data.get('current_amount')
    reasons = user_data.get('reasons')

    await message.answer(
        "Ваша заявка на согласование заработной платы:\n"
        f"<b>Инициатор:</b> \n"
        f"<b>Сотрудник:</b> {name}, {division}, {post}\n"
        f"<b>Действующая сумма:</b> {current}.\n"
        f"<b>Предлагаемая сумма:</b> {proposed}.\n"
        f"<b>Причина перевода: </b>{reasons}.",
    )
    await message.answer(
        "Запрос введен верно?",
        reply_markup=get_callback_btns(
            btns={
            'Данные верны': f'yes_task',
            'Изменить данные': f'no_task',
            }   
        )
    )

@user_private_router.callback_query(F.data.startswith("yes_task"))
async def yes_app(callback:types.CallbackQuery):
    await callback.message.delete_reply_markup()
    await bot.send_message(callback.from_user.id, "Вы подтвердили правильность введенных данных.")
    await callback.message.answer(
        "Отправить заявку HR?",      
        reply_markup=get_callback_btns(
                btns={
                    'Да': f'go_app',
                    'Нет': f'stop_app',
                }
            ),    
    )

@user_private_router.callback_query(F.data.startswith("go_app"))
async def go_app(callback: types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Заявка успешно отправлена!"
    )
    await callback.message.answer(
        "Информация о сроке решения будет отправлена Вам в ближайшее время.", reply_markup=reply.main
    )
    # Сброс состояния и сохранённых данных у пользователя
    await state.clear()

@user_private_router.callback_query(F.data.startswith("stop_app"))
async def stop_app(callback: types.CallbackQuery):
    await callback.message.delete_reply_markup() 
    await callback.message.answer(
        "Выберите тип обращения.", reply_markup=reply.main
    )

@user_private_router.callback_query(F.data.startswith("no_task"))
async def no_app(callback:types.CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Что необходимо изменить?", 
        reply_markup=get_callback_btns(
                btns={
                    'ФИО сотрудника': f'search_name_change',
                    'Подразделение': f'search_division_change',
                    'Должность': f'search_post_change',
                    'Действующая сумма': f'current_amount_change',
                    'Предлагаемая сумма': f'proposed_amount_change',
                    'Причины перевода': f'reasons_change',
                }
            ),    
    )

 

@user_private_router.callback_query(F.data.startswith("proposed_amount_change"))
async def proposed_amount_change(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Введите исправленную <b>предлагаемую сумму</b>", 
    )
    await state.set_state(taskZP.proposed_amount)
    await state.update_data({'proposed_amount_changed': True})   

@user_private_router.callback_query(F.data.startswith("current_amount_change"))
async def current_amount_change(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Введите исправленную <b>действующую сумму</b>", 
    )
    await state.set_state(taskZP.current_amount)
    await state.update_data(current_amount_changed=True)
    
@user_private_router.callback_query(F.data.startswith("reasons_change"))
async def reasons_change(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Введите исправленные <b>причины перевода</b>", 
    )
    await state.set_state(taskZP.reasons)
    await state.update_data(reasons_changed=True)
