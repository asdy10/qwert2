
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ContentType, ReplyKeyboardMarkup, ReplyKeyboardRemove

from keyboards.default.markups import admin_set_sub, admin_set_bonus
from states import AddSubState, AddBonusState
from loader import dp, db, bot
from filters import IsAdmin
from utils.db.get_set_info_db import update_user_sub, update_user_bonus, get_user

"""discount"""


@dp.message_handler(IsAdmin(), text=admin_set_sub)
async def process_sub(message: Message, state: FSMContext):
    await AddSubState.cid.set()
    await message.answer('Введите cid пользователя')


@dp.message_handler(IsAdmin(), state=AddSubState.cid)
async def process_sub_cid(message: Message, state: FSMContext):
    if check_is_int(message.text):
        async with state.proxy() as data:
            data['cid'] = message.text
        user = get_user(message.text)
        try:
            if str(user['sub']) == '0':
                update_user_sub(message.text, '1')
                await message.answer('Доступ разрешен')
            else:
                update_user_sub(message.text, '0')
                await message.answer('Доступ запрещен')
        except:
            await message.answer('Пользователя не найдено')
        await state.finish()

    else:
        await message.answer('Некорректное число')


def check_is_int(m):
    try:
        int(m)
        return True
    except:
        return False


@dp.message_handler(IsAdmin(), state=AddSubState.sub)
async def process_set_sub(message: Message, state: FSMContext):
    if check_is_int(message.text):
        async with state.proxy() as data:
            cid = data['cid']
        update_user_sub(cid, message.text)
        await message.answer('Изменено')
        await state.finish()
    else:
        await message.answer('Некорректное число')


@dp.message_handler(IsAdmin(), text=admin_set_bonus)
async def process_bonus(message: Message, state: FSMContext):
    await AddBonusState.cid.set()
    await message.answer('Введите cid пользователя')


@dp.message_handler(IsAdmin(), state=AddBonusState.cid)
async def process_bonus_cid(message: Message, state: FSMContext):
    if check_is_int(message.text):
        async with state.proxy() as data:
            data['cid'] = message.text
        await AddBonusState.next()
        await message.answer('Введите реферальный бонус')
    else:
        await message.answer('Некорректное число')


@dp.message_handler(IsAdmin(), state=AddBonusState.bonus)
async def process_set_bonus(message: Message, state: FSMContext):
    try:
        s = float(message.text)
        async with state.proxy() as data:
            cid = data['cid']
        update_user_bonus(cid, s)
        await message.answer('Изменено')
        await state.finish()
    except:
        await message.answer('Некорректное число')
