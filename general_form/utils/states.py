from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    essence = State()
    expect = State()
    essence2 = State()
    expect2 = State()
    quiz = State()
    quiz2 = State()
    resquiz = State()
    resquiz2 = State()