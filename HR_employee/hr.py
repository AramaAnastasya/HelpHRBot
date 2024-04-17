import os
from aiogram import F, types, Router, Bot,Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.formatting import as_list, as_marked_section, Bold,Spoiler #Italic, as_numbered_list и тд 
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime, timedelta
from sqlalchemy import insert
import re
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, \
    get_user_locale
from HR_employee.keyboards.inline import get_callback_btns, sorted_keybordFirst, sorted_keybordSecond, sortedAct_keybordFirst, sortedAct_keybordSecond, сhoiceStatistic_keybord
from HR_employee.keyboards import inline
from filters.chat_types import ChatTypeFilter
from HR_employee.utils.states import Applications

from keyboards import reply

from general_form.keyboards.inline import send, sendAct, sendquiz, sendquizAct
from different_format.keyboards.inline import send_different, send_differentAct
from task_ZP.keyboards.inline import send_zp, send_zpAct
from transfer_request.keyboards.inline import send_transfer, send_transferAct

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()

from config import DATABASE_URI

engine = create_engine(DATABASE_URI)

# Создайте сессию для работы с базой данных
Session = sessionmaker(bind=engine)
metadata = MetaData()
table_Employee = Table('employee', metadata, autoload_with=engine)
table_application = Table('Applications', metadata, autoload_with=engine)
table_question = Table('Question', metadata, autoload_with=engine)
table_position = Table('Position', metadata, autoload_with=engine)
table_division = Table('Division', metadata, autoload_with=engine)


@user_private_router.message((F.text.lower() == "актуальные задачи"))
async def transfer_cmd(message: types.Message, state:FSMContext):
    await state.update_data(chat_id=message.from_user.id, request="Актуальные задачи", reply_markup=reply.hr)
    await message.answer("Выберите категорию", reply_markup=sortedAct_keybordFirst)

# Вывод  inline-клавиатуры для сортировки заявок 
@user_private_router.callback_query(F.data == "sort_app1")
async def sort_applic(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    await bot.send_message(callback.from_user.id, "Выберите тип заявки для вывода актуальных задач", reply_markup=sortedAct_keybordSecond, parse_mode="HTML")

# Выводзаявок актуальных на перевод
@user_private_router.callback_query(F.data == "sort_app_transf1")
async def go_app_transf(callback: types.CallbackQuery, bot: Bot, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline != None, table_application.c.Date_actual_deadline == None, table_application.c.ID_Class_application == 1).order_by(table_application.c.Date_planned_deadline).all()
    if result:
        for row in result:
            # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            if(row.ID_Employee == 1):
                result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                    f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}", 
                    reply_markup=send_transferAct
                    )
            else:
                result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                    f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}", 
                    reply_markup=send_transferAct)
    else:
        await callback.message.answer(
                    f"Актуальных заявок на перевод на данный момент нет",
                    reply_markup=reply.hr
                    )
    # Закройте сессию
    session.close()

# Вывод автуальных заявок на смену ЗП
@user_private_router.callback_query(F.data == "sort_app_zp1")
async def go_app_zp(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    # Получите сессию для работы с базой данных
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline != None, table_application.c.Date_actual_deadline == None, table_application.c.ID_Class_application == 3).order_by(table_application.c.Date_planned_deadline).all()
    if result:
        for row in result:
            # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            if(row.ID_Employee == 1):
                result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на согласование заработной платы</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                        f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                        f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                        f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                        f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                        f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                    reply_markup=send_zpAct)
            else:
                result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на согласование заработной платы</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                        f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                        f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                        f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                        f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                        f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                    reply_markup=send_zpAct)
    else:
        await callback.message.answer(
                    f"Актуальных заявок на согласование заработной платы на данный момент нет",
                    reply_markup=reply.hr
                    )
    session.close()

# Вывод актуальных заявок перевод на другой формат рабоыт
@user_private_router.callback_query(F.data == "sort_app_diff1")
async def go_app_diff(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    # Получите сессию для работы с базой данных
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline != None, table_application.c.Date_actual_deadline == None, table_application.c.ID_Class_application == 2).order_by(table_application.c.Date_planned_deadline).all()
    if result:
        for row in result:
            # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            if(row.ID_Employee == 1):
                result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на перевод на другой формат работы</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                                f"<b>Инициатор:</b>  {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                                f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                                f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                    reply_markup=send_differentAct)
            else:
                result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на перевод на другой формат работы</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                                f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                                f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                                f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}", 
                    reply_markup=send_differentAct)   
    else:
        await callback.message.answer(
                    f"Актуальных заявок на перевод на другой формат работы на данный момент нет",
                    reply_markup=reply.hr
                    ) 
    # Закройте сессию
    session.close()

