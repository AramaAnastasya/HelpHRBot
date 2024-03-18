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

from filters.chat_types import ChatTypeFilter

from utils.states import Employee
from task_ZP.utils.states import taskZP
from different_format.utils.states import FormTransf
from transfer_request.utils.states import transferRequest
from keyboards import reply
from task_ZP.callbacks.callback_task_ZP import agreement_ZP
from transfer_request.callbacks.callback_transfer import staff_post
from different_format.handlers.user_diff_format import diff_format
from different_format.keyboards.inline import placenowkb

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()

@user_private_router.message((F.text.lower() == "заявка на перевод"))
async def transfer_cmd(message: types.Message, state:FSMContext):
    await state.update_data(request="заявка на перевод")
    await message.answer(
        "Выполните поиск сотрудника или введите его данные вручную",
        reply_markup=reply.employee_search
    )

@user_private_router.message((F.text.lower() == "заявка на согласование зп"))
async def transfer_cmd(message: types.Message, state:FSMContext):
    await state.update_data(request="заявка на согласование зп")
    await message.answer(
        "Выполните поиск сотрудника или введите его данные вручную",
        reply_markup=reply.employee_search
    )

@user_private_router.message(F.text == "Заявка на перевод на другой формат работы")
async def fill_transfer(message: Message, state: FSMContext):
    await state.update_data(request="Заявка на перевод на другой формат работы")
    await message.answer(
        "Выполните поиск сотрудника или введите его данные вручную",
        reply_markup=reply.employee_search
    )


@user_private_router.message((F.text.lower() == "ввести вручную"))
async def transfer_cmd(message: types.Message, state:FSMContext):
    await message.answer(
        "Введите <b>ФИО сотрудника</b>",
        reply_markup=reply.cancel
    )
    await state.update_data(search_name_chg=False)
    await state.set_state(Employee.search_name)

@user_private_router.message(Employee.search_name)
async def cmd_division(message: Message, state: FSMContext):
    await state.update_data(search_name=message.text)
    user_data = await state.get_data()
    name_change = user_data.get('search_name_chg')
    request_change = user_data.get('request')
    if name_change == True:  
        if request_change == "заявка на перевод":
            await staff_post(message, state)
            await state.update_data(search_name_chg=False)
        if request_change == "заявка на согласование зп":
            await agreement_ZP(message, state)
            await state.update_data(search_name_chg=False)
        if request_change == "Заявка на перевод на другой формат работы":
            await diff_format(message, state) 
            await state.update_data(search_name_chg=False)
    else: 
        await message.answer(
            "Введите <b>подразделение</b>",
              reply_markup=reply.cancel
        )
        await state.update_data(search_division_chg=False)
        await state.set_state(Employee.search_division)

@user_private_router.message(Employee.search_division)
async def cmd_post(message: Message, state: FSMContext):
    await state.update_data(search_division=message.text)
    data = await state.get_data()
    division_change = data.get('search_division_chg')
    request_change = data.get('request')   
    if division_change == True:  
        if request_change == "заявка на перевод":
            await staff_post(message, state)
            await state.update_data(search_division_chg=False)
        if request_change == "заявка на согласование зп":
            await agreement_ZP(message, state)
            await state.update_data(search_division_chg=False)
        if request_change == "Заявка на перевод на другой формат работы":
            await diff_format(message, state) 
            await state.update_data(search_division_chg=False)
    else:  
        await message.answer(
            "Введите <b>должность</b>",
            reply_markup=reply.cancel
        )
        await state.update_data(search_post_chg=False)
        await state.set_state(Employee.search_post)


