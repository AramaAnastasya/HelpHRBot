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

from filters.chat_types import ChatTypeFilter

from utils.states import Employee
from task_ZP.utils.states import taskZP
from different_format.utils.states import FormTransf
from transfer_request.utils.states import transferRequest
from keyboards import reply
from keyboards.inline import division_cmd, alphabet_division
from task_ZP.callbacks.callback_task_ZP import agreement_ZP
from transfer_request.callbacks.callback_transfer import staff_post
from different_format.handlers.user_diff_format import diff_format
from different_format.keyboards.inline import placenowkb
from transfer_request.keyboards.inline import get_callback_btns

from config import DATABASE_URI

# Создайте подключение к базе данных
engine = create_engine(DATABASE_URI)

# Создайте сессию для работы с базой данных
Session = sessionmaker(bind=engine)

# Создайте таблицу, из которой будут извлекаться данные
metadata = MetaData()
table = Table('employee', metadata, autoload_with=engine)
table_division = Table('Division', metadata, autoload_with=engine)
table_post = Table('Position', metadata, autoload_with=engine)

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()

@user_private_router.message((F.text.lower() == "заявка на перевод")) 
async def transfer_cmd(message: types.Message, state:FSMContext):
    await state.update_data(request="заявка на перевод")
    await message.answer(
        "Введите <b>ФИО сотрудника</b>\n<i>Пример входных данных:</i> Иванов Иван Иванович",
        reply_markup=reply.cancel
    )
    await state.set_state(Employee.search_bd)
    await state.update_data({'search_change': False}) 

@user_private_router.message((F.text.lower() == "заявка на согласование зп"))
async def task_ZP_cmd(message: types.Message, state:FSMContext):
    await state.update_data(request="заявка на согласование зп")
    await message.answer(
        "Выполните поиск сотрудника или введите его данные вручную",
        reply_markup=reply.employee_search
    )
    await state.update_data({'search_change': False}) 

@user_private_router.message(F.text == "Заявка на перевод на другой формат работы")
async def transfer_format(message: Message, state: FSMContext):
    await state.update_data(request="Заявка на перевод на другой формат работы")
    await message.answer(
        "Введите <b>ФИО сотрудника</b>\n<i>Пример входных данных:</i> Иванов Иван Иванович",
        reply_markup=reply.cancel
    )
    await state.set_state(Employee.search_bd)
    await state.update_data({'search_change': False}) 