# Вывод актуальных заявок общей формы
@user_private_router.callback_query(F.data == "sort_app_general1")
async def go_app_general(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    # Получите сессию для работы с базой данных
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline != None, table_application.c.Date_actual_deadline == None, table_application.c.ID_Class_application == 4).order_by(table_application.c.Date_planned_deadline).all()
    if result:
        for row in result:
            # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            await callback.message.answer(
                f"<b>Заявка по общей форме</b>\n"
                f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                            f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                reply_markup=sendAct)
    else:
        await callback.message.answer(
                    f"Актуальных заявок на данный момент нет",
                    reply_markup=reply.hr
                    )
    # Закройте сессию
    session.close()

# Вывод актуальных всех заявок
@user_private_router.callback_query(F.data == "sort_app_all1")
async def go_app_all(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    # Получите сессию для работы с базой данных
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline != None, table_application.c.Date_actual_deadline == None).order_by(table_application.c.Date_planned_deadline).all()
    if result:
        for row in result:
            # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            if(row.ID_Class_application == 1):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод:</b>\n<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}", 
                        reply_markup=send_transferAct)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод:</b>\n<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}", 
                    reply_markup=send_transferAct)
            if(row.ID_Class_application == 2):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод на другой формат работы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                                    f"<b>Инициатор:</b>  {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                    f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                                    f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                    f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                    f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                                    f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                        reply_markup=send_differentAct)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод на другой формат работы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                                    f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                    f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                                    f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                    f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                                    f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                        reply_markup=send_differentAct)
            if(row.ID_Class_application == 3):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на согласование заработной платы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                            f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                            f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                            f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                        reply_markup=send_zpAct)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на согласование заработной платы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                            f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                            f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                            f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                        reply_markup=send_zpAct)
            if(row.ID_Class_application == 4):
                await callback.message.answer(
                    f"<b>Заявка по общей форме</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                                f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                                f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                                f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                    reply_markup=sendAct)
    else:
        await callback.message.answer(
                f"Актуальных заявок на данный момент нет",
                reply_markup=reply.hr
                )
                
    # Закройте сессию
    session.close()


# Вывод актуальных вопросов
@user_private_router.callback_query(F.data == "sort_quest1")
async def go_app_general(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    # Получите сессию для работы с базой данных
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result_Quest = session.query(table_question).filter(table_question.c.Date_planned_deadline != None, table_question.c.Date_actual_deadline == None).order_by(table_question.c.Date_planned_deadline).all()
    if result_Quest:
        for row in result_Quest:
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            await callback.message.answer(
                f"<b>Вопрос</b>\n"
                f"<b>Номер вопроса:</b> {row.id}\n"
                            f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                            f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                reply_markup=sendquizAct)
    else:
        await callback.message.answer(
                    f"Актуальных вопросов на данный момент нет",
                    reply_markup=reply.hr
                    )
    # Закройте сессию
    session.close()

# Вывод актуальных всех вопросов и заявок
@user_private_router.callback_query(F.data == "sort_all1")
async def go_app_general(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline != None, table_application.c.Date_actual_deadline == None).order_by(table_application.c.Date_planned_deadline).all()
    result_Quest = session.query(table_question).filter(table_question.c.Date_planned_deadline != None, table_question.c.Date_actual_deadline == None).order_by(table_question.c.Date_planned_deadline).all()
    if result and not result_Quest:
        for row in result:
        # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            if(row.ID_Class_application == 1):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n <b>Дата подачи заявки:</b> {row.Date_application}\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}", 
                        reply_markup=send_transferAct)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}", 
                        reply_markup=send_transferAct)
            if(row.ID_Class_application == 2):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод на другой формат работы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                                    f"<b>Инициатор:</b>  {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                    f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                                    f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                    f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                    f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                                    f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                        reply_markup=send_differentAct)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод на другой формат работы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                                    f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                    f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                                    f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                    f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                    f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                                    f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                        reply_markup=send_differentAct)
            if(row.ID_Class_application == 3):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на согласование заработной платы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                            f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                            f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                            f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                        reply_markup=send_zpAct)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на согласование заработной платы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                            f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                            f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                            f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                        reply_markup=send_zpAct)
            if(row.ID_Class_application == 4):
                await callback.message.answer(
                    f"<b>Заявка по общей форме</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                                f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                                f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                                f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                    reply_markup=sendAct)
    elif result and result_Quest:
        for row in result:
            # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            if(row.ID_Class_application == 1):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n <b>Дата подачи заявки:</b> {row.Date_application}\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}", 
                        reply_markup=send_transferAct)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}\n<b>Дата дедлайна:</b> {row.Date_planned_deadline}", 
                        reply_markup=send_transferAct)
            if(row.ID_Class_application == 2):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод на другой формат работы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                                    f"<b>Инициатор:</b>  {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                    f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                                    f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                    f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                    f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                                    f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                        reply_markup=send_differentAct)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод на другой формат работы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                                    f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                    f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                                    f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                    f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                    f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                                    f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                        reply_markup=send_differentAct)
            if(row.ID_Class_application == 3):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на согласование заработной платы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                            f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                            f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                            f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                        reply_markup=send_zpAct)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на согласование заработной платы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                            f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                            f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                            f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                        reply_markup=send_zpAct)
            if(row.ID_Class_application == 4):
                await callback.message.answer(
                    f"<b>Заявка по общей форме</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                                f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                                f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                                f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                    reply_markup=sendAct)
        for row in result_Quest:
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            await callback.message.answer(
                f"<b>Вопрос</b>\n"
                f"<b>Номер вопроса:</b> {row.id}\n"
                            f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                            f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                reply_markup=sendquizAct)
    elif not result and result_Quest:
        for row in result_Quest:
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            await callback.message.answer(
                f"<b>Вопрос</b>\n"
                f"<b>Номер вопроса:</b> {row.id}\n"
                            f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}\n"
                            f"<b>Дата дедлайна:</b> {row.Date_planned_deadline}",
                reply_markup=sendquizAct)
    
    else:
        await callback.message.answer(  
                    f"Актуальных задач на данный момент нет",
                    reply_markup=reply.hr
                    )
    
   
    # Закройте сессию
    session.close()

   
    

