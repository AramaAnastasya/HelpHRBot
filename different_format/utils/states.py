from aiogram.fsm.state import StatesGroup, State

class FormTransf(StatesGroup):
    placenow = State()
    placeWwill = State()
    timework = State()
    city = State()
    reason = State()
    timework2 = State()
    city2 = State()
    reason2 = State()