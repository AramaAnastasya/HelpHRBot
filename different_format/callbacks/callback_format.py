from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot, types
from aiogram.types import Message
from different_format.keyboards.inline import hr, placenowkb, placewillkb, yesnotransfer,changetr, placenowkbedi, placewillkbedi, send_different, send_differentAct
from different_format.utils.states import FormTransf
from keyboards.reply import cancel, main, start_kb
from keyboards import inline
from utils.states import Employee
from sqlalchemy import create_engine, MetaData, Table, func
from sqlalchemy.orm import sessionmaker
from avtorization.utils.states import FSMAdmin
from datetime import date
from sqlalchemy import insert
from sqlalchemy import func
import re

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

router = Router()

@router.callback_query(F.data == 'officenow')
async def fill_officenow(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите  <b>формат работы на переход</b>", reply_markup=placewillkb, parse_mode="HTML")
    await state.update_data(placenow = "Офис")
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'hybridnow')
async def fill_hybridnow(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите  <b>формат работы на переход</b>", reply_markup=placewillkb, parse_mode="HTML")
    await state.update_data(placenow = "Гибрид")
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'remotelynow')
async def fill_remotelynow(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите  <b>формат работы на переход</b>", reply_markup=placewillkb, parse_mode="HTML")
    await state.update_data(placenow = "Удаленно")
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'officewill')
async def fill_officewill(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Введите <b>часы работы</b>", parse_mode="HTML", reply_markup=cancel)
    await state.update_data(placewill = "Офис")
    await state.set_state(FormTransf.timework)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'hybridwill')
async def fill_hybridwill(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Введите <b>часы работы</b>", parse_mode="HTML", reply_markup=cancel)
    await state.update_data(placewill = "Гибрид")
    await state.set_state(FormTransf.timework)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'remotelywill')