@user_private_router.message((F.text.lower() == "новые задачи")) 
async def transfer_cmd23(message: types.Message, state:FSMContext):
    await state.update_data(chat_id=message.from_user.id, request="Новые задачи", reply_markup=reply.hr)
    await message.answer("Выберите категорию", reply_markup=sorted_keybordFirst)


# Вывод  inline-клавиатуры для сортировки заявок 
@user_private_router.callback_query(F.data == "sort_app")
async def sort_applic(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    await bot.send_message(callback.from_user.id, "Выберите тип заявки для вывода новых задач", reply_markup=sorted_keybordSecond, parse_mode="HTML")

# Вывод заявок на перевод
@user_private_router.callback_query(F.data == "sort_app_transf")
async def go_app_transf(callback: types.CallbackQuery, bot: Bot, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline == None, table_application.c.ID_Class_application == 1).order_by(table_application.c.Date_application).all()
    if result:
        for row in result:
            # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            if(row.ID_Employee == 1):
                result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                    f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}", 
                    reply_markup=send_transfer)
            else:
                result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                    f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}", 
                    reply_markup=send_transfer)
    else:
        await callback.message.answer(
                    f"Новых заявок на перевод на данный момент нет",
                    reply_markup=reply.hr
                    )
    # Закройте сессию
    session.close()

# Вывод заявок на смену ЗП
@user_private_router.callback_query(F.data == "sort_app_zp")
async def go_app_zp(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    # Получите сессию для работы с базой данных
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline == None, table_application.c.ID_Class_application == 3).order_by(table_application.c.Date_application).all()
    if result:
        for row in result:
            # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            if(row.ID_Employee == 1):
                result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на согласование заработной платы</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                        f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                        f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                        f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                        f"<b>Дата подачи заявки:</b> {row.Date_application}",
                    reply_markup=send_zp)
            else:
                result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на согласование заработной платы</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                        f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                        f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                        f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                        f"<b>Дата подачи заявки:</b> {row.Date_application}",
                    reply_markup=send_zp)
    else:
        await callback.message.answer(
                    f"Новых заявок на согласование заработной платы на данный момент нет",
                    reply_markup=reply.hr
                    )
    session.close()

# Вывод заявок перевод на другой формат рабоыт
@user_private_router.callback_query(F.data == "sort_app_diff")
async def go_app_diff(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    # Получите сессию для работы с базой данных
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline == None, table_application.c.ID_Class_application == 2).order_by(table_application.c.Date_application).all()
    if result:
        for row in result:
            # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            if(row.ID_Employee == 1):
                result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на перевод на другой формат работы</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                                f"<b>Инициатор:</b>  {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                                f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                f"<b>Дата подачи заявки:</b> {row.Date_application}", 
                    reply_markup=inline.send_different)
            else:
                result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на перевод на другой формат работы</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                                f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                                f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                f"<b>Дата подачи заявки:</b> {row.Date_application}", 
                    reply_markup=inline.send_different) 
    else:
        await callback.message.answer(
                    f"Новых заявок на перевод на другой формат работы на данный момент нет",
                    reply_markup=reply.hr
                    )   
    # Закройте сессию
    session.close()

# Вывод  заявок общей формы
@user_private_router.callback_query(F.data == "sort_app_general")
async def go_app_general(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    # Получите сессию для работы с базой данных
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline == None, table_application.c.ID_Class_application == 4).order_by(table_application.c.Date_application).all()
    if result:
        for row in result:
            # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            await callback.message.answer(
                f"<b>Заявка по общей форме</b>\n"
                f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}",
                reply_markup=send)
    else:
        await callback.message.answer(
                    f"Новых заявок на данный момент нет",
                    reply_markup=reply.hr
                    )
    # Закройте сессию
    session.close()

