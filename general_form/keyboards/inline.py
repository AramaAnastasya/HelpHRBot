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
            InlineKeyboardButton(text="Да", callback_data="yesquiz"),
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

hrquiz = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="yeshrquiz"),
            InlineKeyboardButton(text="Нет", callback_data="nohrquiz")
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

send = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrap_send"),
            InlineKeyboardButton(text="Установка дедлайна", callback_data="set_deadline")
        ] 
    ]
)

sendAct = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrap_send"),
            InlineKeyboardButton(text="Изменить дедлайн", callback_data="set_deadline")
        ],
        [
            InlineKeyboardButton(text="Отметить выполненной", callback_data="click")
        ]
    ]
)

send_d = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Свернуть", callback_data="unwrap_send"),
            InlineKeyboardButton(text="Установка дедлайна", callback_data="set_deadline")
        ] 
    ]
)

sendAct_d = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Свернуть", callback_data="unwrap_send"),
            InlineKeyboardButton(text="Изменить дедлайн", callback_data="set_deadline")
        ],
        [
            InlineKeyboardButton(text="Отметить выполненной", callback_data="click")
        ]
    ]
)

sendquiz = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrapquiz"),
            InlineKeyboardButton(text="Установка дедлайна", callback_data="set_deadlinequiz")
        ]
    ]
)

sendquizAct = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrapquiz"),
            InlineKeyboardButton(text="Изменить дедлайн", callback_data="set_deadlinequiz")
        ],
        [
            InlineKeyboardButton(text="Отметить выполненной", callback_data="clickquiz")
        ]
    ]
)

sendquiz_d = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Свернуть", callback_data="unwrapquiz"),
            InlineKeyboardButton(text="Установка дедлайна", callback_data="set_deadlinequiz")
        ]
    ]
)

sendquizAct_d = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Свернуть", callback_data="unwrapquiz"),
            InlineKeyboardButton(text="Изменить дедлайн", callback_data="set_deadlinequiz")
        ],
        [
            InlineKeyboardButton(text="Отметить выполненной", callback_data="clickquiz")
        ]
    ]
)