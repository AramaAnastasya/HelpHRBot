import os
import re
from aiogram import F, types, Router, Bot,Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.formatting import as_list, as_marked_section, Bold,Spoiler #Italic, as_numbered_list и тд 
from sqlalchemy import create_engine, MetaData, Table, func
from sqlalchemy.orm import sessionmaker
from HR_employee.calendar import nav_cal_handler
from avtorization.utils.states import FSMAdmin
from datetime import date
from sqlalchemy import insert, func
import re
from filters.chat_types import ChatTypeFilter
from handlers.keyboards.inline import init_zp, init_zp_d

from utils.states import Employee
from task_ZP.utils.states import taskZP
from keyboards import reply, inline
from task_ZP.keyboards.inline import get_callback_btns, send_zp, send_zpAct, send_zpAct_d, send_zp_d


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
table_position = Table('Position', metadata, autoload_with=engine)
application = Table('Applications', metadata, autoload_with=engine)

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
    if resultInitiator:
        if search == False:
            await message.answer(
            "Ваша заявка на согласование заработной платы\n"
            f"<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n"
            f"<b>Сотрудник:</b> {result.Surname} {result.Name} {result.Middle_name}, {result.Division}, {result.Position}\n"
            f"<b>Действующая сумма:</b> {current}\n"
            f"<b>Предлагаемая сумма:</b> {proposed}\n"
            f"<b>Причина перевода: </b>{reasons}",
            )
        else:
            result_Division = session.query(table_division).filter(table_division.c.id == int(division)).first()
            await message.answer(
            "Ваша заявка на согласование заработной платы\n"
            f"<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n"
            f"<b>Сотрудник:</b> {name}, {result_Division.Division}, {post}\n"
            f"<b>Действующая сумма:</b> {current}\n"
            f"<b>Предлагаемая сумма:</b> {proposed}\n"
            f"<b>Причина перевода: </b>{reasons}",
            )
        await message.answer(
            "Запрос введен верно?",
            reply_markup=get_callback_btns(
                btns={
                'Да': f'yes_task',
                'Нет': f'no_task',
                }   
            )
        )
    else:
        await state.clear()
        await message.answer("Ошибка в формировании заявки.")
        await message.answer("Пройдите авторизацию повторно", reply_markup=reply.start_kb)
        await state.set_state(FSMAdmin.phone)

