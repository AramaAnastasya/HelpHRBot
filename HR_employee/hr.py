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
from datetime import date
from sqlalchemy import insert
import re
from HR_employee.keyboards.inline import get_callback_btns, sorted_keybordFirst, sorted_keybordSecond, sortedAct_keybordFirst, sortedAct_keybordSecond
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
    print('Общая подкатегория1')
    await callback.message.delete_reply_markup()
    await bot.send_message(callback.from_user.id, "Выберите тип заявки для вывода актуальных задач", reply_markup=sortedAct_keybordSecond, parse_mode="HTML")

# Выводзаявок актуальных на перевод
@user_private_router.callback_query(F.data == "sort_app_transf1")
async def go_app_transf(callback: types.CallbackQuery, bot: Bot, state:FSMContext):
    print('TRANS1')
    await state.update_data(unwrap = True)
    await callback.message.edit_reply_markup()
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
    await callback.message.delete_reply_markup()
    await state.update_data(unwrap = True)
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
    await callback.message.delete_reply_markup()
    await state.update_data(unwrap = True)
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
    await callback.message.delete_reply_markup()
    await state.update_data(unwrap = True)
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
    await callback.message.delete_reply_markup()
    await state.update_data(unwrap = True)
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
    await callback.message.delete_reply_markup()
    await state.update_data(unwrap = True)
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
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline != None, table_application.c.Date_actual_deadline == None).order_by(table_application.c.Date_planned_deadline).all()
   
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
    result_Quest = session.query(table_question).filter(table_question.c.Date_planned_deadline != None, table_question.c.Date_actual_deadline == None).order_by(table_question.c.Date_planned_deadline).all()
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
    # Закройте сессию
    session.close()

   
    

@user_private_router.message((F.text.lower() == "новые задачи")) 
async def transfer_cmd23(message: types.Message, state:FSMContext):
    await state.update_data(chat_id=message.from_user.id, request="Новые задачи", reply_markup=reply.hr)
    await message.answer("Выберите категорию", reply_markup=sorted_keybordFirst)


# Вывод  inline-клавиатуры для сортировки заявок 
@user_private_router.callback_query(F.data == "sort_app")
async def sort_applic(callback: types.CallbackQuery, state:FSMContext):
    print('Общая подкатегория')
    await callback.message.delete_reply_markup()
    await bot.send_message(callback.from_user.id, "Выберите тип заявки для вывода новых задач", reply_markup=sorted_keybordSecond, parse_mode="HTML")

