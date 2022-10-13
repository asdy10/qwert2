import time

from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from keyboards.default.markups import *
from loader import dp, db, bot
from filters import IsUser
from states import AccountState
from utils.db.get_set_info_db import get_user

#
# @dp.message_handler(IsUser(), text=account_info)
# async def process_account_info(message: Message, state: FSMContext):
#     acc = get_user(message.from_user.id)
#     markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#     markup.add(continue_subscribe, back_message)
#     await AccountState.start.set()
#     await message.answer(f'📆 Подписка действует до {acc["sub"]}\n💰 Реферальный бонус: {acc["bonus"]}\n'
#                          f'Приглашайте людей и получайте 5% с каждой их покупки!\n'
#                          f'🔗Ваша уникальная инвайт-ссылка: https://t.me/youla_top_parser_bot?start={message.from_user.id}', reply_markup=markup)
#
#
# @dp.message_handler(IsUser(), text=continue_subscribe, state=AccountState.start)
# async def process_account_info_continue_subscribe(message: Message, state: FSMContext):
#     #await AccountState.next()
#     await state.finish()
#     await message.answer('Стоимость подписки:\n<b>1 день: 5$\n1 месяц: 100$</b>\n'
#                          'Для продления подписки обратитесь к менеджеру https://t.me/wb_totop_admin\n'
#                          '(Автоматическая оплата в разработке)', reply_markup=user_markup())
#
#
# @dp.message_handler(IsUser(), text=back_message, state=AccountState.start)
# async def process_account_info_back(message: Message, state: FSMContext):
#     await state.finish()
#     await message.answer('Выберите пункт меню', reply_markup=user_markup())
#
#
# @dp.message_handler(IsUser(), text=cancel_message, state=AccountState.subscribe)
# async def process_account_info_continue_subscribe_cancel(message: Message, state: FSMContext):
#     await state.finish()
#
#     await message.answer('Для продления подписки обратитесь к менеджеру https://t.me/wb_totop_admin\n'
#                          'Автоматическая оплата в разработке', reply_markup=user_markup())
