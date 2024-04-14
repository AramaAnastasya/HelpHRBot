from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_callback_btns(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (2,1)):

    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()

send_zp = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrap_zp"),
            InlineKeyboardButton(text="Установка дедлайна", callback_data="set_deadline")
        ]
    ]
)

send_zpAct = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrap_zp"),
            InlineKeyboardButton(text="Изменить дедлайн", callback_data="set_deadline")
        ],
        [
            InlineKeyboardButton(text="Отметить выполненной", callback_data="click")
        ]
    ]
)

send_zp_d = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Свернуть", callback_data="unwrap_zp"),
            InlineKeyboardButton(text="Установка дедлайна", callback_data="set_deadline")
        ]
    ]
)

send_zpAct_d = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Свернуть", callback_data="unwrap_zp"),
            InlineKeyboardButton(text="Изменить дедлайн", callback_data="set_deadline")
        ],
        [
            InlineKeyboardButton(text="Отметить выполненной", callback_data="click")
        ]
    ]
)

changeInf = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Сотрудник", callback_data="search_changed")        
        ],
        [
            InlineKeyboardButton(text="Действующая сумма", callback_data="current_amount_change"),
            InlineKeyboardButton(text="Предлагаемая сумма", callback_data="proposed_amount_change")
        ],
        [
            InlineKeyboardButton(text="Причина перевода", callback_data="reasons_change")

        ]
    ]
)