# Вывод заявок на перевод
@user_private_router.callback_query(F.data == "sort_app_transf")
async def go_app_transf(callback: types.CallbackQuery, bot: Bot, state:FSMContext):
    print('TRANS')
    await state.update_data(unwrap = False)
    await callback.message.edit_reply_markup()
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
    await callback.message.delete_reply_markup()
    await state.update_data(unwrap = False)
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
                        f"<b>Дата:</b> {row.Date_application}",
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
                        f"<b>Дата:</b> {row.Date_application}",
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
    await callback.message.delete_reply_markup()
    await state.update_data(unwrap = False)
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
                                f"<b>Дата:</b> {row.Date_application}", 
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
                                f"<b>Дата:</b> {row.Date_application}", 
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
    await callback.message.delete_reply_markup()
    await state.update_data(unwrap = False)
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
                            f"<b>Дата:</b> {row.Date_application}",
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
    await callback.message.delete_reply_markup()
    await state.update_data(unwrap = False)
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
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата:</b> {row.Date_application}\n", 
                        reply_markup=send_transfer)
                else:
                    result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                    await callback.message.answer(
                        f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                        f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата</b>: {row.Date_application}\n", 
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
                                    f"<b>Дата:</b> {row.Date_application}", 
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
                                    f"<b>Дата:</b> {row.Date_application}", 
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
                            f"<b>Дата:</b> {row.Date_application}",
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
                            f"<b>Дата:</b> {row.Date_application}",
                    reply_markup=send_zp)
            if(row.ID_Class_application == 4):
                await callback.message.answer(
                    f"<b>Заявка по общей форме</b>\n"
                    f"<b>Номер заявки:</b> {row.id}\n"
                                f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                                f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                                f"<b>Дата:</b> {row.Date_application}",
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
    await callback.message.delete_reply_markup()
    await state.update_data(unwrap = False)
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
                            f"<b>Дата:</b> {row.Date_application}",
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
    
    # Получите сессию для работы с базой данных
    session = Session()
    # Выберите данные из таблицы с использованием фильтрации
    result = session.query(table_application).filter(table_application.c.Date_planned_deadline == None).order_by(table_application.c.Date_application).all()
    for row in result:
        # Выведите сообщение с найденными данными и инлайн кнопкой
        result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
        if(row.ID_Class_application == 1):
            if(row.ID_Employee == 1):
                result_Division = session.query(table_division).filter(row.ID_Division == table_division.c.id).first()
                result_Position = session.query(table_position).filter(row.ID_Position == table_position.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                    f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {row.Full_name_employee}, {result_Division.Division}, {result_Position.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата:</b> {row.Date_application}\n", 
                   reply_markup=send_transfer)
            else:
                result_Employee = session.query(table_Employee).filter(row.ID_Employee == table_Employee.c.id).first()
                await callback.message.answer(
                    f"<b>Заявка на перевод</b>\n<b>Номер заявки:</b> {row.id}\n"
                    f"<b>Инициатор:</b> {result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n<b>Сотрудник:</b> {result_Employee.Surname} {result_Employee.Name} {result_Employee.Middle_name}, {result_Employee.Division}, {result_Employee.Position}\n<b>Дата конца Испытательного Срока:</b> {row.End_date_IS}.\n<b>Дата</b>: {row.Date_application}\n", 
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
                                f"<b>Дата:</b> {row.Date_application}", 
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
                                f"<b>Дата:</b> {row.Date_application}", 
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
                         f"<b>Дата:</b> {row.Date_application}",
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
                         f"<b>Дата:</b> {row.Date_application}",
                    reply_markup=send_zp)
        if(row.ID_Class_application == 4):
            await callback.message.answer(
                f"<b>Заявка по общей форме</b>\n"
                f"<b>Номер заявки:</b> {row.id}\n"
                            f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                            f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                            f"<b>Дата:</b> {row.Date_application}",
                reply_markup=send)
            
    result_Quest = session.query(table_question).filter(table_question.c.Date_planned_deadline == None).order_by(table_question.c.Date_application).all()
    for row in result_Quest:
        result_Initor = session.query(table_Employee).filter(row.ID_Initiator == table_Employee.c.id).first()
        await callback.message.answer(
            f"<b>Вопрос</b>\n"
            f"<b>Номер вопроса:</b> {row.id}\n"
                        f"<b>Инициатор: </b>{result_Initor.Surname} {result_Initor.Name[0]}.{result_Initor.Middle_name[0]}.\n"
                        f"<b>Суть обращения: </b>{ row.Essence_question}\n"
                        f"<b>Дата:</b> {row.Date_application}",
            reply_markup=sendquiz)

    
    # Закройте сессию
    session.close()

@user_private_router.message((F.text.lower() == "статистика")) 
async def transfer_cmd(message: types.Message, state:FSMContext):
    await state.update_data(request="статистика")
    await message.answer(
        "узнать статистику",
        reply_markup=reply.hr
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

    print(msg_id)
    print(msg_no_comm)

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
    print(f"введите комментарий {msg_yes_comm}")
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
    print(f"введите комментарий {msg_yes}")
     
    print(message.chat.id)
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
    print(f"комментарий по заявке {msg_comm}")

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

    print(f"id заявки {msg_id}")
    print(msg_yes)
    print(msg_go)
    print(comm_quiz)
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
    number_q = data.get('number_q')
    comment = data.get('comment')
    msg_id = data.get('id_mess')
    msg_yes = data.get('id_mess_state')
    msg_go = data.get('id_mess_go')

    print(f"id заявки {msg_id}")
    print(msg_yes)
    print(msg_go)
    await call.message.answer("Выберите категорию", reply_markup=reply.hr)

    await state.update_data(comment = "")
    await state.update_data(number_q = "")

    await bot.delete_message(call.message.chat.id, msg_go+1)