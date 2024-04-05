from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.reply import cancel
from general_form.utils.states import Form
from general_form.keyboards import inline
from keyboards import reply
from avtorization.utils.states import FSMAdmin
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

router = Router()

from config import DATABASE_URI

# Создайте подключение к базе данных
engine = create_engine(DATABASE_URI)

# Создайте сессию для работы с базой данных
Session = sessionmaker(bind=engine)

# Создайте таблицу, из которой будут извлекаться данные
metadata = MetaData()
table = Table('employee', metadata, autoload_with=engine)

@router.message(F.text == "Общая форма")
async def fill_request(message: Message, state: FSMContext):
    await state.set_state(Form.essence)
    await message.answer(
            "Введите <b>суть обращения</b>",
            reply_markup=cancel,
            parse_mode="HTML",

    )

@router.message(Form.essence)
async def fill_essence(message: Message, state: FSMContext):
    await state.update_data(essence=message.text)
    await state.set_state(Form.expect)
    await message.answer("Введите <b>ожидаемый результат</b>", reply_markup=cancel, parse_mode="HTML")


@router.message(Form.expect)
async def fill_expect(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_id_str = str(user_id)  # Преобразуем user_id в строку
    session = Session()
    user_info = session.query(table).filter(table.c.id_telegram == user_id_str).first()

    if user_info:
        await state.update_data(expect=message.text)
        data = await state.get_data()
        formatter_text = (
            f"Ваша заявка по общей форме\n"
            f"<b>Инициатор:</b> {user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
            f"<b>Суть обращения:</b> {data['essence']}\n"
            f"<b>Ожидаемый результат:</b> {data['expect']}"
        )
        await message.answer(formatter_text, parse_mode="HTML", reply_markup=cancel)
        await message.answer("Запрос введен верно?", reply_markup=inline.yesno)
    else:
        await state.clear()
        await message.answer("Ошибка в формировании заявки.")
        await message.answer("Пройдите авторизацию повторно", reply_markup=reply.start_kb)
        await state.set_state(FSMAdmin.phone)


@router.message(F.text == "Задать вопрос")
async def fill_request(message: Message, state: FSMContext):
    await state.set_state(Form.quiz)
    await message.answer(
        "Введите <b>суть вопроса</b>",
        reply_markup=cancel,
        parse_mode="HTML",
    )

@router.message(Form.quiz)
async def fill_essence(message: Message, state: FSMContext):
    await state.update_data(quiz=message.text)
    await state.set_state(Form.resquiz)
    await message.answer("Введите <b>ожидаемый результат</b>", reply_markup=cancel, parse_mode="HTML")


@router.message(Form.resquiz)
async def fill_expect(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_id_str = str(user_id)  # Преобразуем user_id в строку
    session = Session()
    user_info = session.query(table).filter(table.c.id_telegram == user_id_str).first()
    if user_info:

        await state.update_data(resquiz=message.text)
        data = await state.get_data()
        formatter_text = (
            f"Ваш вопрос\n"
            f"<b>Инициатор:</b> {user_info.Surname} {user_info.Name[0]}. {user_info.Middle_name[0]}.\n"
            f"<b>Суть вопроса:</b> {data['quiz']}\n"
            f"<b>Ожидаемый результат:</b> {data['resquiz']}")
        await message.answer(formatter_text, parse_mode="HTML", reply_markup=cancel)
        await message.answer("Запрос введен верно?", reply_markup=inline.yesnoquiz)
    else:
        await state.clear()
        await message.answer("Ошибка в формировании заявки.")
        await message.answer("Пройдите авторизацию повторно", reply_markup=reply.start_kb)
        await state.set_state(FSMAdmin.phone)