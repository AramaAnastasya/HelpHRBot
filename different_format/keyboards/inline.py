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
            InlineKeyboardButton(text="Да", callback_data="yes_diff"),
            InlineKeyboardButton(text="Нет", callback_data="no_diff")
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



placenowkb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Офис", callback_data="officenow")
        ],
        [
            InlineKeyboardButton(text="Гибрид", callback_data="hybridnow")
        ],
        [
            InlineKeyboardButton(text="Удаленно", callback_data="remotelynow")
        ]

    ]
    
)


placewillkb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Офис", callback_data="officewill")
        ],
        [
            InlineKeyboardButton(text="Гибрид", callback_data="hybridwill")
        ],
        [
            InlineKeyboardButton(text="Удаленно", callback_data="remotelywill")
        ]

    ]
)



yesnotransfer = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="yestr"),
            InlineKeyboardButton(text="Нет", callback_data="notr")
        ]

    ]
)



changetr = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Сотрудник", callback_data="search_changed"),
        ],
        [
            InlineKeyboardButton(text="Формат на данный момент", callback_data="placenowedi"),
        ],
        [
            InlineKeyboardButton(text="Формат на переход", callback_data="placewilledi"),
        ],
        [
            InlineKeyboardButton(text="Часы работы", callback_data="timeworkedi"),
        ],
        [
            InlineKeyboardButton(text="Город", callback_data="cityedi"),
        ],
        [
            InlineKeyboardButton(text="Причина перевода", callback_data="reasonedi"),
        ]
    ]
)




placenowkbedi = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Офис", callback_data="officenowedi")
        ],
        [
            InlineKeyboardButton(text="Гибрид", callback_data="hybridnowedi")
        ],
        [
            InlineKeyboardButton(text="Удаленно", callback_data="remotelynowedi")
        ]

    ]
)



placewillkbedi = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Офис", callback_data="officewilledi")
        ],
        [
            InlineKeyboardButton(text="Гибрид", callback_data="hybridwilledi")
        ],
        [
            InlineKeyboardButton(text="Удаленно", callback_data="remotelywilledi")
        ]

    ]
)

send_different = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrap_different"),
            InlineKeyboardButton(text="Установка дедлайна", callback_data="set_deadline")
        ]
    ]
)

send_differentAct = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrap_different"),
            InlineKeyboardButton(text="Изменить дедлайн", callback_data="set_deadline")
        ],
        [
            InlineKeyboardButton(text="Отметить выполненной", callback_data="click")
        ]
    ]
)

send_different_d = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Свернуть", callback_data="unwrap_different"),
            InlineKeyboardButton(text="Установка дедлайна", callback_data="set_deadline")
        ]
    ]
)

send_differentAct_d = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Свернуть", callback_data="unwrap_different"),
            InlineKeyboardButton(text="Изменить дедлайн", callback_data="set_deadline")
        ],
        [
            InlineKeyboardButton(text="Отметить выполненной", callback_data="click")
        ]
    ]
)