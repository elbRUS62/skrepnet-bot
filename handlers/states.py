from aiogram.fsm.state import State, StatesGroup


class RegStates(StatesGroup):
    waiting_name = State()


class AdminStates(StatesGroup):
    waiting_add_admin = State()
    waiting_del_admin = State()
    waiting_extend_username = State()
    waiting_extend_days = State()
    waiting_reset_username = State()
    waiting_broadcast_text = State()
    waiting_delete_username = State()