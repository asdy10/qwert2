import asyncio
import os
import threading

from aiogram.dispatcher import FSMContext

from handlers.user.notices import run_send_notice, LoopStart, send_messages
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup
from data import config
from filters import IsUser, IsAdmin
import handlers
from handlers.user.notices import run_send_notice, LoopStart
from keyboards.default.markups import admin_menu_markup, user_markup
from loader import dp, bot
from utils.db.get_and_filter_data import get_and_filter_all
from utils.db.get_set_info_db import *
import filters
import logging


filters.setup(dp)

WEBAPP_HOST = "127.0.0.1"
WEBAPP_PORT = int(os.environ.get("PORT", 5000))


@dp.message_handler(IsUser(), commands='start', state='*')
async def cmd_start_user(message: types.Message, state: FSMContext):
    await state.finish()
    print(message.text, message.from_user.id)
    if not get_user(message.from_user.id):
        try:
            ref = message.text.split()[1]
        except:
            ref = 0
        create_user(message.from_user.id, message.from_user.username, ref)
    await message.answer('Выберите пункт главного меню', reply_markup=user_markup())


@dp.message_handler(IsAdmin(), commands='start', state='*')
async def cmd_start_admin(message: types.Message, state: FSMContext):
    await state.finish()
    print(message.text)
    await message.answer('🤖 Я бот. Режим админа', reply_markup=admin_menu_markup())


async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)#, filename='logs.txt'
    db.create_tables()
    logging.info('#####START#####')
    await bot.delete_webhook()
    await bot.set_webhook(config.WEBHOOK_URL)
    asyncio.create_task(send_messages())
    th = threading.Thread(target=LoopStart)
    th.start()



async def on_shutdown():
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bot down")


if __name__ == '__main__':
    if "HEROKU" in list(os.environ.keys()):

        executor.start_webhook(
            dispatcher=dp,
            webhook_path=config.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )

    else:

        executor.start_polling(dp, on_startup=on_startup, skip_updates=False)