# Вывод всех заявок
@user_private_router.callback_query(F.data == "sort_app_all")
async def go_app_all(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    # Получите сессию для работы с базой данных
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline == None).order_by(table_application.c.Date_application).all()
    if result:
        for row in result:
            # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            if(row.ID_Class_application == 1):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}\n", 
                        reply_markup=send_transfer)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}\n", 
                        reply_markup=send_transfer)
            if(row.ID_Class_application == 2):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод на другой формат работы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                                    f"<b>Инициатор:</b>  {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                    f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                                    f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                    f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                    f"<b>Дата подачи заявки:</b> {row.Date_application}", 
                        reply_markup=send_different)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод на другой формат работы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                                    f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                    f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                                    f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                    f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                    f"<b>Дата подачи заявки:</b> {row.Date_application}", 
                        reply_markup=send_different)
            if(row.ID_Class_application == 3):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на согласование заработной платы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                            f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                            f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}",
                        reply_markup=send_zp)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на согласование заработной платы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                            f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                            f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}",
                    reply_markup=send_zp)
            if(row.ID_Class_application == 4):
                await callback.message.answer(
                    f"<b>Заявка по общей форме</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                                f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                                f"<b>Дата подачи заявки:</b> {row.Date_application}",
                    reply_markup=send)
    else:
        await callback.message.answer(
                    f"Новых заявок на данный момент нет",
                    reply_markup=reply.hr
                    )                
    # Закройте сессию
    session.close()


# Вывод вопросов
@user_private_router.callback_query(F.data == "sort_quest")
async def go_app_general(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    # Получите сессию для работы с базой данных
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result_Quest = session.query(table_question).filter(table_question.c.Date_planned_deadline == None).order_by(table_question.c.Date_application).all()
    if result_Quest:
        for row in result_Quest:
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            await callback.message.answer(
                f"<b>Вопрос</b>\n"
                f"<b>Номер вопроса:</b> {row.id}\n"
                            f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}",
                reply_markup=sendquiz)
    else:
        await callback.message.answer(  
                    f"Новых вопросов на данный момент нет",
                    reply_markup=reply.hr
                    )
    # Закройте сессию
    session.close()

# Вывод всех вопросов и заявок
@user_private_router.callback_query(F.data == "sort_all")
async def go_app_general(callback: types.CallbackQuery, state:FSMContext):
    msg_id = callback.message.message_id
    await bot.delete_message(callback.message.chat.id, msg_id)
    # Получите сессию для работы с базой данных
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline == None).order_by(table_application.c.Date_application).all()
    result_Quest = session.query(table_question).filter(table_question.c.Date_planned_deadline == None).order_by(table_question.c.Date_application).all()
    if result and result_Quest:
        for row in result:
            # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            if(row.ID_Class_application == 1):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}\n", 
                    reply_markup=send_transfer)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}\n", 
                        reply_markup=send_transfer)
            if(row.ID_Class_application == 2):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод на другой формат работы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                                    f"<b>Инициатор:</b>  {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                    f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                                    f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                    f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                    f"<b>Дата подачи заявки:</b> {row.Date_application}", 
                        reply_markup=send_different)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод на другой формат работы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                                    f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                    f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                                    f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                    f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                    f"<b>Дата подачи заявки:</b> {row.Date_application}", 
                        reply_markup=send_different)
            if(row.ID_Class_application == 3):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на согласование заработной платы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                            f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                            f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}",
                        reply_markup=send_zp)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на согласование заработной платы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                            f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                            f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}",
                        reply_markup=send_zp)
            if(row.ID_Class_application == 4):
                await callback.message.answer(
                    f"<b>Заявка по общей форме</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                                f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                                f"<b>Дата подачи заявки:</b> {row.Date_application}",
                    reply_markup=send)
                  
        for row in result_Quest:
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            await callback.message.answer(
                f"<b>Вопрос</b>\n"
                f"<b>Номер вопроса:</b> {row.id}\n"
                            f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}",
                reply_markup=sendquiz)
    elif result and not result_Quest:
         for row in result:
            # Выведите сообщение с найденными данными и инлайн кнопкой
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            if(row.ID_Class_application == 1):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}\n", 
                    reply_markup=send_transfer)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата подачи заявки:</b> {row.Date_application}\n", 
                        reply_markup=send_transfer)
            if(row.ID_Class_application == 2):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод на другой формат работы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                                    f"<b>Инициатор:</b>  {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                    f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                                    f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                    f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                    f"<b>Дата подачи заявки:</b> {row.Date_application}", 
                        reply_markup=send_different)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод на другой формат работы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                                    f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                    f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                                    f"<b>Формат на данный момент:</b> {row.Current_work_format}\n"
                                    f"<b>Формат на переход:</b> {row.Future_work_format}\n"
                                    f"<b>Дата подачи заявки:</b> {row.Date_application}", 
                        reply_markup=send_different)
            if(row.ID_Class_application == 3):
                if(row.ID_Employee == 1):
                    result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                    result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на согласование заработной платы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n"
                            f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                            f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}",
                        reply_markup=send_zp)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на согласование заработной платы</b>\n"
                        f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n"
                            f"<b>Действующая сумма:</b> {row.Suggested_amount}.\n"
                            f"<b>Предлагаемая сумма:</b> {row.Current_amount}.\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}",
                        reply_markup=send_zp)
            if(row.ID_Class_application == 4):
                await callback.message.answer(
                    f"<b>Заявка по общей форме</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                                f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                                f"<b>Дата подачи заявки:</b> {row.Date_application}",
                    reply_markup=send)
    elif not result and result_Quest:
        for row in result_Quest:
            result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
            await callback.message.answer(
                f"<b>Вопрос</b>\n"
                f"<b>Номер вопроса:</b> {row.id}\n"
                            f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                            f"<b>Дата подачи заявки:</b> {row.Date_application}",
                reply_markup=sendquiz)
    else:
         await callback.message.answer(  
                    f"Новых задач на данный момент нет",
                    reply_markup=reply.hr
                    )
    # Закройте сессию
    session.close()

