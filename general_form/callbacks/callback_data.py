from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot, types
from aiogram.types import Message
from general_form.keyboards.inline import yesno, hr, change, changequiz, yesnoquiz, hrquiz, send
from general_form.utils.states import Form
from keyboards.reply import cancel, main, start_kb
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from datetime import date
from sqlalchemy import insert

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
    if user_info:
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
        await bot.send_message(id_HR, 
                            f"<b>Заявка общая:</b>\n"
                            f"<b>Инициатор: </b>{user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
                            f"<b>Суть обращения: </b>{essence_data}\n"
                            f"<b>Дата: {today.strftime('%Y-%m-%d')}</b>", 
                            parse_mode="HTML", reply_markup=send)
        
        session.commit()
        await call.message.edit_reply_markup()
        await state.clear()
    else:
        await bot.send_message(call.from_user.id, "Ошибка в формировании заявки.")
        await bot.send_message(call.from_user.id, "Пройдите авторизацию повторно", reply_markup=start_kb)

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

    user_info = session.query(table).filter(table.c.id_telegram == user_id_str).first()
    if user_info:
        # Получение данных из состояний
        data = await state.get_data()

        # Определение, какие данные использовать

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

        await bot.send_message(call.from_user.id, "Заявка успешно отправлена!")
        await bot.send_message(call.from_user.id, "Информация о сроке решения будет отправлена Вам в ближайшее время.", reply_markup=main)
        await bot.send_message(id_HR, 
                            f"<b>Заявка вопроса:</b>\n"
                            f"<b>Инициатор: </b>{user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}\n"
                            f"<b>Суть вопроса: </b>{quiz_data}\n"
                            f"<b>Дата: {today.strftime('%Y-%m-%d')}</b>", parse_mode="HTML", reply_markup=send)   

        session.commit()
        await call.message.edit_reply_markup()
        await state.clear()
    else:
        await bot.send_message(call.from_user.id, "Ошибка в формировании заявки.")
        await bot.send_message(call.from_user.id, "Пройдите авторизацию повторно", reply_markup=start_kb)

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