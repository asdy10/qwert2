from aiogram.dispatcher.filters.state import StatesGroup, State


class AddSubState(StatesGroup):
    cid = State()
    sub = State()


class AddBonusState(StatesGroup):
    cid = State()
    bonus = State()