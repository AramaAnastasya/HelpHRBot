from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot, types
from aiogram.types import Message
from aiogram.filters.callback_data import CallbackData
from general_form.keyboards.inline import yesno, hr, change, changequiz, yesnoquiz, hrquiz
from general_form.utils.states import Form
from HR_employee.calendar import nav_cal_handler
from keyboards.reply import cancel, main, start_kb
from general_form.keyboards.inline import send, sendquiz, sendquizAct, sendAct
from sqlalchemy import create_engine, MetaData, Table, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from datetime import date
from sqlalchemy import insert
import re

router = Router()

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



@router.callback_query(F.data == 'yes')
async def yes(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Отправить заявку в HR?", reply_markup=hr)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'no')
async def no(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите пункт для изменения:", reply_markup=change)
    await call.message.edit_reply_markup()


@router.callback_query(F.data == 'yesquiz')
async def yes(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Отправить заявку в HR?", reply_markup=hrquiz)
    await call.message.edit_reply_markup()
        

@router.callback_query(F.data == 'noquiz')
async def no(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите пункт для изменения:", reply_markup=changequiz)
    await call.message.edit_reply_markup()

@router.callback_query(F.data == 'yeshr')
async def yeshr(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    today = date.today()
    session = Session()
    user_id = call.from_user.id
    user_id_str = str(user_id)  

    user_info = session.query(table).filter(table.c.id_telegram == user_id_str).first()
    existing_record_HR = session.query(table).filter(table.c.Surname == "Минин", table.c.Name == "Вася", table.c.Middle_name == "роз").first()
    if user_info:
        last_id = session.query(func.max(application.c.id)).scalar()
        new_id = last_id + 1
       # Получение данных из состояний
        data = await state.get_data()

        # Определение, какие данные использовать
        essence_data = data.get('essence')
        expect_data = data.get('expect')

        # 2. Обновление записи в таблице Applications
        application_data = {
            "ID_Initiator": user_info.id,
            "ID_Employee": 1,
            "ID_Class_application": 4,
            "Date_application": today.strftime('%Y-%m-%d'),
            "Essence_question": essence_data,
            "Expected_result": expect_data
        }
        session.execute(
            insert(application).values(application_data)
        )
        await bot.send_message(call.from_user.id, "Заявка успешно отправлена!")
        await bot.send_message(call.from_user.id, "Информация о сроке решения будет отправлена Вам в ближайшее время.", reply_markup=main)
        await bot.send_message(existing_record_HR.id_telegram, 
                            f"<b>Заявка общая:</b>\n"
                            f"<b>Номер заявки: </b>{new_id}\n"
                            f"<b>Инициатор: </b>{user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
                            f"<b>Суть обращения: </b>{essence_data}\n"
                            f"<b>Дата:</b> {today.strftime('%Y-%m-%d')}", 
                            parse_mode="HTML", reply_markup=send)       
        session.commit()
        await call.message.edit_reply_markup()
        await state.clear()
    else:
        await bot.send_message(call.from_user.id, "Ошибка в формировании заявки.")
        await bot.send_message(call.from_user.id, "Пройдите авторизацию повторно", reply_markup=start_kb)


message_states = {}
@router.callback_query(F.data =='unwrap')
async def unwrap_message(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    session = Session()


    today = date.today()
    msg_id = call.message.message_id
    message_text = call.message.text

    # Регулярное выражение для поиска числа после строки "Номер заявки:"
    pattern = r"Номер заявки:\s*(\d+)"

    # Применяем регулярное выражение к сообщению
    match = re.search(pattern, message_text)
    number_q = match.group(1)


    id_info = session.query(application).filter(application.c.id == number_q).first()
    essence_que = id_info.Essence_question
    expect_res = id_info.Expected_result
    date_info = id_info.Date_application
    number_init = id_info.ID_Initiator
    init_info = session.query(table).filter(table.c.id == number_init).first()
    surname_init = init_info.Surname
    name_init = init_info.Name
    middle_init = init_info.Middle_name
    division_init = init_info.Division
    position_init = init_info.Position
    email_init = init_info.Email
    phone_init = init_info.Phone_number

    data = await state.get_data()
    unwrap = data.get('unwrap')
 
    if unwrap == True:
        reply_markup = sendAct
        date_planned = f"\n<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}"
    else:
        reply_markup = sendquiz
        date_planned = ""

    if msg_id not in message_states:
        # Если состояния сообщения нет, устанавливаем его в "second"
        message_states[msg_id] = "second"

    if msg_id in message_states and message_states[msg_id] == "first":
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=msg_id,
                                    text=                                   
                                    f"<b>Заявка общая:</b>\n"
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"<b>Инициатор: </b>{surname_init} {name_init[0]}. {middle_init[0]}.\n"
                                    f"<b>Суть обращение: </b> {essence_que}\n"
                                    f"<b>Дата: </b>{date_info}"
                                    f"{date_planned}", 
                                    reply_markup=reply_markup)
        # Обновляем состояние сообщения в "second"
        message_states[msg_id] = "second"
    elif msg_id in message_states and message_states[msg_id] == "second":
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=msg_id,
                                    text=
                                    f"<b>Заявка общая:</b>\n"
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"<b>Инициатор: </b>{surname_init} {name_init} {middle_init}\n"
                                    f"<b>Должность: </b>{division_init}\n"
                                    f"<b>Подразделение: </b>{position_init}\n"
                                    f"<b>Телефон: </b>{phone_init}\n"
                                    f"<b>Почта: </b>{email_init}\n"
                                    f"<b>Суть обращение: </b> {essence_que}\n"
                                    f"<b>Ожидаемый результат: </b> {expect_res}\n"
                                    f"<b>Дата: </b>{date_info}"
                                    f"{date_planned}", 
                                    reply_markup=reply_markup)
        # Возвращаем состояние сообщения к "first"
        message_states[msg_id] = "first"
    

@router.callback_query(F.data == 'nohr')
async def nohr(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите тип обращения", reply_markup=main)
    await call.message.edit_reply_markup()
    await state.clear()

@router.callback_query(F.data == 'yeshrquiz')
async def yeshr(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    session = Session()
    user_id = call.from_user.id
    user_id_str = str(user_id) 
    existing_record_HR = session.query(table).filter(table.c.Surname == "Минин", table.c.Name == "Вася", table.c.Middle_name == "роз").first()
    user_info = session.query(table).filter(table.c.id_telegram == user_id_str).first()
    if user_info:
        # Получение данных из состояний
        data = await state.get_data()

        last_id = session.query(func.max(question.c.id)).scalar()
        new_id = last_id + 1

        quiz_data = data.get('quiz')

        resquiz_data = data.get('resquiz')
        today = date.today()

        # 2. Обновление записи в таблице Question
        application_data = {
            "ID_Initiator": user_info.id,
            "ID_Employee": 1,
            "Date_application":today.strftime('%Y-%m-%d'),
            "Essence_question": quiz_data,
            "Essence_result": resquiz_data
        }
        session.execute(
            insert(question).values(application_data)
        )
        await state.update_data(unwrap = False)
        await bot.send_message(call.from_user.id, "Заявка успешно отправлена!")
        await bot.send_message(call.from_user.id, "Информация о сроке решения будет отправлена Вам в ближайшее время.", reply_markup=main)
        await bot.send_message(existing_record_HR.id_telegram, 
                            f"<b>Заявка вопроса:</b>\n"
                            f"<b>Номер заявки: </b>{new_id}\n"
                            f"<b>Инициатор: </b>{user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}\n"
                            f"<b>Суть вопроса: </b>{quiz_data}\n"
                            f"<b>Дата: {today.strftime('%Y-%m-%d')}</b>", parse_mode="HTML", reply_markup=sendquiz)   

        session.commit()
        await call.message.edit_reply_markup()
        await state.clear()
    else:
        await bot.send_message(call.from_user.id, "Ошибка в формировании заявки.")
        await bot.send_message(call.from_user.id, "Пройдите авторизацию повторно", reply_markup=start_kb)

message_states_quiz = {}
@router.callback_query(F.data =='unwrapquiz')
async def unwrap_message(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    session = Session()

    today = date.today()
    msg_id = call.message.message_id
    message_text = call.message.text

    # Регулярное выражение для поиска числа после строки "Номер заявки:"
    pattern = r"Номер заявки:\s*(\d+)"

    # Применяем регулярное выражение к сообщению
    match = re.search(pattern, message_text)
    number_q = match.group(1)


    id_info = session.query(question).filter(question.c.id == number_q).first()
    essence_que = id_info.Essence_question
    expect_res = id_info.Essence_result
    date_info = id_info.Date_application
    number_init = id_info.ID_Initiator
    init_info = session.query(table).filter(table.c.id == number_init).first()
    surname_init = init_info.Surname
    name_init = init_info.Name
    middle_init = init_info.Middle_name
    division_init = init_info.Division
    position_init = init_info.Position
    email_init = init_info.Email
    phone_init = init_info.Phone_number

    data = await state.get_data()
    unwrap = data.get('unwrap')
 
    if unwrap == True:
        reply_markup = sendquizAct
        date_planned = f"\n<b>Дата дедлайна:</b> {id_info.Date_planned_deadline}"
    else:
        reply_markup = sendquiz
        date_planned = ""
    if msg_id not in message_states_quiz:
        # Если состояния сообщения нет, устанавливаем его в "second"
        message_states_quiz[msg_id] = "second"

    if msg_id in message_states_quiz and message_states_quiz[msg_id] == "first":
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=msg_id,
                                    text=                                   
                                    f"<b>Заявка вопроса:</b>\n"
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"<b>Инициатор: </b>{surname_init} {name_init[0]}. {middle_init[0]}.\n"
                                    f"<b>Суть вопроса: </b>{essence_que}\n"
                                    f"<b>Дата:</b> {date_info}"
                                    f"{date_planned}", 
                                    parse_mode="HTML", reply_markup=reply_markup)  
        # Обновляем состояние сообщения в "second"
        message_states_quiz[msg_id] = "second"
    elif msg_id in message_states_quiz and message_states_quiz[msg_id] == "second":
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=msg_id,
                                    text=
                                    f"<b>Заявка вопроса:</b>\n"
                                    f"<b>Номер заявки: </b>{number_q}\n"
                                    f"<b>Инициатор: </b>{surname_init} {name_init} {middle_init}\n"
                                    f"<b>Должность: </b>{division_init}\n"
                                    f"<b>Подразделение: </b>{position_init}\n"
                                    f"<b>Телефон: </b>{phone_init}\n"
                                    f"<b>Почта: </b>{email_init}\n"
                                    f"<b>Суть вопроса: </b> {essence_que}\n"
                                    f"<b>Ожидаемый результат: </b> {expect_res}\n"
                                    f"<b>Дата: </b>{date_info}"
                                    f"{date_planned}",
                                    reply_markup=reply_markup)
        # Возвращаем состояние сообщения к "first"
        message_states_quiz[msg_id] = "first"


@router.callback_query(F.data =='set_deadlinequiz')
async def deadline_message(call: types.CallbackQuery, bot: Bot, state:FSMContext):
    session = Session()

    msg_id = call.message.message_id
    message_text = call.message.text

    pattern = r"Номер заявки:\s*(\d+)"

    match = re.search(pattern, message_text)
    number_q = match.group(1)
    await state.update_data(id_mess = msg_id)
    await state.update_data(number_q = number_q)
    await state.update_data(type_quiz = True)
    print("зашел")
    print(msg_id)
    print(number_q)
    await nav_cal_handler(call.message) 

@router.callback_query(F.data == 'nohrquiz')
async def nohr(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите тип обращения", reply_markup=main)
    await call.message.edit_reply_markup()
    await state.clear()


@router.callback_query(F.data == 'essenseedi')
async def essenseedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, f"Изменение пункта суть обращения")
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Введите <b>суть обращения</b>", parse_mode='HTML', reply_markup=cancel)
    await state.set_state(Form.essence2)

@router.message(Form.essence2)
async def essenseedi2(message: Message, state: FSMContext):
    session = Session()
    user_id = message.from_user.id
    user_id_str = str(user_id)  # Преобразуем user_id в строку
    user_info = session.query(table).filter(table.c.id_telegram == user_id_str).first()
    if user_info:
        await state.update_data(essence = message.text)
        data = await state.get_data()
        await message.answer(
                f"Ваша заявка:\n"
                f"<b>Инициатор:</b> {user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}\n"
                f"<b>Суть обращения:</b> {data['essence']}\n"
                f"<b>Ожидаемый результат:</b> {data['expect']}", parse_mode="HTML", reply_markup=cancel)
        await message.answer("Запрос введен верно?", reply_markup=yesno)
    else:
        await message("Ошибка в формировании заявки.")
        await message("Пройдите авторизацию повторно", reply_markup=start_kb)



@router.callback_query(F.data == 'expectedi')
async def expectedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, f"Изменение пункта ожидаемый результат")
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Введите <b>ожидаемый результат</b>", parse_mode='HTML', reply_markup=cancel)
    await state.set_state(Form.expect2)

@router.message(Form.expect2)
async def expectedi2(message: Message, state: FSMContext):
    session = Session()
    user_id = message.from_user.id
    user_id_str = str(user_id)  # Преобразуем user_id в строку
    user_info = session.query(table).filter(table.c.id_telegram == user_id_str).first()
    if user_info:
        await state.update_data(expect = message.text)
        data = await state.get_data()
        await message.answer(
                f"Ваша заявка:\n"
                f"<b>Инициатор:</b> {user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}\n"
                f"<b>Суть обращения:</b> {data['essence']}\n"
                f"<b>Ожидаемый результат:</b> {data['expect']}", parse_mode="HTML", reply_markup=cancel)
        await message.answer("Запрос введен верно?", reply_markup=yesno)
    else:
        await message("Ошибка в формировании заявки.")
        await message("Пройдите авторизацию повторно", reply_markup=start_kb)







@router.callback_query(F.data == 'noquiz')
async def noquiz(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, "Выберите пункт для изменения:", reply_markup=changequiz)
    await call.message.edit_reply_markup()


@router.callback_query(F.data == 'quizedit')
async def quizedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, f"Изменение пункта суть вопроса")
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Введите <b>суть вопроса</b>", parse_mode='HTML', reply_markup=cancel)
    await state.set_state(Form.quiz2)

@router.message(Form.quiz2)
async def quizedit2(message: Message, state: FSMContext):
    session = Session()
    user_id = message.from_user.id
    user_id_str = str(user_id)  # Преобразуем user_id в строку
    user_info = session.query(table).filter(table.c.id_telegram == user_id_str).first()
    if user_info:
        await state.update_data(quiz = message.text)
        data = await state.get_data()
        await message.answer(
                f"Ваш вопрос:\n"
                f"<b>Инициатор:</b> {user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}\n"
                f"<b>Суть вопроса:</b> {data['quiz']}\n"
                f"<b>Ожидаемый результат:</b> {data['resquiz']}", parse_mode="HTML", reply_markup=cancel)
        await message.answer("Запрос введен верно?", reply_markup=yesnoquiz)
    else:
        await message("Ошибка в формировании заявки.")
        await message("Пройдите авторизацию повторно", reply_markup=start_kb)



@router.callback_query(F.data == 'resquizedit')
async def resquizedit(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(call.from_user.id, f"Изменение пункта ожидаемый результат")
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Введите <b>ожидаемый результат</b>", parse_mode='HTML', reply_markup=cancel)
    await state.set_state(Form.resquiz2)

@router.message(Form.resquiz2)
async def quizedit2(message: Message, state: FSMContext):
    session = Session()
    user_id = message.from_user.id
    user_id_str = str(user_id)  # Преобразуем user_id в строку
    user_info = session.query(table).filter(table.c.id_telegram == user_id_str).first()
    if user_info:
        await state.update_data(resquiz = message.text)
        data = await state.get_data()
        await message.answer(
                f"Ваш вопрос:\n"
                f"<b>Инициатор:</b> {user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}\n"
                f"<b>Суть вопроса:</b> {data['quiz']}\n"
                f"<b>Ожидаемый результат:</b> {data['resquiz']}", parse_mode="HTML", reply_markup=cancel)
        await message.answer("Запрос введен верно?", reply_markup=yesnoquiz)
    else:
        await message("Ошибка в формировании заявки.")
        await message("Пройдите авторизацию повторно", reply_markup=start_kb)