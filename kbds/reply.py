from aiogram.types import KeyboardButtonPollType, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Создать заявку"),
            KeyboardButton(text="Задать вопрос"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Что Вас интересует?'
)

del_kbd = ReplyKeyboardRemove()


start_kb2 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Заявка на перевод"),
            KeyboardButton(text="Заявка на перевод на другой формат работы"),
        ],
        {
            KeyboardButton(text="Заявка на согласование ЗП"),
            KeyboardButton(text="Общая форма"),
        },
        [
            KeyboardButton(text="Отмена заявки"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Что Вас интересует?'
)

back_start = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отмена заявки"),
        ]
    ],
    resize_keyboard=True,
)


button_kb = ReplyKeyboardMarkup(
     keyboard=[
        [
            KeyboardButton(text="Да", ),
            KeyboardButton(text="Нет"),
        ]
    ],
    resize_keyboard=True,
)


transfer_kb = ReplyKeyboardMarkup(
     keyboard=[
        [
            KeyboardButton(text="ФИО сотрудника"),
            KeyboardButton(text="Должность"),
            KeyboardButton(text="Подразделение"),
        ],
        {
            KeyboardButton(text="Дата конца ИС"),
            KeyboardButton(text="Цели"),
            KeyboardButton(text="Срок исполнения"),
        },
        [
            KeyboardButton(text="Ожидаемый результат"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Что хотите изменить?'
)