@user_private_router.message((F.text.lower() == "статистика")) 
async def transfer_cmd(message: types.Message, state:FSMContext):
    await state.update_data(request="статистика", reply_markup=reply.hr)
    await message.answer("Выберите период", reply_markup=сhoiceStatistic_keybord)
    

# Словарь с названиями месяцев на русском языке
month_names = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь',7: 'Июль', 8: 'Август', 9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь',12: 'Декабрь'}

# Вывод cтатистики по заявкам и вопросм на текущий месяц
@user_private_router.callback_query(F.data == "now_month")
async def go_app_general(callback: types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    # Получаем текущую дату и время
    now = datetime.now()
    month_name = month_names[now.month]
    # Создаем дату начала текущего месяца без времени
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_month_date_only = start_of_month.date()
    session = Session()
    text = (f"Статистика заявок на <b>{month_name} {now.year}</b> года\n")
    # Выберите данные из таблицы с использованием фильтрации
    count_Quest = session.query(table_question).filter(table_question.c.Date_actual_deadline != None, table_question.c.Date_actual_deadline >= start_of_month_date_only).order_by(table_question.c.Date_application).count()
    
    countGener_App = session.query(table_application).filter(table_application.c.Date_actual_deadline != None, table_application.c.Date_actual_deadline >= start_of_month_date_only, table_application.c.ID_Class_application == 4).count()
    text += f"Количеcтво заявок по общей форме: <b>{countGener_App if countGener_App != 0 else 'нет'}</b>\n"
    countTransf_App = session.query(table_application).filter(table_application.c.Date_actual_deadline != None, table_application.c.Date_actual_deadline >= start_of_month_date_only, table_application.c.ID_Class_application == 1).count()
    text += f"Количеcтво заявок на перевод: <b>{countTransf_App if countTransf_App != 0 else 'нет'}</b>\n"
    countZP_App = session.query(table_application).filter(table_application.c.Date_actual_deadline != None, table_application.c.Date_actual_deadline >= start_of_month_date_only, table_application.c.ID_Class_application == 3).count()
    text += f"Количеcтво заявок на перевод ЗП: <b>{countZP_App if countZP_App != 0 else 'нет'}</b>\n"
    countDiffFor_App = session.query(table_application).filter(table_application.c.Date_actual_deadline != None, table_application.c.Date_actual_deadline >= start_of_month_date_only, table_application.c.ID_Class_application == 2).count()
    text += f"Количеcтво заявок на перевод на другой формат работы: <b>{countDiffFor_App if countDiffFor_App != 0 else 'нет'}</b>\n\n"
    summApp = countGener_App + countTransf_App + countDiffFor_App + countZP_App
    text += f'Суммарное количество заявок: <b> {summApp} </b>\n'
    text += f"Количеcтво вопросов: <b>{count_Quest if count_Quest != 0 else '0'}</b>\n"
    # Если АктуальныйДедлайн есть, он в этом месяце и дата АктуальногоДедлайна БОЛЬШЕ ПлановогоДедлайна
    countOverdue_App = session.query(table_application).filter(table_application.c.Date_actual_deadline != None, table_application.c.Date_actual_deadline >= start_of_month_date_only, table_application.c.Date_planned_deadline < table_application.c.Date_actual_deadline).count()
    # Если АктуальныйДедлайн нет, ПлановыйДедлайн принадлежит выбранному промежутку и ПлановыйДедлайн меньше Сегодня
    countOverdue_App2 = session.query(table_application).filter(table_application.c.Date_actual_deadline == None, table_application.c.Date_planned_deadline != None, table_application.c.Date_planned_deadline < now).count()
    countSummOverdue_App = countOverdue_App + countOverdue_App2
    text += f"\nКоличество просроченных заявок: <b>{ countSummOverdue_App if countSummOverdue_App != 0 else 'нет'}</b> это <b>{((round(countSummOverdue_App / (countSummOverdue_App + summApp), 1)) * 100) if countSummOverdue_App + summApp > 0 else '0'}%</b> от общего количества\n"

    # Если АктуальныйДедлайн нет, ПлановыйДедлайн принадлежит выбранному промежутку и ПлановыйДедлайн меньше Сегодня
    countOverdue_Quest2 = session.query(table_question).filter(table_question.c.Date_actual_deadline == None, table_question.c.Date_planned_deadline != None, table_question.c.Date_planned_deadline < now).count() 
    countOverdue_Quest = session.query(table_question).filter(table_question.c.Date_actual_deadline != None, table_question.c.Date_actual_deadline >= start_of_month_date_only, table_question.c.Date_planned_deadline < table_question.c.Date_actual_deadline).count()
    countSumm_Quest = countOverdue_Quest + countOverdue_Quest2
    text += f"Количество просроченных вопросов: <b> { countSumm_Quest if countSumm_Quest != 0 else 'нет'}</b> это <b>{((round(countSumm_Quest / (count_Quest + countSumm_Quest), 1)) * 100) if count_Quest + countSumm_Quest > 0 else '0'}%</b> от общего количества"
    session.close()

    await callback.message.answer(text=text, reply_markup=reply.hr, parse_mode='HTML')

    
# Вывод cтатистики по заявкам и вопросм на выбранный период
@user_private_router.callback_query(F.data == "choice_month")
async def go_app_general(callback: types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await nav_cal_handler1(callback.message, state)

    
async def nav_cal_handler1(message: Message, state:FSMContext):
    await state.update_data(type_calendar = True)
    await bot.edit_message_reply_markup(
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=await SimpleCalendar(locale='ru').start_calendar()
    )     





@user_private_router.callback_query(F.data == 'click')
async def click_setdl(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    msg_id = call.message.message_id
    message_text = call.message.text

    pattern = r"Номер заявки:\s*(\d+)"

    # Применяем регулярное выражение к сообщению
    match = re.search(pattern, message_text)
    number_q = match.group(1)

    await state.update_data(id_mess = msg_id)
    await state.update_data(number_q = number_q)
    await call.message.answer(
        f"Оставить комментарий по <b>заявке {number_q}</b>", 
        reply_markup = inline.comment_request
    )
    await state.update_data(comm_quiz = False)


@user_private_router.callback_query(F.data == 'clickquiz')
async def click_setdlquiz(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    msg_id = call.message.message_id
    message_text = call.message.text

    # Регулярное выражение для поиска числа после строки "Номер заявки:"
    pattern = r"Номер вопроса:\s*(\d+)"

    # Применяем регулярное выражение к сообщению
    match = re.search(pattern, message_text)
    number_q = match.group(1)

    await state.update_data(id_mess = msg_id)
    await state.update_data(number_q = number_q)

    await call.message.answer(
        f"Оставить комментарий по <b>вопросу {number_q}</b>", 
        reply_markup = inline.comment_request
    )
    await state.update_data(comm_quiz = True)

@user_private_router.callback_query(F.data == 'no_comm')
async def no_comment(call: types.CallbackQuery, state: FSMContext):
    session = Session()
    msg_no_comm = call.message.message_id

    data = await state.get_data()
    number_q = data.get('number_q')
    msg_id = data.get('id_mess')
    comm_quiz = data.get('comm_quiz')
    today = date.today()
    id_info = session.query(table_application).filter(table_application.c.id == number_q).first()

    await call.answer(
        text = "Вы успешно выполнили задачу!",
        cache_time=30
    )
    await call.message.answer("Выберите категорию", reply_markup=reply.hr)

    await bot.delete_message(call.message.chat.id, msg_id)
    await bot.delete_message(call.message.chat.id, msg_no_comm)

    if comm_quiz == False:
        session.execute(
            table_application.update()
            .where(table_application.c.id == number_q)
            .values(Date_actual_deadline=today.strftime('%Y-%m-%d'))
        )
        id_info = session.query(table_application).filter(table_application.c.id == number_q).first()
        user_info = session.query(table_Employee).filter(table_Employee.c.id == id_info.ID_Initiator).first()
        text = f"<b>Сотрудник: </b>"
        if id_info.ID_Employee == 1 and id_info.ID_Class_application != 4:
            result_Division = session.query(table_division).filter(table_division.c.id == id_info.ID_Division).first()
            resultPositiong = session.query(table_position).filter(table_position.c.id == id_info.ID_Position).first()
            text += f"{id_info.Full_name_employee}, {result_Division.Division}, {resultPositiong.Position}\n"               
        elif id_info.ID_Employee != 1 and id_info.ID_Class_application != 4:
            employee_info = session.query(table_Employee).filter(table_Employee.c.id == id_info.ID_Employee).first()
            text += f"{employee_info.Surname} {employee_info.Name} {employee_info.Middle_name}, {employee_info.Division}, {employee_info.Position}\n"
                    
        if id_info.ID_Class_application == 4:
            await bot.send_message(user_info.id_telegram,
                                            f"<b>Заявка по общей форме</b> выполнена\n\n" 
                                            f"<b>Номер заявки: </b>{number_q}\n"
                                            f"<b>Суть обращения: </b>{id_info.Essence_question}\n"
                                            f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                            f"<b>Дата завершения:</b> {today.strftime('%Y-%m-%d')}", 
                                            parse_mode="HTML", reply_markup=reply.main)     
        elif id_info.ID_Class_application == 1:
            await bot.send_message(user_info.id_telegram,
                                            f"<b>Заявка на перевод</b> выполнена\n\n" 
                                            f"<b>Номер заявки: </b>{number_q}\n"
                                            f"{text}"
                                            f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                            f"<b>Дата завершения:</b> {today.strftime('%Y-%m-%d')}",  
                                            parse_mode="HTML", reply_markup=reply.main)     
        elif id_info.ID_Class_application == 2:
            await bot.send_message(user_info.id_telegram,
                                            f"<b>Заявка на перевод на другой формат работы</b> выполнена\n\n" 
                                            f"<b>Номер заявки: </b>{number_q}\n"
                                            f"{text}"
                                            f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                            f"<b>Дата завершения:</b> {today.strftime('%Y-%m-%d')}", 
                                            parse_mode="HTML", reply_markup=reply.main)     
        elif id_info.ID_Class_application == 3:
            await bot.send_message(user_info.id_telegram,
                                        f"<b>Заявка на согласование заработной платы</b> выполнена\n\n" 
                                        f"<b>Номер заявки: </b>{number_q}\n"
                                        f"{text}"
                                        f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                        f"<b>Дата завершения:</b> {today.strftime('%Y-%m-%d')}", 
                                        parse_mode="HTML", reply_markup=reply.main)   
    else:
        session.execute(
            table_question.update()
            .where(table_question.c.id == number_q)
            .values(Date_actual_deadline=today.strftime('%Y-%m-%d'))
        )
        id_quiz = session.query(table_question).filter(table_question.c.id == number_q).first()
        user_info = session.query(table_Employee).filter(table_Employee.c.id == id_quiz.ID_Initiator).first()
        await bot.send_message(user_info.id_telegram,
                                    f"<b>Вопрос</b> выполнен\n\n" 
                                    f"<b>Номер вопроса: </b>{number_q}\n"
                                    f"<b>Суть обращения: </b>{id_quiz.Essence_question}\n"
                                    f"<b>Дата подачи заявки:</b> {id_quiz.Date_application}\n"
                                    f"<b>Дата завершения:</b> {today.strftime('%Y-%m-%d')}", 
                                    parse_mode="HTML", reply_markup=reply.main)     
    await state.update_data(comm_quiz = False)
    session.commit()
    session.close()
    

@user_private_router.callback_query(F.data == 'yes_comm')
async def write_comm(call: types.CallbackQuery, state: FSMContext):
    msg_yes_comm = call.message.message_id
    await state.update_data(id_mess_state = msg_yes_comm)
    await call.message.answer(
            "Введите <b>комментарий</b>",
            reply_markup=reply.hr
    )
    await state.set_state(Applications.comment)

   
@user_private_router.message(Applications.comment)
async def cmd_comm(message: Message, state: FSMContext):
    await state.update_data(comment = message.text)
    data = await state.get_data()
    number_q = data.get('number_q')
    msg_yes = data.get('id_mess_state')
    comm_quiz = data.get('comm_quiz')

    msg_comm = message.message_id
    await state.update_data(id_mess_go = msg_comm)
     
    await bot.delete_message(message.chat.id, msg_yes)
    await message.delete()
    await bot.delete_message(message.chat.id, msg_yes+1)
    if comm_quiz == False:
        await message.answer(
            f"Комментарий по <b>заявке {number_q}:\n\n</b>"
            f"{message.text}", 
            reply_markup = inline.comment_push
        )
    else:
        await message.answer(
            f"Комментарий по <b>вопросу {number_q}:\n\n</b>"
            f"{message.text}", 
            reply_markup = inline.comment_push
        )

@user_private_router.callback_query(F.data == 'go_comm')
async def push_comm(call: types.CallbackQuery, state: FSMContext):
    session = Session()
    data = await state.get_data()
    number_q = data.get('number_q')
    comment = data.get('comment')
    msg_id = data.get('id_mess')
    msg_yes = data.get('id_mess_state')
    msg_go = data.get('id_mess_go')
    comm_quiz = data.get('comm_quiz')
    today = date.today()
    
    await call.answer(
        text = "Вы успешно выполнили задачу!",
        cache_time=30
    )
    await call.message.answer("Выберите категорию", reply_markup=reply.hr)

    await bot.delete_message(call.message.chat.id, msg_id)
    await bot.delete_message(call.message.chat.id, msg_go+1)
    if comm_quiz == False:
        session.execute(
        table_application.update()
        .where(table_application.c.id == number_q)
        .values(Date_actual_deadline=today.strftime('%Y-%m-%d'), Comment = comment)
        )

        id_info = session.query(table_application).filter(table_application.c.id == number_q).first()
        user_info = session.query(table_Employee).filter(table_Employee.c.id == id_info.ID_Initiator).first()
        text = f"<b>Сотрудник: </b>"
        if id_info.ID_Employee == 1 and id_info.ID_Class_application != 4:
            result_Division = session.query(table_division).filter(table_division.c.id == id_info.ID_Division).first()
            resultPositiong = session.query(table_position).filter(table_position.c.id == id_info.ID_Position).first()
            text += f"{id_info.Full_name_employee}, {result_Division.Division}, {resultPositiong.Position}\n"               
        elif id_info.ID_Employee != 1 and id_info.ID_Class_application != 4:
            employee_info = session.query(table_Employee).filter(table_Employee.c.id == id_info.ID_Employee).first()
            text += f"{employee_info.Surname} {employee_info.Name} {employee_info.Middle_name}, {employee_info.Division}, {employee_info.Position}\n"
                    
        if id_info.ID_Class_application == 4:
            await bot.send_message(user_info.id_telegram,
                                            f"<b>Заявка по общей форме</b> выполнена\n\n" 
                                            f"<b>Номер заявки: </b>{number_q}\n"
                                            f"<b>Суть обращения: </b>{id_info.Essence_question}\n"
                                            f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                            f"<b>Дата завершения:</b> {today.strftime('%Y-%m-%d')}\n\n"
                                            f"📌<b>Комментарий:</b> {comment}", 
                                            parse_mode="HTML", reply_markup=reply.main)     
        elif id_info.ID_Class_application == 1:
            await bot.send_message(user_info.id_telegram,
                                            f"<b>Заявка на перевод</b> выполнена\n\n" 
                                            f"<b>Номер заявки: </b>{number_q}\n"
                                            f"{text}"
                                            f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                            f"<b>Дата завершения:</b> {today.strftime('%Y-%m-%d')}\n\n"
                                            f"📌<b>Комментарий:</b> {comment}",  
                                            parse_mode="HTML", reply_markup=reply.main)     
        elif id_info.ID_Class_application == 2:
            await bot.send_message(user_info.id_telegram,
                                            f"<b>Заявка на перевод на другой формат работы</b> выполнена\n\n" 
                                            f"<b>Номер заявки: </b>{number_q}\n"
                                            f"{text}"
                                            f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                            f"<b>Дата завершения:</b> {today.strftime('%Y-%m-%d')}\n\n"
                                            f"📌<b>Комментарий:</b> {comment}",  
                                            parse_mode="HTML", reply_markup=reply.main)     
        elif id_info.ID_Class_application == 3:
            await bot.send_message(user_info.id_telegram,
                                            f"<b>Заявка на согласование заработной платы</b> выполнена\n\n" 
                                            f"<b>Номер заявки: </b>{number_q}\n"
                                            f"{text}"
                                            f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                            f"<b>Дата завершения:</b> {today.strftime('%Y-%m-%d')}\n\n"
                                            f"📌<b>Комментарий:</b> {comment}",  
                                            parse_mode="HTML", reply_markup=reply.main) 
    else:
        session.execute(
            table_question.update()
            .where(table_question.c.id == number_q)
            .values(Date_actual_deadline=today.strftime('%Y-%m-%d'), Comment = comment)
        )
        id_quiz = session.query(table_question).filter(table_question.c.id == number_q).first()
        user_info = session.query(table_Employee).filter(table_Employee.c.id == id_quiz.ID_Initiator).first()
        await bot.send_message(user_info.id_telegram,
                                    f"<b>Вопрос</b> выполнен\n\n" 
                                    f"<b>Номер вопроса: </b>{number_q}\n"
                                    f"<b>Суть обращения: </b>{id_quiz.Essence_question}\n"
                                    f"<b>Дата подачи заявки:</b> {id_quiz.Date_application}\n"
                                    f"<b>Дата завершения:</b> {today.strftime('%Y-%m-%d')}\n\n"
                                    f"📌<b>Комментарий:</b> {comment}",  
                                    parse_mode="HTML", reply_markup=reply.main)     
    await state.update_data(comm_quiz = False)
    session.commit()
    session.close()

@user_private_router.callback_query(F.data == 'back_comm')
async def stop_comm(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_go = data.get('id_mess_go')

    await call.message.answer("Выберите категорию", reply_markup=reply.hr)

    await state.update_data(comment = "")
    await state.update_data(number_q = "")

    await bot.delete_message(call.message.chat.id, msg_go+1)