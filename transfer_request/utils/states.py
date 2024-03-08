from aiogram.fsm.state import StatesGroup, State, default_state


class transferRequest(StatesGroup):
    name_staff = State()
    post_staff = State()
    division_staff = State()
    is_staff = State()
    goals_count = State()
    goals_staff = State()
    due_date_staff = State()
    results_staff = State()
    fio_changed = State()  
    post_changed = State()
    division_changed = State()
    is_changed = State()
    goals_changed = State()
    goals_count_changed = State()
    due_date_changed = State()
    results_changed = State()
    goal_number = State()
