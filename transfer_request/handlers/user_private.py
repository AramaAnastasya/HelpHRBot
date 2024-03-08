import os
from aiogram import F, types, Router, Bot,Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.formatting import as_list, as_marked_section, Bold,Spoiler #Italic, as_numbered_list и тд 
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from filters.chat_types import ChatTypeFilter

from transfer_request.utils.states import transferRequest
from keyboards import reply
from transfer_request.keyboards.inline import get_callback_btns
from transfer_request.callbacks.callback_transfer import staff_post

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()

 
@user_private_router.message((F.text.lower() == "создать заявку"))
async def menu_cmd(message: types.Message):
    await message.answer(
        "Выберите вид заявки.",
        reply_markup=reply.request
    )


@user_private_router.message((F.text.lower() == "заявка на перевод"))
async def transfer_cmd(message: types.Message, state:FSMContext):
    await message.answer(
        "Введите <b>ФИО сотрудника</b>",
        reply_markup=reply.cancel
    )
    await state.update_data(fio_changed=False)
    await state.set_state(transferRequest.name_staff)


@user_private_router.message(transferRequest.name_staff)
async def cmd_post(message: Message, state: FSMContext):
    await state.update_data(name_staff=message.text)
    data = await state.get_data()
    fio_change = data.get('fio_changed')
    if fio_change == True:  
        await staff_post(message, state)
        await state.update_data(fio_changed=False)
    else:  
        await message.answer(
            "Введите <b>должность сотрудника</b>",
            reply_markup=reply.cancel
        )
        await state.update_data(post_changed=False)
        await state.set_state(transferRequest.post_staff)


@user_private_router.message(transferRequest.post_staff)
async def cmd_division(message: Message, state: FSMContext):
    await state.update_data(post_staff=message.text)
    user_data = await state.get_data()
    post_change = user_data.get('post_changed')
    if post_change == True:  
        await staff_post(message, state)
        await state.update_data(post_changed=False)
    else: 
        await message.answer(
            "Введите <b>подразделение сотрудника</b>",
              reply_markup=reply.cancel
        )
        await state.update_data(division_changed=False)
        await state.set_state(transferRequest.division_staff)

@user_private_router.message(transferRequest.division_staff)
async def cmd_is(message: Message, state: FSMContext):
    await state.update_data(division_staff=message.text)
    user_data = await state.get_data()
    division_change = user_data.get('division_changed')
    if division_change == True: 
        await staff_post(message, state)
        await state.update_data(division_change=False)
    else: 
        await message.answer(
            "Введите <b>дату конца Испытательного Срока</b>",
              reply_markup=reply.cancel
        )
        await state.update_data(is_changed=False)
        await state.set_state(transferRequest.is_staff)

@user_private_router.message(transferRequest.is_staff)
async def cmd_goals(message: Message, state: FSMContext):
    await state.update_data(is_staff=message.text)
    user_data = await state.get_data()
    is_change = user_data.get('is_changed')
    if is_change == True:   
        await staff_post(message, state)
        await state.update_data(is_changed=False)
    else:   
        await message.answer(
            "Введите <b>количество целей</b> на период Испытательного срока",
            reply_markup=reply.cancel)
        await state.update_data(goals_count_changed=False)
        await state.set_state(transferRequest.goals_count)