@user_private_router.callback_query(F.data.startswith("search_changed"))
async def search_fio_change(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    data = await state.get_data()
    request_change = data.get('request')
    if request_change == "заявка на перевод":
        await callback.message.answer(
        "Введите <b>ФИО сотрудника</b>\n<i>Пример входных данных:</i> Иванов Иван Иванович",
        reply_markup=reply.cancel
        )
        await state.set_state(Employee.search_bd)
    if request_change == "заявка на согласование зп":
        await callback.message.answer(
        "Выполните поиск сотрудника или введите его данные вручную",
        reply_markup=reply.employee_search
    )
    if request_change == "Заявка на перевод на другой формат работы":
        await callback.message.answer(
                "Введите <b>ФИО сотрудника</b>\n<i>Пример входных данных:</i> Иванов Иван Иванович",
                reply_markup=reply.cancel
            )
    await state.set_state(Employee.search_bd)
    
    await state.update_data({'search_change': True})   

@user_private_router.message((F.text.lower() == "добавить кандидата"))
async def cmd_name(message: types.Message, state:FSMContext):
    await message.answer(
        "Введите <b>ФИО сотрудника</b>",
        reply_markup=reply.cancel
    )
    await state.set_state(Employee.search_name)
    await state.update_data(search = True)

@user_private_router.message(Employee.search_name)
async def cmd_division(message: Message, state: FSMContext):
    await state.update_data(search_name=message.text)
    await message.answer(
            "Ввод <b>подразделения</b>"
        )
    await message.answer(
        "Выберите подкатегорию",
            reply_markup=division_cmd
    )
 

@user_private_router.callback_query(F.data.startswith("block_division"))
async def block_divis(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    session = Session()
    result = session.query(table_division).filter(table_division.c.Division == "Блок «Цифровая трансформация, бизнес-процессы и документооборот»").first()
    result_Post = session.query(table_post).filter(table_post.c.ID_Division == int(result.id)).all()
    await state.update_data(search_division=int(result.id))
    await callback.message.answer(
        "Вы выбрали <b>Блок \"Цифровая трансформация, бизнес-процессы и документооборот\"</b>",
        reply_markup=reply.cancel
    )
    text = "<b>Введите должность из списка</b>\n"
    for row in result_Post:
        text += f"{row.Position}\n"
    await callback.message.answer(text)
    session.close()
    await state.set_state(Employee.search_post)

@user_private_router.callback_query(F.data.startswith("department_division"))
async def department_divis(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    session = Session()
    result = session.query(table_division).filter(table_division.c.Division.contains("Департамент")).order_by(table_division.c.Division).all()
    await state.update_data(division_input="Департамент")
    await callback.message.answer(
        "Вы выбрали <b>Департамент</b>",
        reply_markup=reply.cancel
    )
    text = "<b>Введите подразделение из списка</b>\n"
    for row in result:
        text += f"{row.Division}\n"
    await callback.message.answer(text)
    session.close()
    await state.set_state(Employee.search_division)
    
@user_private_router.callback_query(F.data.startswith("briefcase_division"))
async def department_divis(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    session = Session()
    result = session.query(table_division).filter(table_division.c.Division.contains("Портфель проектов")).order_by(table_division.c.Division).all()
    await state.update_data(division_input="Портфель проектов")
    await callback.message.answer(
        "Вы выбрали <b>Портфель проектов</b>",
        reply_markup=reply.cancel
    )
    text = "<b>Введите подразделение из списка</b>\n"
    for row in result:
        text += f"{row.Division}\n"
    await callback.message.answer(text)
    session.close()
    await state.set_state(Employee.search_division)

@user_private_router.callback_query(F.data.startswith("proect_division"))
async def department_divis(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    session = Session()
    result = session.query(table_division).filter(table_division.c.Division.contains("Проектный офис")).order_by(table_division.c.Division).first()
    result_Post = session.query(table_post).filter(table_post.c.ID_Division == int(result.id)).all()
    await state.update_data(search_division=int(result.id))
    await callback.message.answer(
        "Вы выбрали <b>Проектный офис</b>",
        reply_markup=reply.cancel
    )
    text = "<b>Введите должность из списка</b>\n"
    for row in result_Post:
        text += f"{row.Position}\n"
    await callback.message.answer(text)
    session.close()
    await state.set_state(Employee.search_post)


@user_private_router.callback_query(F.data.startswith("section_division"))
async def department_divis(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await state.update_data(division_input="Отдел")
    await callback.message.answer(
        "Вы выбрали <b>Отдел</b>",
        reply_markup=alphabet_division
    )


@user_private_router.callback_query(F.data.startswith("alphabet_an"))
async def department_divis(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    session = Session()
    result = session.query(table_division).filter(table_division.c.Division.contains("Отдел")).order_by(table_division.c.Division).all()
    await state.update_data(division_input="Отдел")

    text = "<b>Введите подразделение из списка</b>\n"
    for row in result:
        division = row.Division.split()
        if 'A' <= division[1] <= 'Z' or 'а' <= division[1] <= 'н':
            text += f"{row.Division}\n"
        
    await callback.message.answer(text)
    session.close()
    await state.set_state(Employee.search_division)

@user_private_router.callback_query(F.data.startswith("alphabet_nya"))
async def department_divis(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    session = Session()
    result = session.query(table_division).filter(table_division.c.Division.contains("Отдел")).order_by(table_division.c.Division).all()
    await state.update_data(division_input="Отдел")

    text = "<b>Введите подразделение из списка</b>\n"
    for row in result:
        division = row.Division.split()
        if 'м' <= division[1] <= 'я':
            text += f"{row.Division}\n"
        
    await callback.message.answer(text)
    session.close()
    await state.set_state(Employee.search_division)

@user_private_router.callback_query(F.data.startswith("sector_division"))
async def department_divis(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    session = Session()
    result = session.query(table_division).filter(table_division.c.Division.contains("Сектор")).order_by(table_division.c.Division).all()
    await state.update_data(division_input="Сектор")
    await callback.message.answer(
        "Вы выбрали <b>Сектор</b>",
        reply_markup=reply.cancel
    )
    text = "<b>Введите подразделение из списка</b>\n"
    for row in result:
        text += f"{row.Division}\n"
    await callback.message.answer(text)
    session.close()
    await state.set_state(Employee.search_division)

@user_private_router.callback_query(F.data.startswith("managment_division"))
async def department_divis(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    session = Session()
    result = session.query(table_division).filter(table_division.c.Division.contains("Управление")).order_by(table_division.c.Division).all()
    await state.update_data(division_input="Управление")
    await callback.message.answer(
        "Вы выбрали <b>Управление</b>",
        reply_markup=reply.cancel
    )
    text = "<b>Введите подразделение из списка</b>\n"
    for row in result:
        text += f"{row.Division}\n"
    await callback.message.answer(text)
    session.close()
    await state.set_state(Employee.search_division)




@user_private_router.message(Employee.search_division)
async def depatr_divis(message:Message, state:FSMContext):
    user_data = await state.get_data()
    division_input = user_data.get('division_input')
    session = Session()
    result = session.query(table_division).filter(table_division.c.Division == message.text, table_division.c.Division.contains(division_input)).first()
    if result:    
        result_Post = session.query(table_post).filter(table_post.c.ID_Division == int(result.id)).all()
        await state.update_data(search_division=int(result.id))
        await message.answer(
        f"Вы выбрали <b>{result.Division}</b>",
            reply_markup=reply.cancel
        )
        if result_Post:
            text = "<b>Введите должность из списка</b>\n"
            for row in result_Post:
                text += f"{row.Position}\n"
            await message.answer(text)    
            await state.set_state(Employee.search_post)
            session.close()        
    else:
        await message.answer(
            "Совпадения не найдены!"
        )
        await message.answer(
            "Проверьте поисковые данные."
        )
    
    


@user_private_router.message(Employee.search_post)
async def cmd_output(message: Message, state: FSMContext):
    user_data = await state.get_data()
    search_change = user_data.get('search_change')
    request_change = user_data.get('request')
    name = user_data.get('search_name')
    division = user_data.get('search_division')
    
    session = Session()
    result = session.query(table_post).filter(table_post.c.Position == message.text, table_post.c.ID_Division == division).first()
    if result:
        await state.update_data(search_post=message.text)       
        result_Division = session.query(table_division).filter(table_division.c.id == int(division)).first()
        await message.answer(
            "Сотрудник:\n"
            f"<b>ФИО:</b> {name}\n"
            f"<b>Подразделение: </b>{result_Division.Division}\n"
            f"<b>Должность:</b> {result.Position}\n",
        )
        if request_change == "заявка на перевод" and search_change == False:
            await message.answer(
            "Введите <b>дату конца Испытательного Срока</b>",
              reply_markup=reply.cancel
            )
            await state.update_data(is_changed=False)
            await state.set_state(transferRequest.is_staff)

        elif request_change == "заявка на согласование зп" and search_change == False:
            await message.answer(
            "Введите <b>действующую сумму</b>",
            reply_markup=reply.cancel
            )
            await state.update_data(current_amount_changed=False)
            await state.set_state(taskZP.current_amount)

        elif request_change == "Заявка на перевод на другой формат работы" and search_change == False:
            await state.set_state(FormTransf.placenow)
            await message.answer(
            "Выберите <b>формат работы на данный момент</b>",
            reply_markup=placenowkb,
            parse_mode="HTML",
            )
        elif search_change == True:

            if request_change == "заявка на перевод":
                await staff_post(message, state)
                await state.update_data(search_change=False)
            if request_change == "заявка на согласование зп":
                await agreement_ZP(message, state)
                await state.update_data(search_change=False)
            if request_change == "Заявка на перевод на другой формат работы":
                await diff_format(message, state) 
                await state.update_data(search_change=False)
    else:
        await message.answer(
            "Совпадения не найдены!"
        )
        await message.answer(
            "Проверьте введенные данные."
        )
    

@user_private_router.message((F.text.lower() == "поиск действующего сотрудника"))
async def search_name_cmd(message: types.Message, state:FSMContext):
    await message.answer(
        "Введите <b>ФИО сотрудника</b>\n<i>Пример входных данных:</i> Иванов Иван Иванович",
        reply_markup=reply.cancel
    )
    await state.set_state(Employee.search_bd)
    await state.update_data(search = False)

@user_private_router.message(Employee.search_bd)
async def cmd_search(message: Message, state: FSMContext):
    # Получите сессию для работы с базой данных
    session = Session()
    emlpoyee_name = message.text.split()
    if len(emlpoyee_name) == 3:

        # Получите введенные переменные от пользователя
        word1 = message.text.split()[0]
        word2 = message.text.split()[1]
        word3 = message.text.split()[2]
        
        # Выберите данные из таблицы с использованием фильтрации
        result = session.query(table).all()
        data = await state.get_data()
        data["list"] = []
        
        for row in result:
            surname = row.Surname.lower() == word1.lower() or row.Surname.lower() ==  word2.lower() or row.Surname.lower() ==  word3.lower()
            name = row.Name.lower() ==  word1.lower() or row.Name.lower() == word2.lower() or row.Name.lower() ==  word3.lower()
            middle_name = row.Middle_name.lower() ==  word1.lower() or row.Middle_name.lower() == word2.lower() or row.Middle_name.lower() ==  word3.lower()
            if surname == True and name == True and middle_name == True:
                data["list"].append(row.id)
        list = data.get("list")
        if len(list) != 0:
            for i, empl in enumerate(list):
                result = session.query(table).filter(table.c.id == empl).first()
                await message.answer(
                    f"<b>ФИО:</b> {result.Surname} {result.Name} {result.Middle_name}\n<b>Подразделение: </b>{result.Division}\n<b>Должность:</b> {result.Position}", 
                    reply_markup=get_callback_btns(
                    btns={
                        f"Выбрать": f"select_{result.id}"
                }
                ))    
        
        elif len(list) == 0:
            await message.answer(
                "Совпадения не найдены!"
            )
            await message.answer(
                "Проверьте поисковые данные"
            )
        
        # Закройте сессию
        session.close()
    else:
        await message.answer(
            "Введите ФИО сотрудника в формате: <i>Иванов Иван Иванович</i>"
        )

@user_private_router.callback_query(F.data.startswith("select_"))
async def choice_employee(callback: types.CallbackQuery, state: FSMContext):
    # Получение номера цели из данных обратного вызова   
    await state.update_data(search_bd = int(callback.data.split("_")[1]))
    user_data = await state.get_data()
    search_bd = user_data.get('search_bd')
    data = await state.get_data()
    request_change = data.get('request')
    search_change = data.get('search_change')
    await callback.message.delete_reply_markup()
    if request_change == "заявка на перевод" and search_change == False:
        await callback.message.answer(
        f"Сотрудник успешно выбран!"
    )
        await callback.message.answer(
        "Введите <b>дату конца Испытательного Срока</b> в формате: <i>01.01.2000</i>",
            reply_markup=reply.cancel
        )
        await state.update_data(is_changed=False)
        await state.set_state(transferRequest.is_staff)

    elif request_change == "заявка на согласование зп" and search_change == False:
        await callback.message.answer(
        f"Сотрудник успешно выбран!"
    )
        await callback.message.answer(
        "Введите <b>действующую сумму</b>",
        reply_markup=reply.cancel
        )
        await state.update_data(current_amount_changed=False)
        await state.set_state(taskZP.current_amount)

    elif request_change == "Заявка на перевод на другой формат работы" and search_change == False:
        await callback.message.answer(
        f"Сотрудник успешно выбран!"
    )
        await state.set_state(FormTransf.placenow)
        await callback.message.answer(
        "Выберите <b>формат работы на данный момент</b>",
        reply_markup=placenowkb,
        parse_mode="HTML",
        )
    elif search_change == True:
        await callback.message.answer(
        f"Сотрудник успешно изменен!" 
        )
        await search_cmd(callback.message, state)
        


@user_private_router.channel_post(F.text ==  "Сотрудник успешно изменен!")
async def search_cmd(message:Message, state:FSMContext):
    data = await state.get_data()
    request_change = data.get('request')
    if request_change == "заявка на перевод":
        await staff_post(message, state)
        await state.update_data(search_change=False)
    if request_change == "заявка на согласование зп":
        await agreement_ZP(message, state)
        await state.update_data(search_change=False)
    if request_change == "Заявка на перевод на другой формат работы":
        await diff_format(message, state) 
        await state.update_data(search_change=False)
 
   