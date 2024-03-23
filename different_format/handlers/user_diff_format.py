import os
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from keyboards.reply import cancel
from different_format.utils.states import FormTransf
from different_format.keyboards import inline
from keyboards import reply
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URI

bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
# Создайте подключение к базе данных
engine = create_engine(DATABASE_URI)

# Создайте сессию для работы с базой данных
Session = sessionmaker(bind=engine)

# Создайте таблицу, из которой будут извлекаться данные
metadata = MetaData()
table = Table('employee', metadata, autoload_with=engine)
table_division = Table('Division', metadata, autoload_with=engine)

router = Router()

@router.message(FormTransf.timework)
async def fill_timework(message: Message, state: FSMContext):
    await state.update_data(timework = message.text)
    await state.set_state(FormTransf.city)
    await message.answer("Введите <b>город</b>", reply_markup=cancel, parse_mode="HTML")


@router.message(FormTransf.city)
async def fill_city(message: Message, state: FSMContext):
    await state.update_data(city = message.text)
    await state.set_state(FormTransf.reason)
    await message.answer("Введите <b>причину перевода</b>", reply_markup=cancel, parse_mode="HTML")



@router.message(FormTransf.reason)
async def fill_transferend(message: Message, state: FSMContext):
    await state.update_data(reason = message.text)
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    await state.update_data(initiator = chat_member.user.id)
    await diff_format(message, state)       

@router.message(FormTransf.timework2)
async def timeworkedit2(message: Message, state: FSMContext):
    await state.update_data(timework = message.text)
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    await state.update_data(initiator = chat_member.user.id)
    await diff_format(message, state)       


@router.message(FormTransf.city2)
async def cityedit2(message: Message, state: FSMContext):
    await state.update_data(city = message.text)
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    await state.update_data(initiator = chat_member.user.id)
    await diff_format(message, state)       


@router.message(FormTransf.reason2)
async def reasonedit2(message: Message, state: FSMContext):
    await state.update_data(reason = message.text)
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    await state.update_data(initiator = chat_member.user.id)
    await diff_format(message, state)

async def diff_format(message: Message, state:FSMContext):
    data = await state.get_data()
    session = Session()
    search_bd = data.get('search_bd')
    result = session.query(table).filter(table.c.id == search_bd).first()
    initiator = data.get('initiator')
    resultInitiator = session.query(table).filter(table.c.id_telegram == str(initiator)).first()
    search = data.get('search')
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    if search == False:
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {result.Surname} {result.Name} {result.Middle_name}, {result.Division}, {result.Position}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    else:
        result_Division = session.query(table_division).filter(table_division.c.id == int(division)).first()
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {name}, {result_Division.Division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    await message.answer(formatter_text, parse_mode="HTML", reply_markup=cancel)
    await message.answer("Запрос введен верно?", reply_markup=inline.yesnotransfer)