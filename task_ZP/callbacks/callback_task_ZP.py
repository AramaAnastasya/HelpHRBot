import os
from aiogram import F, types, Router, Bot,Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.formatting import as_list, as_marked_section, Bold,Spoiler #Italic, as_numbered_list и тд 
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

from filters.chat_types import ChatTypeFilter

from utils.states import Employee
from task_ZP.utils.states import taskZP
from keyboards import reply
from task_ZP.keyboards.inline import get_callback_btns

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()

from config import DATABASE_URI

# Создайте подключение к базе данных
engine = create_engine(DATABASE_URI)

# Создайте сессию для работы с базой данных
Session = sessionmaker(bind=engine)

# Создайте таблицу, из которой будут извлекаться данные
metadata = MetaData()
table = Table('employee', metadata, autoload_with=engine)
table_division = Table('Division', metadata, autoload_with=engine)

async def agreement_ZP(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    session = Session()
    search_bd = user_data.get('search_bd')
    initiator = user_data.get('initiator')
    result = session.query(table).filter(table.c.id == search_bd).first()
    resultInitiator = session.query(table).filter(table.c.id_telegram == str(initiator)).first()
    proposed = user_data.get('proposed_amount')
    current = user_data.get('current_amount')
    reasons = user_data.get('reasons')
    search = user_data.get('search')
    name = user_data.get('search_name')
    division = user_data.get('search_division')
    post = user_data.get('search_post')
    
    if search == False:
        await message.answer(
        "Ваша заявка на согласование заработной платы:\n"
        f"<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n"
        f"<b>Сотрудник:</b> {result.Surname} {result.Name} {result.Middle_name}, {result.Division}, {result.Position}\n"
        f"<b>Действующая сумма:</b> {current}.\n"
        f"<b>Предлагаемая сумма:</b> {proposed}.\n"
        f"<b>Причина перевода: </b>{reasons}.",
        )
    else:
        result_Division = session.query(table_division).filter(table_division.c.id == int(division)).first()
        await message.answer(
        "Ваша заявка на согласование заработной платы:\n"
        f"<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n"
        f"<b>Сотрудник:</b> {name}, {result_Division.Division}, {post}\n"
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
async def no_app(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
            "Что необходимо изменить?", 
            reply_markup=get_callback_btns(
                btns={
                    'Сотрудник': f'search_changed',
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
