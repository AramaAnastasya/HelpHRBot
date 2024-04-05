from aiogram.types import KeyboardButtonPollType, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Подать заявку"),
            KeyboardButton(text="Задать вопрос")
        ],
         [
            KeyboardButton(text="Отправленные заявки")
        ]
    ],
    resize_keyboard=True, 
    input_field_placeholder='Что Вас интересует?'
)

cancel = ReplyKeyboardMarkup( 
    keyboard=[
        [
            KeyboardButton(text="Отменить заявку ❌")
        ]
    ],
    resize_keyboard=True,

)


request = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Заявка на перевод"),
            KeyboardButton(text="Общая форма")
        ],
        [
            KeyboardButton(text="Заявка на согласование ЗП"),
            KeyboardButton(text="Заявка на перевод на другой формат работы")
        ],
        [
            KeyboardButton(text="Отменить заявку ❌")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Что Вас интересует?'

)
start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отправить номер ☎️", request_contact=True)
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Что Вас интересует?'
)

employee_search = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Поиск сотрудника"),
            KeyboardButton(text="Ввести вручную"),
        ],
        [
            KeyboardButton(text="Отменить заявку ❌"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Что Вас интересует?'
)

hr = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Актуальные задачи"),
            KeyboardButton(text="Новые задачи"),
            KeyboardButton(text="Статистика"),
        ]
    ],
    resize_keyboard=True
)
