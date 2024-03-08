from aiogram.types import KeyboardButtonPollType, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Подать заявку"),
            KeyboardButton(text="Задать вопрос")
        ]
    ],
    resize_keyboard=True, 
    input_field_placeholder='Что Вас интересует?'
)

cancel = ReplyKeyboardMarkup( 
    keyboard=[
        [
            KeyboardButton(text="Отменить заявку")
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
            KeyboardButton(text="Заявка на согласование ЗП")
        ],
        [
            KeyboardButton(text="Заявка на перевод другой формат работы")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Что Вас интересует?'

)