@user_private_router.message(transferRequest.goals_count)
async def cmd_goals_loop(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число.")
        return
    
    goals_count = int(message.text)
    await state.update_data(goals_count=message.text)
    user_data = await state.get_data()
    goals_count_change = user_data.get('goals_count_changed')
    if goals_count_change == True: 
        await staff_post(message, state)
        await state.update_data(goals_count_changed=False)
    else: 
        for i in range(goals_count):
            await message.answer(
                f"Введите <b>цель {i + 1} на период Испытательного срока</b>",
            reply_markup=reply.cancel
            )
            await state.update_data(goals_changed=False)
            await state.set_state(transferRequest.goals_staff)
            break

@user_private_router.message(transferRequest.goals_staff)
async def cmd_due(message: Message, state: FSMContext):
    goals_staff = message.text
    await state.update_data(goals_staff=message.text)

    data = await state.get_data()

    user_data = await state.get_data()
    goals_change = user_data.get('goals_changed')
    if goals_change == True: 
        # Получение номера цели и шага из данных состояния
        goal_number = data.get("goal_number")
        step = data.get("step")

        # Изменение данных цели в зависимости от шага
        if step == 1:
            # Изменение цели
            goals_list = data.get("goals_list")
            goals_list[goal_number] = message.text

            # Переход к следующему шагу
            await state.update_data({"goal_number": goal_number,"step": 2})

            # Запрос нового срока исполнения
            await message.answer(
                "Введите новый <b>срок исполнения:</b>"
            )
            await state.set_state(transferRequest.due_date_staff)
            await state.update_data(goals_changed = False)
            await state.update_data(due_date_changed=True)
    else: 
        if "goals_list" not in data:
            data["goals_list"] = []
        data["goals_list"].append(goals_staff)

        await state.update_data(data)

        # Переход к следующему этапу цикла
        await state.set_state(transferRequest.due_date_staff)

        # Запрос срока исполнения
        await message.answer(
            "Введите <b>срок исполнения</b>",
            reply_markup=reply.cancel
        )
        await state.update_data(due_date_changed = False)

@user_private_router.message(transferRequest.due_date_staff)
async def cmd_results(message: Message, state: FSMContext):
    due_date_staff = message.text
    await state.update_data(due_date_staff=message.text)

    data = await state.get_data()

    user_data = await state.get_data()
    due_date_change = user_data.get('due_date_changed')

    if due_date_change == True: 

        goal_number = data.get("goal_number")
        step = data.get("step")
        if step == 2:
            due_date_list = data.get("due_date_list")
            due_date_list[goal_number] = due_date_staff

            await state.update_data({"step": 3})

            await message.answer(
                "Введите новый <b>ожидаемый результат:</b> "
            )
            await state.set_state(transferRequest.results_staff)
            await state.update_data(results_changed=True)
            await state.update_data(due_data_changed=False)
    else:
        if "due_date_list" not in data:
            data["due_date_list"] = []
        data["due_date_list"].append(due_date_staff)

        await state.update_data(data)
        await state.set_state(transferRequest.results_staff)
        await message.answer(
            "Введите <b>ожидаемый результат</b>",
            reply_markup=reply.cancel
        )
        await state.update_data(results_changed=False)

@user_private_router.message(transferRequest.results_staff)
async def cmd_results_loop(message: Message, state: FSMContext):
    results_staff = message.text
    await state.update_data(results_staff=message.text)

    data = await state.get_data()

    user_data = await state.get_data()
    results_change = user_data.get('results_changed')

    if results_change == True: 

        goal_number = data.get("goal_number")
        step = data.get("step")
        if step == 3:

            results_list = data.get("results_list")
            results_list[goal_number] = message.text

            await state.update_data(data)

            await message.answer(
                f"Данные цели {goal_number+1} изменены."
            )
            await staff_post(message, state)
            await state.update_data(results_changed=False)
    else:
        if "results_list" not in data:
            data["results_list"] = []
        data["results_list"].append(results_staff)
        await state.update_data(data)

        user_data = await state.get_data()
        data["goals_count"] = int(user_data.get('goals_count'))

        goals_count = data["goals_count"]

        if "goals_staff_count" in data:
            current_goal = data["goals_staff_count"]
        else:
            current_goal = 0

        if current_goal == goals_count-1:
            # Завершение цикла и переход к следующему состоянию
            await message.answer(f"Цели введены успешно.")
            await staff_post(message, state)
        else:
            # Переход к следующему этапу цикла
            if "goals_staff_count" in data:
                data["goals_staff_count"] += 1
            else:
                data["goals_staff_count"] = 1
            await state.set_data(data)
            await message.answer(
                f"Введите <b>цель {data['goals_staff_count'] + 1} на период Испытательного срока</b>",
                reply_markup=reply.cancel
            )
            await state.set_state(transferRequest.goals_staff)
