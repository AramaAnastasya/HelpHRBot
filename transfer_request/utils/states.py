from aiogram.fsm.state import StatesGroup, State, default_state


class transferRequest(StatesGroup):
    is_staff = State()
    goals_count = State()
    goals_staff = State()
    due_date_staff = State()
    results_staff = State()
    is_changed = State()
    goals_changed = State()
    goals_count_changed = State()
    due_date_changed = State()
    results_changed = State()
    goal_number = State()
    unwrap = State()