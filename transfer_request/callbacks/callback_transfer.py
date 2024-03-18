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

from utils.states import Employee
from transfer_request.utils.states import transferRequest
from keyboards import reply
from transfer_request.keyboards.inline import get_callback_btns

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()



async def staff_post(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data.get('search_name')
    division = user_data.get('search_division')
    post = user_data.get('search_post')
    is_s = user_data.get('is_staff')

    data = await state.get_data()

    goals_list = data.get("goals_list")
    due_date_list = data.get("due_date_list")
    results_list = data.get("results_list")
    await message.answer(
        "Ваша заявка на перевод:\n"
        f"<b>Инициатор:</b> \n"
        f"<b>Сотрудник:</b> {name}, {division}, {post}\n"
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
        "Заявка успешно отправлена!"
    )
    await callback.message.answer(
        "Информация о сроке решения будет отправлена Вам в ближайшее время.", reply_markup=reply.main
    )
    # Сброс состояния и сохранённых данных у пользователя
    await state.clear()

@user_private_router.callback_query(F.data.startswith("stop_application"))
async def stop_app(callback: types.CallbackQuery):
    await callback.message.delete_reply_markup() 
    await callback.message.answer(
        "Выберите тип обращения.", reply_markup=reply.main
    )

@user_private_router.callback_query(F.data.startswith("no_application"))
async def no_app(callback:types.CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        "Что необходимо изменить?", 
        reply_markup=get_callback_btns(
                btns={
                    'ФИО сотрудника': f'search_name_change',
                    'Подразделение': f'search_division_change',
                    'Должность': f'search_post_change',
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




