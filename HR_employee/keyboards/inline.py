from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

def get_callback_btns(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (1,1)):

    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()

sorted_keybordFirst = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Заявки", callback_data="sort_app"),
            InlineKeyboardButton(text="Вопросы", callback_data="sort_quest")
        ],
        [
            InlineKeyboardButton(text="Просмотреть всё", callback_data="sort_all")
        ]

    ]
)

sorted_keybordSecond = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Заявка на перевод", callback_data="sort_app_transf")
        ],
        [
            InlineKeyboardButton(text="Заявка на согласование ЗП", callback_data="sort_app_zp")
        ],
        [
            InlineKeyboardButton(text="Заявка на перевод на другой формат работы", callback_data="sort_app_diff")
        ],
        [
            InlineKeyboardButton(text="Заявки общей формы", callback_data="sort_app_general")
        ],
        [
            InlineKeyboardButton(text="Просмотреть всё", callback_data="sort_app_all")
        ]

    ]
)

sortedAct_keybordFirst = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Заявки", callback_data="sort_app1"),
            InlineKeyboardButton(text="Вопросы", callback_data="sort_quest1")
        ],
        [
            InlineKeyboardButton(text="Просмотреть всё", callback_data="sort_all1")
        ]

    ]
)

sortedAct_keybordSecond = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Заявка на перевод", callback_data="sort_app_transf1")
        ],
        [
            InlineKeyboardButton(text="Заявка на согласование ЗП", callback_data="sort_app_zp1")
        ],
        [
            InlineKeyboardButton(text="Заявка на перевод на другой формат работы", callback_data="sort_app_diff1")
        ],
        [
            InlineKeyboardButton(text="Заявки общей формы", callback_data="sort_app_general1")
        ],
        [
            InlineKeyboardButton(text="Просмотреть всё", callback_data="sort_app_all1")
        ]

    ]
)


сhoiceStatistic_keybord = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Текущий месяц", callback_data="now_month"),
            InlineKeyboardButton(text="Выбрать период", callback_data="choice_month")
        ]
    ]
)

set_deadline_tmrw = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Изменить дедлайн", callback_data="set_deadline"),
            InlineKeyboardButton(text="Отметить выполненной", callback_data="click")
        ]
    ]
)

set_deadline_tmrw_quiz = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Изменить дедлайн", callback_data="set_deadlinequiz"),
            InlineKeyboardButton(text="Отметить выполненной", callback_data="clickquiz")
        ]
    ]
)

comment_request = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="yes_comm"),
            InlineKeyboardButton(text="Нет", callback_data="no_comm")
        ]
    ]
)

comment_push = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Отправить", callback_data="go_comm"),
            InlineKeyboardButton(text="Отмена", callback_data="back_comm")
        ]
    ]
)