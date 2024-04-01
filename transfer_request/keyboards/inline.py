from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_callback_btns(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (2,2)):

    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()

send_transfer = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrap_trans"),
            InlineKeyboardButton(text="Установка дедлайна", callback_data="set_deadline")
        ]

    ]
)

send_transferAct = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrap_trans"),
            InlineKeyboardButton(text="Изменить дедлайн", callback_data="update_deadline")
        ],
        [
            InlineKeyboardButton(text="Отметить выполненной", callback_data="click")
        ]
    ]
)