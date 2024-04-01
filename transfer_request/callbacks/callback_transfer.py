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
from sqlalchemy import create_engine, MetaData, Table, func
from sqlalchemy.orm import sessionmaker
from avtorization.utils.states import FSMAdmin
from datetime import date
from sqlalchemy import insert, func
import re
from HR_employee.calendar import nav_cal_handler

from filters.chat_types import ChatTypeFilter

from utils.states import Employee
from transfer_request.utils.states import transferRequest
from keyboards import reply, inline
from transfer_request.keyboards.inline import get_callback_btns, send_transfer, send_transferAct

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

async def staff_post(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    # Получите сессию для работы с базой данных
    session = Session()
    search_bd = user_data.get('search_bd')
    result = session.query(table).filter(table.c.id == search_bd).first()
    initiator = user_data.get('initiator')
    resultInitiator = session.query(table).filter(table.c.id_telegram == str(initiator)).first()
    is_s = user_data.get('is_staff')

    data = await state.get_data()

    goals_list = data.get("goals_list")
    due_date_list = data.get("due_date_list")
    results_list = data.get("results_list")

    search = user_data.get('search')
    name = user_data.get('search_name')
    division = user_data.get('search_division')
    post = user_data.get('search_post')
    if resultInitiator:
        if search == False:
            await message.answer(
            "Ваша заявка на согласование заработной платы:\n"
            f"<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n"
            f"<b>Сотрудник:</b> {result.Surname} {result.Name} {result.Middle_name}, {result.Division}, {result.Position}\n"
            f"<b>Дата конца Испытательного Срока:</b> {is_s}."  
            )
        else:
            result_Division = session.query(table_division).filter(table_division.c.id == int(division)).first()
            await message.answer(
            "Ваша заявка на согласование заработной платы:\n"
            f"<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n"
            f"<b>Сотрудник:</b> {name}, {result_Division.Division}, {post}\n"
            f"<b>Дата конца Испытательного Срока:</b> {is_s}."  
            )
        if len(goals_list) == len(due_date_list) == len(results_list):
            #Все списки имеют одинаковую длину
            for i, goal in enumerate(goals_list):
                due_date = due_date_list[i]
                result = results_list[i]
                if i == len(goals_list) - 1:
                    message_text = f"<b>Цель {i + 1}:</b> {goal}\n<b>Срок исполнения:</b> {due_date}\n<b>Ожидаемый результат:</b> {result}"
                    await message.answer(message_text, 
                    )
                    await message.answer(
                        "Запрос введен верно?",
                        reply_markup=get_callback_btns(
                        btns={
                        'Данные верны': f'yes_application',
                        'Изменить данные': f'no_application',
                        }   
                )
            )
                else:
                    message_text = f"<b>Цель {i + 1}:</b> {goal}\n<b>Срок исполнения:</b> {due_date}\n<b>Ожидаемый результат:</b> {result}"
                    await message.answer(message_text)
        else:
            await message.answer(
                "Ошибка", reply_markup=reply.main
            )
    else:
        await state.clear()
        await message.answer("Ошибка в формировании заявки.")
        await message.answer("Пройдите авторизацию повторно", reply_markup=reply.start_kb)
        await state.set_state(FSMAdmin.phone)

@user_private_router.callback_query(F.data.startswith("yes_application"))
async def yes_app(callback:types.CallbackQuery):
    await callback.message.delete_reply_markup()
    await bot.send_message(callback.from_user.id, "Вы подтвердили правильность введенных данных.")
    await callback.message.answer(
        "Отправить заявку HR?",      
        reply_markup=get_callback_btns(
                btns={
                    'Да': f'go_application',
                    'Нет': f'stop_application',
                }
            ),    
    )

@user_private_router.callback_query(F.data.startswith("go_application"))
async def go_app(callback: types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    today = date.today()
    session = Session()
    user_id = callback.from_user.id
    user_id_str = str(user_id) 
    existing_record_HR = session.query(table).filter(table.c.Surname == "Минин", table.c.Name == "Вася", table.c.Middle_name == "роз").first()
    user_info = session.query(table).filter(table.c.id_telegram == user_id_str).first()
    if user_info:
        last_id = session.query(func.max(application.c.id)).scalar()
        new_id = last_id + 1
        data = await state.get_data()
        search_bd = data.get('search_bd')
        is_s = data.get('is_staff')
        goals_list = data.get("goals_list")
        due_date_list = data.get("due_date_list")
        results_list = data.get("results_list")
        search = data.get('search')
        name = data.get('search_name')
        division = data.get('search_division')
        post = data.get('search_post')
        goals_IS = ""
        for i, goal in enumerate(goals_list):
                due_date = due_date_list[i]
                result = results_list[i]
                goals_IS += f"<b>Цель {i + 1}:</b> {goal}\\n<b>Срок исполнения:</b> {due_date}\\n<b>Ожидаемый результат:</b> {result}\\n"    
        if search == False:
            result = session.query(table).filter(table.c.id == search_bd).first()
            application_data = {
                "ID_Initiator": user_info.id,
                "ID_Employee": result.id,
                "ID_Class_application": 1,
                'End_date_IS': is_s,
                'Goals_for_period_IS': goals_IS,
                "Date_application": today.strftime('%Y-%m-%d'),
            }
            session.execute(
                insert(application).values(application_data)
            )
            await bot.send_message(callback.from_user.id, "Заявка успешно отправлена!")
            await bot.send_message(callback.from_user.id, "Информация о сроке решения будет отправлена Вам в ближайшее время.", reply_markup=reply.main)
            text =  f"<b>Заявка на перевод:</b>\n<b>Номер заявки: </b>{new_id}\n<b>Инициатор:</b> {user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n<b>Сотрудник:</b> {result.Surname} {result.Name} {result.Middle_name}, {result.Division}, {result.Position}\n<b>Дата конца Испытательного Срока:</b> {is_s}.\n"  
            text += f"<b>Дата: {today.strftime('%Y-%m-%d')}</b>"        
            await bot.send_message(existing_record_HR.id_telegram,  text,
                                parse_mode="HTML", reply_markup=send_transfer)
        else:
            result_Division = session.query(table_division).filter(table_division.c.id == int(division)).first()
            resultPositiong = session.query(table_position).filter(table_position.c.Position == str(post)).first()
            # 2. Обновление записи в таблице Applications
            application_data = {
                "ID_Initiator": user_info.id,
                "ID_Employee": 1,
                "ID_Class_application": 1,
                'Full_name_employee': name,
                'ID_Division': int(division),
                'ID_Position': resultPositiong.id,
                'End_date_IS': is_s,
                'Goals_for_period_IS': goals_IS,
                "Date_application": today.strftime('%Y-%m-%d'),
            }
            session.execute(
                insert(application).values(application_data)
            )
            today = date.today()
            await bot.send_message(callback.from_user.id, "Заявка успешно отправлена!")
            await bot.send_message(callback.from_user.id, "Информация о сроке решения будет отправлена Вам в ближайшее время.", reply_markup=reply.main)
            text =  f"<b>Заявка на перевод:</b>\n<b>Номер заявки: </b>{new_id}\n<b>Инициатор:</b> {user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n<b>Сотрудник:</b> {name}, {result_Division.Division}, {post}\n<b>Дата конца Испытательного Срока:</b> {is_s}.\n"  
            text += f"<b>Дата: {today.strftime('%Y-%m-%d')}</b>"        
            await bot.send_message(existing_record_HR.id_telegram,  text,
                                parse_mode="HTML", reply_markup=send_transfer)
            
        session.commit()
        await state.clear()
        await state.update_data(unwrap = False)
    else:
        await bot.send_message(callback.from_user.id, "Ошибка в формировании заявки.")
        await bot.send_message(callback.from_user.id, "Пройдите авторизацию повторно", reply_markup=reply.start_kb)



message_states_app = {}
@user_private_router.callback_query(F.data =='unwrap_trans')
async def unwrap_message_app(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    session = Session()

    msg_id = call.message.message_id
    message_text = call.message.text

    # Регулярное выражение для поиска числа после строки "Номер заявки:"
    pattern = r"Номер заявки:\s*(\d+)"

    # Применяем регулярное выражение к сообщению
    match = re.search(pattern, message_text)
    number_q = match.group(1)


    id_info = session.query(application).filter(application.c.id == number_q).first()
    deadline_prob = id_info.End_date_IS
    goals_list = id_info.Goals_for_period_IS
    number_init = id_info.ID_Initiator
    date_info = id_info.Date_application

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

    data = await state.get_data()
    unwrap = data.get('unwrap')
 
    if unwrap == True:
        reply_markup = send_transferAct
        date_planned = f"\n<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}"
    else:
        reply_markup = send_transfer
        date_planned = ""
    init_info = session.query(table).filter(table.c.id == number_init).first()
    surname_init = init_info.Surname
    name_init = init_info.Name
    middle_init = init_info.Middle_name
    division_init = init_info.Division
    position_init = init_info.Position
    email_init = init_info.Email
    phone_init = init_info.Phone_number
 
    goals_list = goals_list.split("\\n")
    text = ""
    for i in enumerate(goals_list):
        text += f"{i[1]}\n" 
    print(goals_list)
    if msg_id not in message_states_app:
        # Если состояния сообщения нет, устанавливаем его в "second"
        message_states_app[msg_id] = "second"

    if msg_id in message_states_app and message_states_app[msg_id] == "first":
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=msg_id,
                                    text =  
                                    f"<b>Заявка на перевод:</b>\n"
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"<b>Инициатор:</b> {surname_init} {name_init[0]}. {middle_init[0]}.\n"
                                    f"<b>Сотрудник:</b> {fullname_employee}, {divis_info}, {post_info}\n"
                                    f"<b>Дата конца Испытательного Срока:</b> {deadline_prob}.\n"
                                    f"<b>Дата: {date_info}</b>"
                                    f"{date_planned}", 
                                    parse_mode="HTML", reply_markup=reply_markup)
        # Обновляем состояние сообщения в "second"
        message_states_app[msg_id] = "second"
    elif msg_id in message_states_app and message_states_app[msg_id] == "second":
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=msg_id,
                                    text=
                                    f"<b>Заявка на перевод:</b>\n"
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"<b>Инициатор: </b>{surname_init} {name_init} {middle_init}\n"
                                    f"<b>Должность: </b>{division_init}\n"
                                    f"<b>Подразделение: </b>{position_init}\n"
                                    f"<b>Телефон: </b>{phone_init}\n"
                                    f"<b>Почта: </b>{email_init}\n"
                                    f"<b>Сотрудник: </b>{fullname_employee}\n{divis_info}\n{post_info}\n"
                                    f"<b>Дата конца Испытательного Срока: </b>{deadline_prob}\n"
                                    f"{text}"
                                    f"<b>Дата: {date_info}</b>"
                                    f"{date_planned}", 
                                    parse_mode="HTML", reply_markup=reply_markup)
        # Возвращаем состояние сообщения к "first"
        message_states_app[msg_id] = "first"




@user_private_router.callback_query(F.data.startswith("stop_application"))
async def stop_app(callback: types.CallbackQuery):
    await callback.message.delete_reply_markup() 
    await callback.message.answer(
        "Выберите тип обращения", reply_markup=reply.main
    )

@user_private_router.callback_query(F.data.startswith("no_application"))
async def no_app(callback:types.CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Что необходимо изменить?", 
        reply_markup=get_callback_btns(
                btns={
                    'Сотрудник': f'search_changed',
                    'Дата конца ИС': f'is_change',
                    'Цели': f'goals_change',
                }
            ),    
    )


@user_private_router.callback_query(F.data.startswith("is_change"))
async def is_change(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Введите исправленную <b>дату конца ИС</b>", 
    )
    await state.set_state(transferRequest.is_staff)
    await state.update_data(is_changed=True)


@user_private_router.callback_query(F.data.startswith("goals_change"))
async def goals_change(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    data = await state.get_data()

    goals_list = data.get("goals_list")
    await callback.message.answer(
        "Выберите цель, которую необходимо исправить",  
        reply_markup=get_callback_btns(
        btns={
            f"Цель {i + 1}": f"goal_{i}" for i in range(len(goals_list))
        }
        )
    )
   
@user_private_router.callback_query(F.data.startswith("goal_"))
async def goal_change(callback: types.CallbackQuery, state: FSMContext):
    # Получение номера цели из данных обратного вызова
    goal_number = int(callback.data.split("_")[1])

    await callback.message.delete_reply_markup()

    # Запрос новых данных цели у пользователя
    await callback.message.answer(
        f"Введите новую <b>цель {goal_number+1}:</b>"
    )

    # Переход в состояние ожидания ввода новой цели
    await state.set_state(transferRequest.goals_staff)
    await state.update_data({"goal_number": goal_number, "step": 1})
    await state.update_data(goals_changed=True)