@user_private_router.message(Employee.search_post)
async def cmd_post(message: Message, state: FSMContext):
    await state.update_data(search_post=message.text)
    data = await state.get_data()
    post_change = data.get('search_post_chg')
    request_change = data.get('request')
    if post_change == True:  
        if request_change == "заявка на перевод":
            await staff_post(message, state)
            await state.update_data(search_post_chg=False)
        if request_change == "заявка на согласование зп":
            await agreement_ZP(message, state)
            await state.update_data(search_post_chg=False)
        if request_change == "Заявка на перевод на другой формат работы":
            await diff_format(message, state) 
            await state.update_data(search_post_chg=False)
        
    else:  
        user_data = await state.get_data()
        name = user_data.get('search_name')
        division = user_data.get('search_division')
        post = user_data.get('search_post')
        await message.answer(
            "Сотрудник:\n"
            f"<b>ФИО:</b> {name}\n"
            f"<b>Подразделение: </b>{division}\n"
            f"<b>Должность:</b> {post}\n",
        )
        if request_change == "заявка на перевод":
            await message.answer(
            "Введите <b>дату конца Испытательного Срока</b>",
              reply_markup=reply.cancel
            )
            await state.update_data(is_changed=False)
            await state.set_state(transferRequest.is_staff)

        if request_change == "заявка на согласование зп":
            await message.answer(
            "Введите <b>действующую сумму</b>",
            reply_markup=reply.cancel
            )
            await state.update_data(current_amount_changed=False)
            await state.set_state(taskZP.current_amount)

        if request_change == "Заявка на перевод на другой формат работы":
            await state.set_state(FormTransf.placenow)
            await message.answer(
            "Выберите <b>формат работы на данный момент</b>",
            reply_markup=placenowkb,
            parse_mode="HTML",
            )

@user_private_router.callback_query(F.data.startswith("search_name_change"))
async def fio_change(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Введите исправленное <b>ФИО сотрудника</b>", 
    )
    await state.set_state(Employee.search_name)
    await state.update_data({'search_name_chg': True})   

@user_private_router.callback_query(F.data.startswith("search_post_change"))
async def post_change(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Введите исправленную <b>должность сотрудника</b>", 
    )
    await state.set_state(Employee.search_post)
    await state.update_data(search_post_chg=True)
    
@user_private_router.callback_query(F.data.startswith("search_division_change"))
async def division_change(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Введите исправленное <b>подразделение сотрудника</b>", 
    )
    await state.set_state(Employee.search_division)
    await state.update_data(search_division_chg=True)
 

@user_private_router.message((F.text.lower() == "поиск сотрудника"))
async def transfer_cmd(message: types.Message, state:FSMContext):
    await message.answer(
        "Введите <b>ФИО сотрудника</b>",
        reply_markup=reply.cancel
    )
    await state.update_data(search_name_chg=False)
    await state.set_state(Employee.search_bd)

@user_private_router.message((F.text.lower() == "поиск сотрудника"))
async def transfer_cmd(message: types.Message, state:FSMContext):
    await message.answer(
        "Введите <b>ФИО сотрудника</b>",
        reply_markup=reply.cancel
    )
    await state.update_data(search_name_chg=False)
    await state.set_state(Employee.search_bd)

@user_private_router.message(Employee.search_bd)
async def cmd_post(message: Message, state: FSMContext):
    await state.update_data(search_name=message.text)
    data = await state.get_data()
    name_change = data.get('search_name_chg')
    request_change = data.get('request')
    # if name_change == True:  
    #     if request_change == "заявка на перевод":
    #         await staff_post(message, state)
    #         await state.update_data(search_name_chg=False)
    #     if request_change == "заявка на согласование зп":
    #         await agreement_ZP(message, state)
    #         await state.update_data(search_name_chg=False)
    #     if request_change == "Заявка на перевод на другой формат работы":
    #         await diff_format(message, state) 
    #         await state.update_data(search_name_chg=False)
    # else:  
    await message.answer(
            "Совпадения:",
            reply_markup=reply.cancel
        )
    await message.answer(
        "Сотрудник успешно выбран!"
    )
    if request_change == "заявка на перевод":
        await message.answer(
        "Введите <b>дату конца Испытательного Срока</b>",
            reply_markup=reply.cancel
        )
        await state.update_data(is_changed=False)
        await state.set_state(transferRequest.is_staff)

    if request_change == "заявка на согласование зп":
        await message.answer(
        "Введите <b>действующую сумму</b>",
        reply_markup=reply.cancel
        )
        await state.update_data(current_amount_changed=False)
        await state.set_state(taskZP.current_amount)

    if request_change == "Заявка на перевод на другой формат работы":
        await state.set_state(FormTransf.placenow)
        await message.answer(
        "Выберите <b>формат работы на данный момент</b>",
        reply_markup=placenowkb,
        parse_mode="HTML",
        )