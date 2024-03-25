from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

division_cmd = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Блок «Цифровая трансформация,\n бизнес-процессы и документооборот»", callback_data="block_division"),
        ],
        [
            InlineKeyboardButton(text="Департамент", callback_data="department_division")
        ],
        [
            InlineKeyboardButton(text="Портфель проектов", callback_data="briefcase_division")
        ],
        [
            InlineKeyboardButton(text="Отдел", callback_data="section_division"),
            InlineKeyboardButton(text="Сектор", callback_data="sector_division")
        ],
        [
            InlineKeyboardButton(text="Управление", callback_data="managment_division")
        ]
    ]
)

alphabet_division = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="A-Z, А-М", callback_data="alphabet_an"),
            InlineKeyboardButton(text="Н-Я", callback_data="alphabet_nya")
        ]
    ]
)

send = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="qq"),
            InlineKeyboardButton(text="Установка дедлайна", callback_data="qqq")
        ]

    ]
)