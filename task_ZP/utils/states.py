from aiogram.fsm.state import StatesGroup, State, default_state


class taskZP(StatesGroup):
    proposed_amount = State()
    current_amount = State()
    reasons = State()
    proposed_amount_changed = State()  
    current_amount_changed = State()
    reasons_changed = State()