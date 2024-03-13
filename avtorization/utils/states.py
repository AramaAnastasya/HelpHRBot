from aiogram.fsm.state import StatesGroup, State, default_state

class FSMAdmin(StatesGroup):
    phone = State()
