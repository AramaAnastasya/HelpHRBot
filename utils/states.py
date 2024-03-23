from aiogram.fsm.state import StatesGroup, State, default_state


class Employee(StatesGroup):
    search_bd = State()
    search_name = State()
    search_division = State()
    search_post = State()
    search_name_chg = State()  
    search_post_chg = State()
    search_division_chg = State()
    request = State()
    initiator = State()
    search = State()
    search_change = State()
    division_input = State()