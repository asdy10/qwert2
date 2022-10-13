from aiogram.dispatcher.filters.state import StatesGroup, State


class AccountState(StatesGroup):
    start = State()
    subscribe = State()


class MakeTemplateState(StatesGroup):
    price = State()
    pub = State()
    views = State()
    active_ads = State()
    close_ads = State()
    confirm = State()
