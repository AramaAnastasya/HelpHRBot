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

sorted_keybordFirstI = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Заявки", callback_data="sort_appI"),
            InlineKeyboardButton(text="Вопросы", callback_data="sort_questI")
        ],
        [
            InlineKeyboardButton(text="Просмотреть всё", callback_data="sort_allI")
        ]

    ]
)

sorted_keybordSecondI = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Заявка на перевод", callback_data="sort_app_transfI")
        ],
        [
            InlineKeyboardButton(text="Заявка на согласование ЗП", callback_data="sort_app_zpI")
        ],
        [
            InlineKeyboardButton(text="Заявка на перевод на другой формат работы", callback_data="sort_app_diffI")
        ],
        [
            InlineKeyboardButton(text="Заявки общей формы", callback_data="sort_app_generalI")
        ],
        [
            InlineKeyboardButton(text="Просмотреть всё", callback_data="sort_app_allI")
        ]

    ]
)

init_quest = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrapquiz"),
        ]
    ]
)



init_quest_d = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Свернуть", callback_data="unwrapquiz"),
        ]
    ]
)

init_transf = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrap_trans"),
        ]
    ]
)



init_transf_d = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Свернуть", callback_data="unwrap_trans"),
        ]
    ]
)

init_zp = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrap_zp"),
        ]
    ]
)



init_zp_d = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Свернуть", callback_data="unwrap_zp"),
        ]
    ]
)

init_diff = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrap_different"),
        ]
    ]
)



init_diff_d = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Свернуть", callback_data="unwrap_different"),
        ]
    ]
)

init_gen = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Развернуть", callback_data="unwrap_send"),
        ]
    ]
)



init_gen_d = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Свернуть", callback_data="unwrap_send"),
        ]
    ]
)