@user_private_router.callback_query(F.data.startswith("yes_task"))
async def yes_app(callback:types.CallbackQuery):
    await callback.message.delete_reply_markup()
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
    today = date.today()
    session = Session()
    user_id = callback.from_user.id
    user_id_str = str(user_id)  # Преобразуем user_id в строку

    user_info = session.query(table).filter(table.c.id_telegram == user_id_str).first()

    last_id = session.query(func.max(application.c.id)).scalar()
    new_id = last_id + 1
    existing_record_HR = session.query(table).filter(table.c.Surname == "Минин", table.c.Name == "Вася", table.c.Middle_name == "роз").first()
    if user_info:
        # Получение данных из состояний
        data = await state.get_data()
        search_bd = data.get('search_bd')
        proposed = data.get('proposed_amount')
        current = data.get('current_amount')
        reasons = data.get('reasons')
        search = data.get('search')
        name = data.get('search_name')
        division = data.get('search_division')
        post = data.get('search_post')
        if search == False:
            result = session.query(table).filter(table.c.id == search_bd).first()
            # 2. Обновление записи в таблице Applications
            application_data = {
                "ID_Initiator": user_info.id,
                "ID_Employee": result.id,
                "ID_Class_application": 3,
                'Suggested_amount': proposed,
                'Current_amount': current,
                'Cause': reasons,
                "Date_application": today.strftime('%Y-%m-%d'),
            }
            session.execute(
                insert(application).values(application_data)
            )
            await bot.send_message(callback.from_user.id, "Заявка успешно отправлена!")
            await bot.send_message(callback.from_user.id, "Информация о сроке решения будет отправлена Вам в ближайшее время.", reply_markup=reply.main)
            await bot.send_message(existing_record_HR.id_telegram,
                                   f"<b>🔔Вам поступила новая заявка</b>")
            await bot.send_message(existing_record_HR.id_telegram, 
                                f"<b>Заявка на согласование заработной платы</b>\n"
                                f"<b>Номер заявки: </b>{new_id}\n"
                                f"<b>Инициатор:</b> {user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
                                f"<b>Сотрудник:</b> {result.Surname} {result.Name} {result.Middle_name}\n"
                                f"<b>Действующая сумма:</b> {current}\n"
                                f"<b>Предлагаемая сумма:</b> {proposed}\n"
                                f"<b>Дата подачи заявки:</b> {today.strftime('%Y-%m-%d')}", 
                                parse_mode="HTML", reply_markup=send_zp)
        else:
            result_Division = session.query(table_division).filter(table_division.c.id == int(division)).first()
            resultPositiong = session.query(table_position).filter(table_position.c.Position == str(post)).first()
            # 2. Обновление записи в таблице Applications
            application_data = {
                "ID_Initiator": user_info.id,
                "ID_Employee": 1,
                "ID_Class_application": 3,
                'Full_name_employee': name,
                'ID_Division': int(division),
                'ID_Position': resultPositiong.id,
                'Suggested_amount': proposed,
                'Current_amount': current,
                'Cause': reasons,
                "Date_application": today.strftime('%Y-%m-%d'),
            }
            session.execute(
                insert(application).values(application_data)
            )
            today = date.today()
            await bot.send_message(callback.from_user.id, "Заявка успешно отправлена!")
            await bot.send_message(callback.from_user.id, "Информация о сроке решения будет отправлена Вам в ближайшее время.", reply_markup=reply.main)
            await bot.send_message(existing_record_HR.id_telegram,
                                   f"<b>🔔Вам поступила новая заявка</b>")
            await bot.send_message(existing_record_HR.id_telegram, 
                                 f"<b>Заявка на согласование заработной платы</b>\n"
                                f"<b>Номер заявки: </b>{new_id}\n"
                                f"<b>Инициатор:</b> {user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
                                f"<b>Сотрудник:</b> {name}\n"
                                f"<b>Действующая сумма:</b> {current}\n"
                                f"<b>Предлагаемая сумма:</b> {proposed}\n"
                                f"<b>Дата подачи заявки:</b> {today.strftime('%Y-%m-%d')}", 
                                parse_mode="HTML", reply_markup=send_zp)
        session.commit()

        await state.clear()
        await state.update_data(unwrap = False)
    else:
        await bot.send_message(callback.from_user.id, "Ошибка в формировании заявки.")
        await bot.send_message(callback.from_user.id, "Пройдите авторизацию повторно", reply_markup=reply.start_kb)