async def fill_remotelywill(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Введите <b>часы работы</b>", parse_mode="HTML", reply_markup=cancel)
    await state.update_data(placewill = "Удаленно")
    await state.set_state(FormTransf.timework)
    await call.message.edit_reply_markup()


@router.callback_query(F.data == 'yestr')
async def yestr(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Отправить заявку в HR?", reply_markup=hr)
    await call.message.edit_reply_markup()


@router.callback_query(F.data == 'notr')
async def notr(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите пункт для изменения:", reply_markup=changetr)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'yes_diff')
async def yesdiff(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.delete_reply_markup()
    today = date.today()
    session = Session()
    user_id = call.from_user.id
    user_id_str = str(user_id) 
    existing_record_HR = session.query(table).filter(table.c.Surname == "Минин", table.c.Name == "Вася", table.c.Middle_name == "роз").first()
    user_info = session.query(table).filter(table.c.id_telegram == user_id_str).first()
    if user_info:
        # Получение данных из состояний
        data = await state.get_data()
        search_bd = data.get('search_bd')
        search = data.get('search')
        name = data.get('search_name')
        division = data.get('search_division')
        post = data.get('search_post')
        print("a")
        last_id = session.query(func.max(application.c.id)).scalar()
        new_id = last_id + 1
        if search == False:
            result = session.query(table).filter(table.c.id == search_bd).first()
            # 2. Обновление записи в таблице Applications
            application_data = {
                "ID_Initiator": user_info.id,
                "ID_Employee": result.id,
                "ID_Class_application": 2,
                'Current_work_format': data['placenow'],
                'Future_work_format': data['placewill'],
                'Opening_hours': data['timework'],
                'City': data['city'],
                'Cause': data['reason'],
                "Date_application": today.strftime('%Y-%m-%d'),
            }
            session.execute(
                insert(application).values(application_data)
            )
            await bot.send_message(call.from_user.id, "Заявка успешно отправлена!")
            await bot.send_message(call.from_user.id, "Информация о сроке решения будет отправлена Вам в ближайшее время.", reply_markup=main)
            await bot.send_message(existing_record_HR.id_telegram, 
                                 f"<b>Заявка на перевод на другой формат работы:</b>\n"
                                f"<b>Номер заявки: </b>{new_id}\n"
                                f"<b>Инициатор:</b> {user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
                                f"<b>Сотрудник:</b> {result.Surname} {result.Name} {result.Middle_name}\n"
                                f"<b>Формат на данный момент:</b> {data['placenow']}\n"
                                f"<b>Формат на переход:</b> {data['placewill']}\n"
                                f"<b>Дата: {today.strftime('%Y-%m-%d')}</b>", 
                                parse_mode="HTML", reply_markup=send_different)
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
                'Current_work_format': data['placenow'],
                'Future_work_format': data['placewill'],
                'Opening_hours': data['timework'],
                'City': data['city'],
                'Cause': data['reason'],
                "Date_application": today.strftime('%Y-%m-%d'),
            }
            session.execute(
                insert(application).values(application_data)
            )
            today = date.today()
            await bot.send_message(call.from_user.id, "Заявка успешно отправлена!")
            await bot.send_message(call.from_user.id, "Информация о сроке решения будет отправлена Вам в ближайшее время.", reply_markup=main)
            await bot.send_message(existing_record_HR.id_telegram, 
                                f"<b>Заявка на перевод на другой формат работы:</b>\n"
                                f"<b>Номер заявки: </b>{new_id}\n"
                                f"<b>Инициатор:</b> {user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
                                f"<b>Сотрудник:</b> {name} \n"
                                f"<b>Формат на данный момент:</b> {data['placenow']}\n"
                                f"<b>Формат на переход:</b> {data['placewill']}\n"
                                f"<b>Дата: {today.strftime('%Y-%m-%d')}</b>", 
                                parse_mode="HTML", reply_markup=send_different)
        session.commit()
        await state.clear()
        await state.update_data(unwrap = False)
    else:
        await bot.send_message(call.from_user.id, "Ошибка в формировании заявки.")
        await bot.send_message(call.from_user.id, "Пройдите авторизацию повторно", reply_markup=start_kb)



message_states_diff = {}
@router.callback_query(F.data =='unwrap_different')
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
    placenow_info = id_info.Current_work_format
    placewill_info = id_info.Future_work_format
    reason_change = id_info.Cause
    date_info = id_info.Date_application
    number_init = id_info.ID_Initiator
    timework_info = id_info.Opening_hours
    city_info = id_info.City

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
        reply_markup = send_differentAct
        date_planned = f"\n<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}"
    else:
        reply_markup = send_different
        date_planned = ""

    init_info = session.query(table).filter(table.c.id == number_init).first()
    surname_init = init_info.Surname
    name_init = init_info.Name
    middle_init = init_info.Middle_name
    division_init = init_info.Division
    position_init = init_info.Position
    email_init = init_info.Email
    phone_init = init_info.Phone_number


    if msg_id not in message_states_diff:
        # Если состояния сообщения нет, устанавливаем его в "second"
        message_states_diff[msg_id] = "second"

    if msg_id in message_states_diff and message_states_diff[msg_id] == "first":
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=msg_id,
                                    text=                                   
                                    f"<b>Заявка на перевод на другой формат работы:</b>\n"
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"<b>Инициатор:</b> {surname_init} {name_init[0]}. {middle_init[0]}.\n"
                                    f"<b>Сотрудник:</b> {fullname_employee}\n"
                                    f"<b>Формат на данный момент:</b> {placenow_info}\n"
                                    f"<b>Формат на переход:</b> {placewill_info}\n"
                                    f"<b>Дата: {date_info}</b>"
                                    f"{date_planned}",  
                                    parse_mode="HTML", reply_markup=reply_markup)
        # Обновляем состояние сообщения в "second"
        message_states_diff[msg_id] = "second"
    elif msg_id in message_states_diff and message_states_diff[msg_id] == "second":
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=msg_id,
                                    text=
                                    f"<b>Заявка на перевод на другой формат работы:</b>\n"
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"<b>Инициатор: </b>{surname_init} {name_init} {middle_init}\n"
                                    f"<b>Должность: </b>{division_init}\n"
                                    f"<b>Подразделение: </b>{position_init}\n"
                                    f"<b>Телефон: </b>{phone_init}\n"
                                    f"<b>Почта: </b>{email_init}\n"
                                    f"<b>Сотрудник:</b> {fullname_employee}\n{divis_info}\n{post_info}\n"
                                    f"<b>Формат на данный момент:</b> {placenow_info}\n"
                                    f"<b>Формат на переход:</b> {placewill_info}\n"
                                    f"<b>Часы работы:</b> {timework_info}\n"
                                    f"<b>Город:</b> {city_info}\n"
                                    f"<b>Причина перевода:</b> {reason_change}\n"
                                    f"<b>Дата: {date_info}</b>"
                                    f"{date_planned}",  
                                    parse_mode="HTML", reply_markup=reply_markup)
        # Возвращаем состояние сообщения к "first"
        message_states_diff[msg_id] = "first"





@router.callback_query(F.data == 'no_diff')
async def nohr(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите тип обращения", reply_markup=main)
    await call.message.edit_reply_markup()
    await state.clear()


@router.callback_query(F.data == 'placenowedi')
async def placenowedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Изменение пункта Формат на данный момент", reply_markup=cancel)
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Выберите  <b>формат на данный момент</b>", parse_mode='HTML', reply_markup=placenowkbedi)




@router.callback_query(F.data == 'officenowedi')
async def fill_officenowedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(placenow = "Офис")
    user_id = call.from_user.id
    await state.update_data(initiator = user_id)
    data = await state.get_data()
    session = Session()
    search_bd = data.get('search_bd')
    result = session.query(table).filter(table.c.id == search_bd).first()
    resultInitiator = session.query(table).filter(table.c.id_telegram == str(user_id)).first()
    search = data.get('search')
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    if search == False:
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {result.Surname} {result.Name} {result.Middle_name}, {result.Division}, {result.Position}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    else:
        result_Division = session.query(table_division).filter(table_division.c.id == int(division)).first()
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {name}, {result_Division.Division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    
    await bot.send_message(call.from_user.id, formatter_text, parse_mode="HTML", reply_markup=cancel)
    await bot.send_message(call.from_user.id,"Запрос введен верно?", reply_markup=yesnotransfer)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'hybridnowedi')
async def fill_hybridnowedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(placenow = "Гибрид")
    user_id = call.from_user.id
    await state.update_data(initiator = user_id)
    data = await state.get_data()
    session = Session()
    search_bd = data.get('search_bd')
    result = session.query(table).filter(table.c.id == search_bd).first()
    resultInitiator = session.query(table).filter(table.c.id_telegram == str(user_id)).first()
    search = data.get('search')
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    if search == False:
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {result.Surname} {result.Name} {result.Middle_name}, {result.Division}, {result.Position}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    else:
        result_Division = session.query(table_division).filter(table_division.c.id == int(division)).first()
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {name}, {result_Division.Division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    
    
    await bot.send_message(call.from_user.id, formatter_text, parse_mode="HTML", reply_markup=cancel)
    await bot.send_message(call.from_user.id,"Запрос введен верно?", reply_markup=yesnotransfer)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'remotelynowedi')
async def fill_remotelynowedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(placenow = "Удаленно")
    user_id = call.from_user.id
    await state.update_data(initiator = user_id)
    
    data = await state.get_data()
    session = Session()
    search_bd = data.get('search_bd')
    result = session.query(table).filter(table.c.id == search_bd).first()
    resultInitiator = session.query(table).filter(table.c.id_telegram == str(user_id)).first()
    search = data.get('search')
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    if search == False:
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {result.Surname} {result.Name} {result.Middle_name}, {result.Division}, {result.Position}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    else:
        result_Division = session.query(table_division).filter(table_division.c.id == int(division)).first()
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {name}, {result_Division.Division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")

    await bot.send_message(call.from_user.id, formatter_text, parse_mode="HTML", reply_markup=cancel)
    await bot.send_message(call.from_user.id,"Запрос введен верно?", reply_markup=yesnotransfer)
    await call.message.edit_reply_markup()




@router.callback_query(F.data == 'placewilledi')
async def placewilledit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Изменение пункта Формат на переход", reply_markup=cancel)
    await call.message.edit_reply_markup()
    chat_member = await bot.get_chat_member(call.message.chat.id, call.message.from_user.id)
    await state.update_data(initiator = chat_member.user.id)
    await bot.send_message(call.from_user.id, "Выберите  <b>формат на переход</b>", parse_mode='HTML', reply_markup=placewillkbedi)




@router.callback_query(F.data == 'officewilledi')
async def fill_officewilledit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(placewill = "Офис")
    user_id = call.from_user.id
    await state.update_data(initiator = user_id)
    data = await state.get_data()
    session = Session()
    search_bd = data.get('search_bd')
    result = session.query(table).filter(table.c.id == search_bd).first()
    resultInitiator = session.query(table).filter(table.c.id_telegram == str(user_id)).first()
    search = data.get('search')
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    if search == False:
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {result.Surname} {result.Name} {result.Middle_name}, {result.Division}, {result.Position}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    else:
        result_Division = session.query(table_division).filter(table_division.c.id == int(division)).first()
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {name}, {result_Division.Division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    
    await bot.send_message(call.from_user.id, formatter_text, parse_mode="HTML", reply_markup=cancel)
    await bot.send_message(call.from_user.id,"Запрос введен верно?", reply_markup=yesnotransfer)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'hybridwilledi')
async def fill_hybridwilledit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(placewill = "Гибрид")
    user_id = call.from_user.id
    await state.update_data(initiator = user_id)
    data = await state.get_data()
    session = Session()
    search_bd = data.get('search_bd')
    result = session.query(table).filter(table.c.id == search_bd).first()
    resultInitiator = session.query(table).filter(table.c.id_telegram == str(user_id)).first()
    search = data.get('search')
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    if search == False:
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {result.Surname} {result.Name} {result.Middle_name}, {result.Division}, {result.Position}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    else:
        result_Division = session.query(table_division).filter(table_division.c.id == int(division)).first()
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {name}, {result_Division.Division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    
    
    await bot.send_message(call.from_user.id, formatter_text, parse_mode="HTML", reply_markup=cancel)
    await bot.send_message(call.from_user.id,"Запрос введен верно?", reply_markup=yesnotransfer)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'remotelywilledi')
async def fill_remotelywilledit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(placewill = "Удаленно")
    user_id = call.from_user.id
    await state.update_data(initiator = user_id)
    data = await state.get_data()
    session = Session()
    search_bd = data.get('search_bd')
    result = session.query(table).filter(table.c.id == search_bd).first()
    resultInitiator = session.query(table).filter(table.c.id_telegram == str(user_id)).first()
    search = data.get('search')
    name = data.get('search_name')
    division = data.get('search_division')
    post = data.get('search_post')
    if search == False:
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {result.Surname} {result.Name} {result.Middle_name}, {result.Division}, {result.Position}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    else:
        result_Division = session.query(table_division).filter(table_division.c.id == int(division)).first()
        formatter_text = (f"Ваша заявка на перевод на другой формат работы:\n<b>Инициатор:</b> {resultInitiator.Surname} {resultInitiator.Name[0]}. {resultInitiator.Middle_name[0]}.\n<b>Сотрудник:</b> {name}, {result_Division.Division}, {post}\n<b>Формат на данный момент:</b> {data['placenow']}\n<b>Формат на переход:</b> {data['placewill']}\n<b>Часы работы:</b> {data['timework']}\n<b>Город:</b> {data['city']}\n<b>Причина перевода:</b> {data['reason']}")
    
    
    await bot.send_message(call.from_user.id, formatter_text, parse_mode="HTML", reply_markup=cancel)
    await bot.send_message(call.from_user.id,"Запрос введен верно?", reply_markup=yesnotransfer)
    await call.message.edit_reply_markup()




@router.callback_query(F.data == 'timeworkedi')
async def timeworkedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Изменение пункта Часы работы", reply_markup=cancel)
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Введите <b>часы работы</b>", parse_mode='HTML')
    await state.set_state(FormTransf.timework2)




@router.callback_query(F.data == 'cityedi')
async def cityedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Изменение пункта Город", reply_markup=cancel)
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Введите <b>город</b>", parse_mode='HTML')
    await state.set_state(FormTransf.city2)



@router.callback_query(F.data == 'reasonedi')
async def reasonedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Изменение пункта Причина перевода", reply_markup=cancel)
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Введите <b>причину перевода</b>", parse_mode='HTML')
    await state.set_state(FormTransf.reason2)
