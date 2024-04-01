from aiogram.fsm.state import StatesGroup, State, default_state


class Applications(StatesGroup):
    waiting_for_action = State()