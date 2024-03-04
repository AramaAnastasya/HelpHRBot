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

from kbds import reply
from kbds.inline import get_callback_btns

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()

@user_private_router.message(CommandStart())
async def start_cmd(message:Message, state: FSMContext):
    # Получить информацию о члене чата (пользователе, отправившем сообщение)
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)

    # Вывести имя пользователя
    await bot.send_message(message.chat.id, 
            f"Добрый день, <b>{chat_member.user.first_name}</b>! Я виртуальный HR-помощник.\nВыберите тип обращения.",
            reply_markup=reply.start_kb        
            )
    await state.clear()
 
@user_private_router.message((F.text.lower() == "создать заявку"))
async def menu_cmd(message: types.Message):
    await message.answer(
        "Выберите вид заявки.",
        reply_markup=reply.start_kb2
    )

class transferRequest(StatesGroup):
    name_staff = State()
    post_staff = State()
    division_staff = State()
    is_staff = State()
    goals_count = State()
    goals_staff = State()
    due_date_staff = State()
    results_staff = State()
    fio_changed = State()  
    post_changed = State()
    division_changed = State()
    is_changed = State()
    goals_changed = State()
    goals_count_changed = State()
    due_date_changed = State()
    results_changed = State()
    goal_number = State()



@user_private_router.message(Command(commands=["cancel"]))
@user_private_router.message(F.text.lower() == "отмена заявки")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=reply.start_kb
    )
    await message.answer(
        text="Выберите тип обращения"
    )


@user_private_router.message((F.text.lower() == "заявка на перевод"))
async def transfer_cmd(message: types.Message, state:FSMContext):
    await message.answer(
        "Введите <b>ФИО сотрудника</b>",
        reply_markup=reply.back_start
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
            reply_markup=reply.back_start
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
              reply_markup=reply.back_start
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
              reply_markup=reply.back_start
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
            reply_markup=reply.back_start)
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
            reply_markup=reply.back_start
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
            reply_markup=reply.back_start
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
            reply_markup=reply.back_start
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
                reply_markup=reply.back_start
            )
            await state.set_state(transferRequest.goals_staff)


async def staff_post(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data.get('name_staff')
    post = user_data.get('post_staff')
    division = user_data.get('division_staff')
    is_s = user_data.get('is_staff')

    data = await state.get_data()

    goals_list = data.get("goals_list")
    due_date_list = data.get("due_date_list")
    results_list = data.get("results_list")
    await message.answer(
        text="Проверьте корректность введенных данных."
    )
    await message.answer(
            f"<b>ФИО сотрудника:</b> {name}.\n"
             f"<b>Должность:</b> {post}.\n"
             f"<b>Подразделение: </b>{division}. \n"
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
                    reply_markup=get_callback_btns(
                    btns={
                    'Данные верны': f'yes_application',
                    'Изменить данные': f'no_application',
                    }   
                ))
            else:
                message_text = f"<b>Цель {i + 1}:</b> {goal}\n<b>Срок исполнения:</b> {due_date}\n<b>Ожидаемый результат:</b> {result}"
                await message.answer(message_text)
    else:
        await message.answer(
            "Ошибка", reply_markup=reply.start_kb
        )

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
    await callback.message.answer(
        "Отправлено.", reply_markup=reply.start_kb
    )
    # Сброс состояния и сохранённых данных у пользователя
    await state.clear()

@user_private_router.callback_query(F.data.startswith("stop_application"))
async def stop_app(callback: types.CallbackQuery):
    await callback.message.delete_reply_markup() 
    await callback.message.answer(
        "Выберите тип обращения.", reply_markup=reply.start_kb
    )

@user_private_router.callback_query(F.data.startswith("no_application"))
async def no_app(callback:types.CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Что необходимо изменить?", 
        reply_markup=get_callback_btns(
                btns={
                    'ФИО сотрудника': f'fio_change',
                    'Должность': f'post_change',
                    'Подразделение': f'division_change',
                    'Дата конца ИС': f'is_change',
                    'Цели': f'goals_change',
                }
            ),    
    )

 
@user_private_router.callback_query(F.data.startswith("fio_change"))
async def fio_change(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Введите исправленное <b>ФИО сотрудника</b>", 
    )
    await state.set_state(transferRequest.name_staff)
    await state.update_data({'fio_changed': True})   

@user_private_router.callback_query(F.data.startswith("post_change"))
async def post_change(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Введите исправленную <b>должность сотрудника</b>", 
    )
    await state.set_state(transferRequest.post_staff)
    await state.update_data(post_changed=True)
    
@user_private_router.callback_query(F.data.startswith("division_change"))
async def division_change(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Введите исправленное <b>подразделение сотрудника</b>", 
    )
    await state.set_state(transferRequest.division_staff)
    await state.update_data(division_changed=True)

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




@user_private_router.message((F.text.lower() == "заявка на перевод на другой формат работы"))
async def transfer_to_remote(message: types.Message):
    await message.answer(
        "<i>Заявка на перевод на другой формат работы</i>", reply_markup=types.ReplyKeyboardRemove()
    )

