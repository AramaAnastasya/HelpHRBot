from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

yesno = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="yes"),
            InlineKeyboardButton(text="Нет", callback_data="no")
        ]

    ]
)

yesnoquiz = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="yes"),
            InlineKeyboardButton(text="Нет", callback_data="noquiz")
        ]

    ]
)


hr = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="yeshr"),
            InlineKeyboardButton(text="Нет", callback_data="nohr")
        ]

    ]
)

change = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Суть обращения", callback_data="essenseedi"),
            InlineKeyboardButton(text="Ожидаемый результат", callback_data="expectedi")
        ]

    ]
)

changequiz = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Суть вопроса", callback_data="quizedit"),
            InlineKeyboardButton(text="Ожидаемый результат", callback_data="resquizedit")
        ]

    ]
)
