import logging
import asyncio
import sys
from datetime import datetime
import os
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, \
    get_user_locale
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.utils.markdown import hbold
from keyboards import reply
from utils.states import Employee
from filters.chat_types import ChatTypeFilter
from sqlalchemy import create_engine, MetaData, Table, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from datetime import date
from sqlalchemy import insert
import re

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
application = Table('Applications', metadata, autoload_with=engine)
question = Table('Question', metadata, autoload_with=engine)
table_division = Table('Division', metadata, autoload_with=engine)
table_position = Table('Position', metadata, autoload_with=engine)


@user_private_router.callback_query(F.data =='set_deadline')
async def deadline_message(call: types.CallbackQuery, state:FSMContext):
    session = Session()

    msg_id = call.message.message_id
    message_text = call.message.text

    pattern = r"Номер заявки:\s*(\d+)"

    match = re.search(pattern, message_text)
    number_q = match.group(1)
    await state.update_data(id_mess = msg_id)
    await state.update_data(number_q = number_q)
    print("зашел")
    print(msg_id)
    print(number_q)
    await nav_cal_handler(call.message) 

# default way of displaying a selector to user - date set for today
#@user_private_router.message(F.data.startswith == 'set_deadline')
async def nav_cal_handler(message: Message):
    await bot.edit_message_reply_markup(
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=await SimpleCalendar(locale='ru').start_calendar()
    )    

# simple calendar usage - filtering callbacks of calendar format
@user_private_router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, bot:Bot, callback_data: CallbackData, state: FSMContext):
    session = Session()
    data = await state.get_data()
    msg_id = data.get('id_mess')
    number_q = data.get('number_q')
    type_quiz = data.get('type_quiz')
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime(2024, 1, 1), datetime(2026, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'Вы установили дедлайн заявки номер {number_q} на <b>{date.strftime("%d-%m-%Y")}</b>',
        )        
        if type_quiz == True:
            await bot.delete_message(chat_id=callback_query.from_user.id, 
                                 message_id=msg_id)
            session.execute(
                update(question)
                .where(question.c.id == number_q)
                .values(Date_planned_deadline = date.strftime('%Y-%m-%d'))
            )
            session.commit()
            id_quiz = session.query(question).filter(question.c.id == number_q).first()
            user_info = session.query(table).filter(table.c.id == id_quiz.ID_Initiator).first()
            await bot.send_message(user_info.id_telegram,
                                f"Установлен дедлайн по <b>общему вопросу</b>\n\n" 
                                f"<b>Номер заявки: </b>{number_q}\n"
                                f"<b>Суть обращения: </b>{id_quiz.Essence_question}\n"
                                f"<b>Дата подачи заявки:</b> {id_quiz.Date_application}\n"
                                f"<b>Дата дедлайна:</b> {id_quiz.Date_planned_deadline}", 
                                parse_mode="HTML", reply_markup=reply.main)     
            await state.update_data(type_quiz = False)
        else:
            await bot.delete_message(chat_id=callback_query.from_user.id, 
                                 message_id=msg_id)
            session.execute(
                update(application)
                .where(application.c.id == number_q)
                .values(Date_planned_deadline = date.strftime('%Y-%m-%d'))
            )
            session.commit()
            id_info = session.query(application).filter(application.c.id == number_q).first()
            user_info = session.query(table).filter(table.c.id == id_info.ID_Initiator).first()
            text = f"<b>Сотрудник: </b>"
            if id_info.ID_Employee == 1 and id_info.ID_Class_application != 4:
                result_Division = session.query(table_division).filter(table_division.c.id == id_info.ID_Division).first()
                resultPositiong = session.query(table_position).filter(table_position.c.id == id_info.ID_Position).first()
                text += f"{id_info.Full_name_employee}, {result_Division.Division}, {resultPositiong.Position}\n"               
            elif id_info.ID_Employee != 1 and id_info.ID_Class_application != 4:
                employee_info = session.query(table).filter(table.c.id == id_info.ID_Employee).first()
                text += f"{employee_info.Surname} {employee_info.Name} {employee_info.Middle_name}, {employee_info.Division}, {employee_info.Position}\n"
            if id_info.ID_Class_application == 4:
                await bot.send_message(user_info.id_telegram,
                                    f"Установлен дедлайн по <b>общей заявке</b>\n\n" 
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"<b>Суть обращения: </b>{id_info.Essence_question}\n"
                                    f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                    f"<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}", 
                                    parse_mode="HTML", reply_markup=reply.main)     
            elif id_info.ID_Class_application == 1:
                await bot.send_message(user_info.id_telegram,
                                    f"Установлен дедлайн по <b>заявке на перевод</b>\n\n" 
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"{text}"
                                    f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                    f"<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}", 
                                    parse_mode="HTML", reply_markup=reply.main)     
            elif id_info.ID_Class_application == 2:
                await bot.send_message(user_info.id_telegram,
                                    f"Установлен дедлайн по <b>заявке на перевод на другой формат работы</b>\n\n" 
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"{text}"
                                    f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                    f"<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}", 
                                    parse_mode="HTML", reply_markup=reply.main)     
            elif id_info.ID_Class_application == 3:
                await bot.send_message(user_info.id_telegram,
                                    f"Установлен дедлайн по <b>заявке на согласование заработной платы</b>\n\n" 
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"{text}"
                                    f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                    f"<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}", 
                                    parse_mode="HTML", reply_markup=reply.main)   
            await state.update_data(type_quiz = False)  
        await state.clear()
        


# # dialog calendar usage
# @user_private_router.callback_query(DialogCalendarCallback.filter())
# async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: CallbackData):
#     print("da")
#     selected, date = await DialogCalendar(
#         locale=await get_user_locale(callback_query.from_user)
#     ).process_selection(callback_query, callback_data)
#     if selected:
#         text = f'Вы выбрали {date.strftime("%d-%m-%Y")}'
#         await callback_query.message.answer(text, reply_markup=reply.hr)
 