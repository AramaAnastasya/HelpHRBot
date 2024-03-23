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
from sqlalchemy import update

from filters.chat_types import ChatTypeFilter
from avtorization.utils.states import FSMAdmin
from keyboards import reply

user_login_router = Router()
user_login_router.message.filter(ChatTypeFilter(["private"]))


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



@user_login_router.message(FSMAdmin.phone)
async def cmd_is(message: types.Message, state: FSMContext):
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    session = Session()

    if message.contact:
        phone_number = message.contact.phone_number
        phone_number = phone_number.replace('+', '')
        existing_record = session.query(table).filter(table.c.Phone_number == phone_number).first()
        if existing_record:
            # Обновляем значение столбца id_telegram для найденной записи
            session.execute(
                update(table)
                .where(table.c.Phone_number == phone_number)
                .values(id_telegram=chat_member.user.id)
            )
            session.commit()
            await state.clear()
            await message.reply(f"Вы успешно авторизованы!")
            await message.answer("Выберите тип обращения.", reply_markup=reply.main)           
        else:
            await message.reply("Ошибка авторизации. Пожалуйста, отправьте свой контактный номер телефона.")
        
    elif message.text and message.text != "777":

        existing_record = session.query(table).filter(table.c.Phone_number == message.text).first()

        if existing_record:
            # Обновляем значение столбца id_telegram для найденной записи
            session.execute(
                update(table)
                .where(table.c.Phone_number == message.text)
                .values(id_telegram=chat_member.user.id)
            )
            session.commit()  # Фиксируем изменения в базе данных

            await state.clear()
            await message.reply(f"Вы успешно авторизованы!")
            await message.answer("Выберите тип обращения.", reply_markup=reply.main)
        else:
            await message.reply("Ошибка авторизации. Пожалуйста, отправьте свой контактный номер телефона.")

    elif message.text == "777":
        
        existing_record = session.query(table).filter(table.c.Phone_number == message.text,table.c.Surname == "Минин", table.c.Name == "Вася", table.c.Middle_name == "роз").first()
        if message.text:
            # Обновляем значение столбца id_telegram для найденной записи
            session.execute(
                update(table)
                .where(table.c.Phone_number == message.text)
                .values(id_telegram=chat_member.user.id)
            )

            session.commit()
            await state.clear()
            await message.reply(f"Вы успешно авторизованы в HR!")
            await message.answer( "Выбирете нужную категорию", reply_markup=reply.hr)
    else:
            await message.reply("Ошибка авторизации. Пожалуйста, отправьте свой контактный номер телефона.")
    session.close()
