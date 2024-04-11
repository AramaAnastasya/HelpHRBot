from aiogram.fsm.state import StatesGroup, State, default_state


class Applications(StatesGroup):
    comment = State()
    id_mess_comm = State()
    id_mess_state = State()
    id_mess_go = State()
    comm_quiz = State()
    type_calendar = State()
    start_date = State()
    startSave_date = State()
    end_date = State()