message_states_zp = {}
@user_private_router.callback_query(F.data =='unwrap_zp')
async def unwrap_message_zp(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    session = Session()

    msg_id = call.message.message_id
    message_text = call.message.text

    # Регулярное выражение для поиска числа после строки "Номер заявки:"
    pattern = r"Номер заявки:\s*(\d+)"

    # Применяем регулярное выражение к сообщению
    match = re.search(pattern, message_text)
    number_q = match.group(1)


    id_info = session.query(application).filter(application.c.id == number_q).first()
    current_amount = id_info.Current_amount
    suggest_amount = id_info.Suggested_amount
    reason_change = id_info.Cause
    date_info = id_info.Date_application
    number_init = id_info.ID_Initiator


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

    if msg_id not in message_states_zp:
        # Если состояния сообщения нет, устанавливаем его в "second"
        message_states_zp[msg_id] = "second"

    existing_record_HR = session.query(table).filter(table.c.Surname == "Минин", table.c.Name == "Вася", table.c.Middle_name == "роз", table.c.id_telegram == str(call.from_user.id)).first()
    if id_info.Date_planned_deadline != None and message_states_zp[msg_id] == "first" and existing_record_HR != None:
        reply_markup = send_zpAct
        date_planned = f"\n<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}"
    elif id_info.Date_planned_deadline != None and message_states_zp[msg_id] == "second" and existing_record_HR != None:   
        reply_markup = send_zpAct_d
        date_planned = f"\n<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}"
    elif id_info.Date_planned_deadline == None and message_states_zp[msg_id] == "first" and existing_record_HR != None:
        reply_markup = send_zp
        date_planned = ""
    elif id_info.Date_planned_deadline == None and message_states_zp[msg_id] == "second" and existing_record_HR != None:
        reply_markup = send_zp_d
        date_planned = ""
    elif id_info.Date_planned_deadline != None and message_states_zp[msg_id] == "first" and existing_record_HR == None:
        reply_markup = init_zp
        date_planned = f"\n<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}"
    elif id_info.Date_planned_deadline != None and message_states_zp[msg_id] == "second" and existing_record_HR == None:   
        reply_markup = init_zp_d
        date_planned = f"\n<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}"
    elif id_info.Date_planned_deadline == None and message_states_zp[msg_id] == "first" and existing_record_HR == None:
        reply_markup = init_zp
        date_planned = ""
    elif id_info.Date_planned_deadline == None and message_states_zp[msg_id] == "second" and existing_record_HR == None:
        reply_markup = init_zp_d
        date_planned = ""   


    init_info = session.query(table).filter(table.c.id == number_init).first()
    surname_init = init_info.Surname
    name_init = init_info.Name
    middle_init = init_info.Middle_name
    division_init = init_info.Division
    position_init = init_info.Position
    email_init = init_info.Email
    phone_init = init_info.Phone_number

    if msg_id in message_states_zp and message_states_zp[msg_id] == "first":
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=msg_id,
                                    text=                                   
                                    f"<b>Заявка на согласование заработной платы</b>\n"
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"<b>Инициатор: </b>{surname_init} {name_init[0]}. {middle_init[0]}.\n"
                                    f"<b>Сотрудник:</b> {fullname_employee}\n"
                                    f"<b>Действующая сумма:</b> {current_amount}\n"
                                    f"<b>Предлагаемая сумма:</b> {suggest_amount}\n"
                                    f"<b>Дата подачи заявки:</b> {date_info}"
                                    f"{date_planned}", 
                                    parse_mode="HTML", reply_markup=reply_markup)
        # Обновляем состояние сообщения в "second"
        message_states_zp[msg_id] = "second"
    elif msg_id in message_states_zp and message_states_zp[msg_id] == "second":
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=msg_id,
                                    text=
                                    f"<b>Заявка на согласование заработной платы</b>\n"
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"<b>Инициатор: </b>{surname_init} {name_init} {middle_init}\n"
                                    f"<b>Должность: </b>{division_init}\n"
                                    f"<b>Подразделение: </b>{position_init}\n"
                                    f"<b>Телефон: </b>{phone_init}\n"
                                    f"<b>Почта: </b>{email_init}\n"
                                    f"<b>Сотрудник:</b> {fullname_employee}\n{divis_info}\n{post_info}\n"
                                    f"<b>Действующая сумма:</b> {current_amount}\n"
                                    f"<b>Предлагаемая сумма:</b> {suggest_amount}\n"
                                    f"<b>Причина перевода: </b>{reason_change}\n"
                                    f"<b>Дата подачи заявки:</b> {date_info}"
                                    f"{date_planned}", 
                                    parse_mode="HTML", reply_markup=reply_markup)
        # Возвращаем состояние сообщения к "first"
        message_states_zp[msg_id] = "first"



@user_private_router.callback_query(F.data.startswith("stop_app"))
async def stop_app(callback: types.CallbackQuery):
    await callback.message.delete_reply_markup() 
    await callback.message.answer(
        "Выберите тип обращения", reply_markup=reply.main
    )

@user_private_router.callback_query(F.data.startswith("no_task"))
async def no_app(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
            "Выберите пункт для изменения", 
             reply_markup= inline.changeInf   
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
        "Введите исправленную <b>причину перевода</b>", 
    )
    await state.set_state(taskZP.reasons)
    await state.update_data(reasons_changed=True)
