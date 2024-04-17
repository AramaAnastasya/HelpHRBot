import logging
import asyncio
import sys
from datetime import datetime, timedelta, date
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
import re
from HR_employee.keyboards.inline import set_deadline_tmrw, set_deadline_tmrw_quiz
from HR_employee.hr import nav_cal_handler1


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
    msg_id = call.message.message_id
    message_text = call.message.text

    pattern = r"Номер заявки:\s*(\d+)"
    
    match = re.search(pattern, message_text)
    number_q = match.group(1)
    await state.update_data(id_mess = msg_id)
    await state.update_data(number_q = number_q)
    await state.update_data(type_quiz = False)
    await nav_cal_handler(call.message, state) 


async def nav_cal_handler(message: Message, state: FSMContext):
    await state.update_data(type_calendar = False)
    data = await state.get_data()
    type_calendar = data.get('type_calendar')
    await bot.edit_message_reply_markup(
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=await SimpleCalendar(locale='ru').start_calendar()
    )    


@user_private_router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, bot:Bot, callback_data: CallbackData, state: FSMContext):
    
    session = Session()
    data = await state.get_data()
    type_calendar = data.get('type_calendar')
    if type_calendar == True:
        data = await state.get_data()
        start_date = data.get('start_date')
        start_dat = data.get('startSave_date')

        now = datetime.now()
        calendar = SimpleCalendar(
            locale=await get_user_locale(callback_query.from_user), show_alerts=True
        )
        calendar.set_dates_range(datetime(2024, 1, 1), datetime(int(now.strftime('%Y'))+1, 12, 31))
        selected, date = await calendar.process_selection(callback_query, callback_data)
        if selected:
            if start_date == None:
                await state.update_data(start_date = date)
                await state.update_data(startSave_date = date)
                await nav_cal_handler1(callback_query.message, state)
            else:
            # Здесь можно установить состояние для даты окончания вручную
                await state.update_data(start_date = None)
                start_dat = data.get('startSave_date')
                if start_dat != None:
                    session = Session()
                    text = f"Статистика заявок на период с <b>{start_dat.strftime('%d-%m-%Y')}</b> по <b>{date.strftime('%d-%m-%Y')}</b>\n"
                    # Выберите данные из таблицы с использованием фильтрации
                    count_Quest = session.query(question).filter(question.c.Date_actual_deadline != None, question.c.Date_actual_deadline >= start_dat, question.c.Date_actual_deadline <= date).order_by(question.c.Date_application).count()
                    
                    countGener_App = session.query(application).filter(application.c.Date_actual_deadline != None, application.c.Date_actual_deadline >= start_dat, application.c.Date_actual_deadline <= date, application.c.ID_Class_application == 4).count()
                    text += f"Количеcтво заявок по общей форме: <b>{countGener_App if countGener_App != 0 else 'нет'}</b>\n"
                    countTransf_App = session.query(application).filter(application.c.Date_actual_deadline != None, application.c.Date_actual_deadline >= start_dat, application.c.Date_actual_deadline <= date, application.c.ID_Class_application == 1).count()
                    text += f"Количеcтво заявок на перевод: <b>{countTransf_App if countTransf_App != 0 else 'нет'}</b>\n"
                    countZP_App = session.query(application).filter(application.c.Date_actual_deadline != None, application.c.Date_actual_deadline >= start_dat, application.c.Date_actual_deadline <= date, application.c.ID_Class_application == 3).count()
                    text += f"Количеcтво заявок на перевод ЗП: <b>{countZP_App if countZP_App != 0 else 'нет'}</b>\n"
                    countDiffFor_App = session.query(application).filter(application.c.Date_actual_deadline != None, application.c.Date_actual_deadline >= start_dat, application.c.Date_actual_deadline <= date, application.c.ID_Class_application == 2).count()
                    text += f"Количеcтво заявок на перевод на другой формат работы: <b>{countDiffFor_App if countDiffFor_App != 0 else 'нет'}</b>\n\n"
                    summApp = countGener_App + countTransf_App + countDiffFor_App + countZP_App
                    text += f'Суммарное количество заявок: <b> {summApp} </b>\n'
                    text += f"Количеcтво вопросов: <b>{count_Quest if count_Quest != 0 else '0'}</b>\n"
                    
                    # Если АктуальныйДедлайн есть, он принадлежит выбранному промежутку и дата АктуальногоДедлайна БОЛЬШЕ ПлановогоДедлайна
                    countOverdue_App = session.query(application).filter(application.c.Date_actual_deadline != None, application.c.Date_actual_deadline >= start_dat, application.c.Date_actual_deadline <= date,application.c.Date_planned_deadline != None, application.c.Date_actual_deadline > application.c.Date_planned_deadline).count()
                    # Если АктуальныйДедлайн нет, ПлановыйДедлайн принадлежит выбранному промежутку
                    countOverdue_App2 = session.query(application).filter(application.c.Date_actual_deadline == None, application.c.Date_planned_deadline <= date,application.c.Date_planned_deadline != None, application.c.Date_planned_deadline < now).count()
                    countSummOverdue_App = countOverdue_App + countOverdue_App2

                    text += f"\nКоличество просроченных заявок: <b>{ countSummOverdue_App if countSummOverdue_App != 0 else 'нет'}</b> это <b>{((round(countSummOverdue_App / (countSummOverdue_App + summApp), 1)) * 100) if countSummOverdue_App + summApp > 0 else '0'}%</b> от общего количества\n"
                    
                    # Если АктуальныйДедлайн есть, он принадлежит выбранному промежутку и дата АктуальногоДедлайна БОЛЬШЕ ПлановогоДедлайна
                    countOverdue_Quest = session.query(question).filter(question.c.Date_actual_deadline != None, question.c.Date_actual_deadline >= start_dat, question.c.Date_actual_deadline <= date, question.c.Date_actual_deadline > question.c.Date_planned_deadline ).count()
                    # Если АктуальныйДедлайн нет, ПлановыйДедлайн принадлежит выбранному промежутку
                    countOverdue_Quest2 = session.query(question).filter(question.c.Date_actual_deadline == None, question.c.Date_planned_deadline != None, question.c.Date_planned_deadline <= date, question.c.Date_planned_deadline < now).count() 
                    countSumm_Quest = countOverdue_Quest + countOverdue_Quest2
                    text += f"Количество просроченных вопросов: <b> { countSumm_Quest if countSumm_Quest != 0 else 'нет'}</b> это <b>{((round(countSumm_Quest / (count_Quest + countSumm_Quest), 1)) * 100) if count_Quest + countSumm_Quest > 0 else '0'}%</b> от общего количества"
                    session.close()
                    await callback_query.message.answer(text=text, reply_markup=reply.hr, parse_mode='HTML')
                    await state.update_data(type_calendar = False)

    else:
        msg_id = data.get('id_mess')
        number_q = data.get('number_q')
        type_quiz = data.get('type_quiz')
        if type_quiz == False:
            id_info = session.query(application).filter(application.c.id == number_q).first()
            user_info = session.query(table).filter(table.c.id == id_info.ID_Initiator).first()
        else:
            id_quiz = session.query(question).filter(question.c.id == number_q).first() 
            user_info_quiz = session.query(table).filter(table.c.id == id_quiz.ID_Initiator).first()

        text_hr = ""
        text_init = ""
        now = datetime.now()

        chat_id = callback_query.message.chat.id
        calendar = SimpleCalendar(
            locale=await get_user_locale(callback_query.from_user), show_alerts=True
        )
        calendar.set_dates_range(datetime.now(), datetime(int(now.strftime('%Y'))+1, 12, 31))

        selected, date_c = await calendar.process_selection(callback_query, callback_data)
        if selected:        
            if date_c.weekday() == 5 or date_c.weekday() == 6:  # Проверяем, является ли выбранная дата субботой (5) или воскресеньем (6)
                    await callback_query.answer(
                            text = "Выберите рабочий день",
                            cache_time=30
                        )
                    await nav_cal_handler(callback_query.message, state)
                    return                
            else:              
                if type_quiz == True and user_info_quiz.id_telegram != None:
                    if id_quiz.Date_planned_deadline != None:
                        text_hr = f'Вы изменили дедлайн заявки номер {number_q} на <b>{date_c.strftime("%d-%m-%Y")}</b>'
                        text_init = f"⏰ Изменен дедлайн" 
                    elif id_quiz.Date_planned_deadline == None:
                        text_hr = f'Вы установили дедлайн заявки номер {number_q} на <b>{date_c.strftime("%d-%m-%Y")}</b>'
                        text_init = f"⏰ Установлен дедлайн" 
                    await callback_query.message.answer(
                        text_hr,
                    ) 
                    # Текущая дата
                    current_date = datetime.now()
                    # Выбранная дата
                    selected_date = date_c
                    # Разница между двумя датами              
                    difference = selected_date - current_date

                    # Середина срока
                    middle_date = current_date + timedelta(days=difference.days // 2)

                    if middle_date.weekday() == 5:
                        middle_date = middle_date + timedelta(days=2)
                    elif middle_date.weekday() == 6:
                        middle_date = middle_date + timedelta(days=1)

                    session.execute(
                        update(question)
                        .where(question.c.id == number_q)
                        .values(Date_planned_deadline = date_c.strftime('%Y-%m-%d'), Middle_deadline = middle_date)
                    )
                    session.commit()
                
                    await bot.delete_message(chat_id=callback_query.from_user.id, 
                                        message_id=msg_id)
                    
                    id_quiz = session.query(question).filter(question.c.id == number_q).first()
                    await bot.send_message(user_info_quiz.id_telegram,
                                            f"{text_init} по <b>общему вопросу</b>\n\n" 
                                            f"<b>Номер вопроса: </b>{number_q}\n"
                                            f"<b>Суть обращения: </b>{id_quiz.Essence_question}\n"
                                            f"<b>Дата подачи заявки:</b> {id_quiz.Date_application}\n"
                                            f"<b>Дата дедлайна:</b> {id_quiz.Date_planned_deadline}", 
                                            parse_mode="HTML", reply_markup=reply.main)  
                    await send_message_time(bot, state)
                elif type_quiz == False and user_info.id_telegram != None:
                    if id_info.Date_planned_deadline != None:
                        text_hr = f'Вы изменили дедлайн заявки номер {number_q} на <b>{date_c.strftime("%d-%m-%Y")}</b>'
                        text_init = f"Изменен дедлайн" 
                    elif id_info.Date_planned_deadline == None:
                        text_hr = f'Вы установили дедлайн заявки номер {number_q} на <b>{date_c.strftime("%d-%m-%Y")}</b>'
                        text_init = f"Установлен дедлайн" 
                    await callback_query.message.answer(
                        text_hr,
                    ) 
                    # Текущая дата
                    current_date = datetime.now()
                    # Выбранная дата
                    selected_date = date_c
                    # Разница между двумя датами              
                    difference = selected_date - current_date

                    # Середина срока
                    middle_date = current_date + timedelta(days=difference.days // 2)

                    if middle_date.weekday() == 5:
                        middle_date = middle_date + timedelta(days=2)
                    elif middle_date.weekday() == 6:
                        middle_date = middle_date + timedelta(days=1)

                    session.execute(
                        update(application)
                        .where(application.c.id == number_q)
                        .values(Date_planned_deadline = date_c.strftime('%Y-%m-%d'), Middle_deadline = middle_date)
                    )
                    session.commit()
                
                    await bot.delete_message(chat_id=callback_query.from_user.id, 
                                        message_id=msg_id)
                    
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
                                            f"{text_init} по <b>заявке по общей форме</b>\n\n" 
                                            f"<b>Номер заявки: </b>{number_q}\n"
                                            f"<b>Суть обращения: </b>{id_info.Essence_question}\n"
                                            f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                            f"<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}", 
                                            parse_mode="HTML", reply_markup=reply.main)     
                    elif id_info.ID_Class_application == 1:
                        await bot.send_message(user_info.id_telegram,
                                            f"{text_init} по <b>заявке на перевод</b>\n\n" 
                                            f"<b>Номер заявки: </b>{number_q}\n"
                                            f"{text}"
                                            f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                            f"<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}", 
                                            parse_mode="HTML", reply_markup=reply.main)     
                    elif id_info.ID_Class_application == 2:
                        await bot.send_message(user_info.id_telegram,
                                            f"{text_init} по <b>заявке на перевод на другой формат работы</b>\n\n" 
                                            f"<b>Номер заявки: </b>{number_q}\n"
                                            f"{text}"
                                            f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                            f"<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}", 
                                            parse_mode="HTML", reply_markup=reply.main)     
                    elif id_info.ID_Class_application == 3:
                        await bot.send_message(user_info.id_telegram,
                                            f"{text_init} по <b>заявке на согласование заработной платы</b>\n\n" 
                                            f"<b>Номер заявки: </b>{number_q}\n"
                                            f"{text}"
                                            f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                            f"<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}", 
                                            parse_mode="HTML", reply_markup=reply.main)   
                        
                    await send_message_time(bot, state)
                else:
                    await bot.send_message(chat_id, "Ошибка в формировании заявки")
                    await bot.send_message(chat_id, "Инициатор не авторизирован", reply_markup=reply.hr)

            if (type_quiz == False and user_info.id_telegram != None) or (type_quiz == True and user_info_quiz.id_telegram != None):
                if type_quiz == False:
                    id_info = session.query(application).filter(application.c.id == number_q).first()
                    user_info = session.query(table).filter(table.c.id == id_info.ID_Initiator).first()
                    current_amount = id_info.Current_amount
                    suggest_amount = id_info.Suggested_amount

                    date_info = id_info.Date_application
                    number_init = id_info.ID_Initiator
                    deadline_prob = id_info.End_date_IS
                    essence_que = id_info.Essence_question

                    placenow_info = id_info.Current_work_format
                    placewill_info = id_info.Future_work_format

                    id_empl = id_info.ID_Employee
                    empl_id = session.query(table).filter(table.c.id == id_empl).first()
                    if id_info.Full_name_employee:
                        fullname_employee = id_info.Full_name_employee
                    else:
                        fullname_employee = f"{empl_id.Surname} {empl_id.Name} {empl_id.Middle_name}"

                    if id_info.ID_Division:
                        id_divis = id_info.ID_Division
                        divis_id = session.query(table_division).filter(table_division.c.id == id_divis).first()
                        divis_info = divis_id.Division
                    else:
                        divis_info = empl_id.Division


                    if id_info.ID_Position:
                        id_post = id_info.ID_Position
                        post_id = session.query(table_position).filter(table_position.c.id == id_post).first()
                        post_info = post_id.Position
                    else:
                        post_info = empl_id.Position


                    init_info = session.query(table).filter(table.c.id == number_init).first()
                    
                    surname_init = init_info.Surname
                    name_init = init_info.Name
                    middle_init = init_info.Middle_name
                else:
                    id_quiz = session.query(question).filter(question.c.id == number_q).first() 
                    user_info_quiz = session.query(table).filter(table.c.id == id_quiz.ID_Initiator).first()


                

                if type_quiz == False:
                    target_date = id_info.Date_planned_deadline
                    day_before = target_date - timedelta(days=1)
                
                    if day_before.weekday() == 5:
                        day_before = day_before - timedelta(days=1)
                    elif day_before.weekday() == 6:
                        day_before = day_before - timedelta(days=2)
                    # Добавляем к целевой дате один день и устанавливаем время на 10:00 утра
                    target_datetime = datetime(day_before.year, day_before.month, day_before.day, 10, 0 , 0)
                    # Вычисляем разницу между текущим временем и целевым временем
                    delta = target_datetime - datetime.now()
                    if id_info.ID_Class_application == 1 and id_info.Date_actual_deadline == None:
                        if delta.total_seconds() > 0:
                            await asyncio.sleep(delta.total_seconds())
                        id_info = session.query(application).filter(application.c.id == number_q).first()
                        date_c = id_info.Date_planned_deadline
                        date_obj = date_c.strftime('%Y-%m-%d')
                        if datetime.now().date().strftime('%Y-%m-%d') == date_obj:    
                            if id_info.Date_actual_deadline == None:
                                await bot.send_message(chat_id,
                                                    text =  
                                                    f"❗<b>Завтра завершится дедлайн</b>❗\n"
                                                    f"<b>Заявка на перевод</b>\n"
                                                    f"<b>Номер заявки: </b>{number_q}\n"
                                                    f"<b>Инициатор:</b> {surname_init} {name_init[0]}. {middle_init[0]}.\n"
                                                    f"<b>Сотрудник:</b> {fullname_employee}, {divis_info}, {post_info}\n"
                                                    f"<b>Дата конца Испытательного Срока:</b> {deadline_prob}.\n"
                                                    f"<b>Дата подачи заявки:</b> {date_info}\n"
                                                    f"<b>Дата планового дедлайна:</b> {id_info.Date_planned_deadline}", 
                                                    parse_mode="HTML", reply_markup=set_deadline_tmrw)

                    elif id_info.ID_Class_application == 2 and id_info.Date_actual_deadline == None:
                        if delta.total_seconds() > 0:
                            await asyncio.sleep(delta.total_seconds())
                        id_info = session.query(application).filter(application.c.id == number_q).first()
                        date_c = id_info.Date_planned_deadline
                        date_obj = date_c.strftime('%Y-%m-%d')
                        if datetime.now().date().strftime('%Y-%m-%d') == date_obj:    
                            if id_info.Date_actual_deadline == None:
                                await bot.send_message(chat_id,
                                                    text=   
                                                    f"❗<b>Завтра завершится дедлайн</b>❗\n"                                
                                                    f"<b>Заявка на перевод на другой формат работы</b>\n"
                                                    f"<b>Номер заявки: </b>{number_q}\n"
                                                    f"<b>Инициатор:</b> {surname_init} {name_init[0]}. {middle_init[0]}.\n"
                                                    f"<b>Сотрудник:</b> {fullname_employee}\n"
                                                    f"<b>Формат на данный момент:</b> {placenow_info}\n"
                                                    f"<b>Формат на переход:</b> {placewill_info}\n"
                                                    f"<b>Дата: {date_info}</b>\n"
                                                    f"<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}", 
                                                    parse_mode="HTML", reply_markup=set_deadline_tmrw)   
                    elif id_info.ID_Class_application == 3 and id_info.Date_actual_deadline == None:
                        if delta.total_seconds() > 0:
                            await asyncio.sleep(delta.total_seconds())
                        id_info = session.query(application).filter(application.c.id == number_q).first()
                        date_c = id_info.Date_planned_deadline
                        date_obj = date_c.strftime('%Y-%m-%d')
                        if datetime.now().date().strftime('%Y-%m-%d') == date_obj:    
                            if id_info.Date_actual_deadline == None:
                                await bot.send_message(chat_id,
                                                    text=     
                                                    f"❗<b>Завтра завершится дедлайн</b>❗\n"                              
                                                    f"<b>Заявка на согласование заработной платы</b>\n"
                                                    f"<b>Номер заявки: </b>{number_q}\n"
                                                    f"<b>Инициатор: </b>{surname_init} {name_init[0]}. {middle_init[0]}.\n"
                                                    f"<b>Сотрудник:</b> {fullname_employee}\n"
                                                    f"<b>Действующая сумма:</b> {current_amount}\n"
                                                    f"<b>Предлагаемая сумма:</b> {suggest_amount}\n"
                                                    f"<b>Дата подачи заявки:</b> {date_info}\n"
                                                    f"<b>Дата планового дедлайна:</b> {id_info.Date_planned_deadline}", 
                                                    parse_mode="HTML", reply_markup=set_deadline_tmrw)
                    elif id_info.ID_Class_application == 4 and id_info.Date_actual_deadline == None:
                        if delta.total_seconds() > 0:
                            await asyncio.sleep(delta.total_seconds())
                        id_info = session.query(application).filter(application.c.id == number_q).first()
                        date_c = id_info.Date_planned_deadline
                        date_obj = date_c.strftime('%Y-%m-%d')
                        if datetime.now().date().strftime('%Y-%m-%d') == date_obj:                            
                            if id_info.Date_actual_deadline == None:
                                await bot.send_message(chat_id,
                                                    text=      
                                                    f"❗<b>Завтра завершится дедлайн</b>❗\n"                             
                                                    f"<b>Заявка по общей форме</b>\n"
                                                    f"<b>Номер заявки: </b>{number_q}\n"
                                                    f"<b>Инициатор: </b>{surname_init} {name_init[0]}. {middle_init[0]}.\n"
                                                    f"<b>Суть обращения: </b> {essence_que}\n"
                                                    f"<b>Дата подачи заявки:</b>{date_info}\n"
                                                    f"<b>Дата планового дедлайна:</b> {id_info.Date_planned_deadline}", 
                                                    parse_mode="HTML", reply_markup=set_deadline_tmrw)
                else:
                    target_date = id_quiz.Date_planned_deadline
                    day_before = target_date - timedelta(days=1)

                    if day_before.weekday() == 5:
                        day_before = day_before - timedelta(days=1)
                    elif day_before.weekday() == 6:
                        day_before = day_before - timedelta(days=2)

                    # Добавляем к целевой дате один день и устанавливаем время на 10:00 утра
                    target_datetime = datetime(target_date.year, target_date.month, target_date.day, 10, 0, 0)

                    # Вычисляем разницу между текущим временем и целевым временем
                    delta = target_datetime - datetime.now()
                    user_info = session.query(table).filter(table.c.id == id_quiz.ID_Initiator).first()
                    if delta.total_seconds() > 0 and id_quiz.Date_actual_deadline == None:
                        await asyncio.sleep(delta.total_seconds())
                    id_quiz = session.query(question).filter(question.c.id == number_q).first()
                    date_c = id_quiz.Date_planned_deadline
                    date_obj = date_c.strftime('%Y-%m-%d')
                    if datetime.now().date().strftime('%Y-%m-%d') == date_obj:
                        if id_quiz.Date_actual_deadline == None:
                            essense_que_quiz = id_quiz.Essence_question
                            await bot.send_message(chat_id,
                                                    f"❗<b>Завтра завершится дедлайн</b>❗\n"                              
                                                    f"<b>Вопрос</b>\n"
                                                    f"<b>Номер вопроса: </b>{number_q}\n"
                                                    f"<b>Инициатор: </b>{user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
                                                    f"<b>Суть вопроса: </b>{essense_que_quiz}\n"
                                                    f"<b>Дата подачи заявки:</b> {id_quiz.Date_application}\n"
                                                    f"<b>Дата планового дедлайна:</b> {id_quiz.Date_planned_deadline}", 
                                                    parse_mode="HTML", reply_markup=set_deadline_tmrw_quiz)  
                            await state.update_data(type_quiz = False)
                


async def send_message_time(bot:Bot, state: FSMContext):
    session = Session()
    existing_record_HR = session.query(table).filter(table.c.Surname == "Дрыгин", table.c.Name == "Андрей", table.c.Middle_name == "Владимирович").first() 
    data = await state.get_data()
    type_quiz = data.get('type_quiz')
    number_q = data.get('number_q')

    if type_quiz == True:
        id_quiz = session.query(question).filter(question.c.id == number_q).first()
        target_date = id_quiz.Middle_deadline
        target_datetime = datetime(target_date.year, target_date.month, target_date.day, 10, 0, 0)
        delta = target_datetime - datetime.now()

        if delta.total_seconds() > 0 and id_quiz.Date_actual_deadline == None:    
            await asyncio.sleep(delta.total_seconds()) 
        id_quiz = session.query(question).filter(question.c.id == number_q).first()
        date_c = id_quiz.Middle_deadline
        date_obj = date_c.strftime('%Y-%m-%d')
        if datetime.now().date().strftime('%Y-%m-%d') == date_obj:                
            if id_quiz.Date_actual_deadline == None:
                user_info = session.query(table).filter(table.c.id == id_quiz.ID_Initiator).first()
                await bot.send_message(existing_record_HR.id_telegram, 
                                    f"⚡️<b>Оповещение о середине дедлайна</b>⚡️\n"
                                    f"Вопрос\n" 
                                    f"<b>Номер вопроса: </b>{number_q}\n"
                                    f"<b>Инициатор: </b>{user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
                                    f"<b>Суть вопроса: </b>{id_quiz.Essence_question}\n"
                                    f"<b>Дата подачи заявки:</b> {id_quiz.Date_application}\n"
                                    f"<b>Дата планового дедлайна:</b> {id_quiz.Date_planned_deadline}", 
                                    parse_mode="HTML", reply_markup=set_deadline_tmrw_quiz)     

    else:
        id_info = session.query(application).filter(application.c.id == number_q).first()
        text = f"<b>Сотрудник: </b>"
        if id_info.ID_Employee == 1 and id_info.ID_Class_application != 4:
            result_Division = session.query(table_division).filter(table_division.c.id == id_info.ID_Division).first()
            resultPositiong = session.query(table_position).filter(table_position.c.id == id_info.ID_Position).first()
            text += f"{id_info.Full_name_employee}, {result_Division.Division}, {resultPositiong.Position}\n"               
        elif id_info.ID_Employee != 1 and id_info.ID_Class_application != 4:
            employee_info = session.query(table).filter(table.c.id == id_info.ID_Employee).first()
            text += f"{employee_info.Surname} {employee_info.Name} {employee_info.Middle_name}, {employee_info.Division}, {employee_info.Position}\n"

        target_date = id_info.Middle_deadline
        # Добавляем к целевой дате один день и устанавливаем время на 10:00 утра
        target_datetime = datetime(target_date.year, target_date.month, target_date.day, 10, 0, 0)
        # Вычисляем разницу между текущим временем и целевым временем
        delta = target_datetime - datetime.now()
        user_info = session.query(table).filter(table.c.id == id_info.ID_Initiator).first()
        if id_info.ID_Class_application == 4 and id_info.Date_actual_deadline == None:
            if delta.total_seconds() > 0:
                await asyncio.sleep(delta.total_seconds())   
            id_info = session.query(application).filter(application.c.id == number_q).first()
            date_c = id_info.Middle_deadline
            date_obj = date_c.strftime('%Y-%m-%d')
            if datetime.now().date().strftime('%Y-%m-%d') == date_obj:
                if id_info.Date_actual_deadline == None: 
                    await bot.send_message(existing_record_HR.id_telegram,
                                        f"⚡️<b>Оповещение о середине дедлайна</b>⚡️\n"
                                        f"Заявка по общей форме\n" 
                                        f"<b>Номер заявки: </b>{number_q}\n"
                                        f"<b>Инициатор: </b>{user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
                                        f"<b>Суть обращения: </b> {id_info.Essence_question}\n"
                                        f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                        f"<b>Дата планового дедлайна:</b> {id_info.Date_planned_deadline}", 
                                        parse_mode="HTML", reply_markup=set_deadline_tmrw)     
        elif id_info.ID_Class_application == 1 and id_info.Date_actual_deadline == None:
            if delta.total_seconds() > 0:
                await asyncio.sleep(delta.total_seconds())   
            id_info = session.query(application).filter(application.c.id == number_q).first()
            date_c = id_info.Middle_deadline
            date_obj = date_c.strftime('%Y-%m-%d')
            if datetime.now().date().strftime('%Y-%m-%d') == date_obj:
                if id_info.Date_actual_deadline == None: 
                    await bot.send_message(existing_record_HR.id_telegram,
                                        f"⚡️<b>Оповещение о середине дедлайна</b>⚡️\n"
                                        f"Заявка на перевод\n" 
                                        f"<b>Номер заявки: </b>{number_q}\n"
                                        f"<b>Инициатор: </b>{user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
                                        f"{text}"
                                        f"<b>Дата конца Испытательного Срока:</b> {id_info.End_date_IS}.\n"
                                        f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                        f"<b>Дата планового дедлайна:</b> {id_info.Date_planned_deadline}", 
                                        parse_mode="HTML", reply_markup=set_deadline_tmrw)     
        elif id_info.ID_Class_application == 2 and id_info.Date_actual_deadline == None:
            if delta.total_seconds() > 0:
                await asyncio.sleep(delta.total_seconds())   
            id_info = session.query(application).filter(application.c.id == number_q).first()
            date_c = id_info.Middle_deadline
            date_obj = date_c.strftime('%Y-%m-%d')
            if datetime.now().date().strftime('%Y-%m-%d') == date_obj:
                    if id_info.Date_actual_deadline == None: 
                        await bot.send_message(existing_record_HR.id_telegram,
                                            f"⚡️<b>Оповещение о середине дедлайна</b>⚡️\n"
                                            f"Заявка на перевод на другой формат работы\n" 
                                            f"<b>Номер заявки: </b>{number_q}\n"
                                            f"<b>Инициатор: </b>{user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
                                            f"{text}"
                                            f"<b>Формат на данный момент:</b> {id_info.Current_work_format}\n"
                                            f"<b>Формат на переход:</b> {id_info.Future_work_format}\n"
                                            f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                            f"<b>Дата планового дедлайна:</b> {id_info.Date_planned_deadline}", 
                                            parse_mode="HTML", reply_markup=set_deadline_tmrw)     
        elif id_info.ID_Class_application == 3 and id_info.Date_actual_deadline == None:
            if delta.total_seconds() > 0:
                await asyncio.sleep(delta.total_seconds())   
            id_info = session.query(application).filter(application.c.id == number_q).first()
            date_c = id_info.Middle_deadline
            date_obj = date_c.strftime('%Y-%m-%d')
            if datetime.now().date().strftime('%Y-%m-%d') == date_obj:
                if id_info.Date_actual_deadline == None: 
                    await bot.send_message(existing_record_HR.id_telegram,
                                        f"⚡️<b>Оповещение о середине дедлайна</b>⚡️\n"
                                        f"Заявка на согласование заработной платы\n" 
                                        f"<b>Номер заявки: </b>{number_q}\n"
                                        f"<b>Инициатор: </b>{user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
                                        f"{text}"
                                        f"<b>Действующая сумма:</b> {id_info.Current_amount}\n"
                                        f"<b>Предлагаемая сумма:</b> {id_info.Suggest_amount}\n"
                                        f"<b>Дата подачи заявки:</b> {id_info.Date_application}\n"
                                        f"<b>Дата планового дедлайна:</b> {id_info.Date_planned_deadline}", 
                                        parse_mode="HTML", reply_markup=set_deadline_tmrw)   
                