import asyncio
import os
import time

from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from keyboards.default.markups import *
from loader import dp, db, bot
from filters import IsUser
from utils.db.get_and_filter_data import get_and_filter_all
from utils.db.get_set_info_db import *
import pandas as pd


notice_cb = CallbackData('somearg', 'tid', 'action')


@dp.message_handler(IsUser(), text=notice_choice_template)
async def process_notices(message: Message, state: FSMContext):

    temps = get_templates_cid(message.from_user.id)
    if temps:

        for t in temps:
            markup = InlineKeyboardMarkup()
            btn = InlineKeyboardButton('Выбрать', callback_data=notice_cb.new(tid=t['tid'], action='choice'))
            markup.add(btn)
            await message.answer(f'Шаблон №{t["tid"]}\nДата публикации: последние {t["published"]} минут\n'
                                 f'Цена от: {t["min_price"]} до: {t["max_price"]}\n'
                                 f'Просмотров от: {t["views_min"]} до: {t["views_max"]}\n'
                                 f'Активных объявлений от: {t["active_ad_min"]} до: {t["active_ad_max"]}\n'
                                 f'Завершенных объявлений от: {t["close_ad_min"]} до: {t["close_ad_max"]}\n',
                                 reply_markup=markup)

    else:
        await message.answer('У вас еще нет шаблонов')


@dp.callback_query_handler(IsUser(), notice_cb.filter(action='choice'))
async def process_notice_tid(query: CallbackQuery, callback_data: dict, state: FSMContext):
    tid = callback_data['tid']
    update_user_notice(query.from_user.id, tid)
    await query.message.answer('Уведомления включены')


@dp.message_handler(IsUser(), text=notice_off)
async def process_notice_off(message: Message, state: FSMContext):
    update_user_notice(message.from_user.id, 0)
    await message.answer('Уведомления выключены')


def LoopStart():
    asyncio.run(run_send_notice())


async def run_send_notice():
    await asyncio.sleep(0)
    while True:
        try:
            st_time = time.time()
            table = get_from_buffer()

            if len(table) > 0:
                users = get_users()

                for user in users:
                    if int(user['notice']) > 0 and str(user['sub']) == '1':

                        temp = get_template_cid_tid(user['cid'], user['notice'])
                        full_ads = []
                        def_arr = []
                        ads = await get_and_filter_all(temp, ['buffer'], def_arr)
                        full_ads += ads
                        print('len ads filter', len(ads))
                        name1 = 'full'
                        if len(ads) > 0:
                            try:
                                res = pd.read_excel(f'{name1}.xlsx', sheet_name='Result')
                                def_arr = res.values.tolist()
                                new_arr = []
                                count_new_ads = 0
                                for i in full_ads:
                                    if i['seller'] not in str(def_arr):
                                        new_arr.append(i)
                                        def_arr.append(
                                            [i['link'], i['name'], i['price'], i['views'], i['seller'], i['phone'],
                                             i['active_count'],
                                             i['sold_count']])
                                        count_new_ads += 1
                                if count_new_ads > 0:
                                    df = pd.DataFrame({'Link': [i[0] for i in def_arr],
                                                       'Name': [i[1] for i in def_arr],
                                                       'Price': [i[2] for i in def_arr],
                                                       'Views': [i[3] for i in def_arr],
                                                       'Seller': [i[4] for i in def_arr],
                                                       'Phone': [i[5] for i in def_arr],
                                                       'Active count': [i[6] for i in def_arr],
                                                       'Sold count': [i[7] for i in def_arr]})
                                    df2 = pd.DataFrame({'Link': [i['link'] for i in new_arr],
                                                        'Name': [i['name'] for i in new_arr],
                                                        'Price': [i['price'] for i in new_arr],
                                                        'Views': [i['views'] for i in new_arr],
                                                        'Seller': [i['seller'] for i in new_arr],
                                                        'Phone': [i['phone'] for i in new_arr],
                                                        'Active count': [i['active_count'] for i in new_arr],
                                                        'Sold count': [i['sold_count'] for i in new_arr]})
                                    df.to_excel(f'{name1}.xlsx', sheet_name='Result', index=False)
                                    name_to_send = f'{name1}{round(time.time())}'
                                    df2.to_excel(f'{name_to_send}.xlsx', sheet_name='Result', index=False)
                                    s = f'Уведомление. Найдено: {count_new_ads} объявлений' #, время сбора: {round(time.time() - st_time, 2)} секунд'
                                    name_to_send = f'{name_to_send}.xlsx'
                                    create_message(user['cid'], f'{s};{name_to_send}')
                                    # await bot.send_message(user['cid'], s)
                                    # await bot.send_document(user['cid'], open(f'{name_to_send}.xlsx', 'rb'))
                                    os.remove(f'{name_to_send}.xlsx')
                            except Exception as e:
                                df = pd.DataFrame({'Link': [i['link'] for i in full_ads],
                                                   'Name': [i['name'] for i in full_ads],
                                                   'Price': [i['price'] for i in full_ads],
                                                   'Views': [i['views'] for i in full_ads],
                                                   'Seller': [i['seller'] for i in full_ads],
                                                   'Phone': [i['phone'] for i in full_ads],
                                                   'Active count': [i['active_count'] for i in full_ads],
                                                   'Sold count': [i['sold_count'] for i in full_ads]})
                                df.to_excel(f'{name1}.xlsx', sheet_name='Result', index=False)
                                s = f'Уведомление. Найдено: {len(full_ads)} объявлений, время сбора: {round(time.time() - st_time, 2)} секунд'
                                name1 = f'{name1}.xlsx'
                                create_message(user['cid'], f'{s};{name1}')
                                # await bot.send_message(user['cid'], f'Уведомление. Найдено: {full_ads} объявлений, время сбора: {round(time.time() - st_time, 2)} секунд')
                                # await bot.send_document(user['cid'], open(f'{name1}.xlsx', 'rb'))
                        else:
                            print('no ads')
                clear_buffer()

            t_sleep = round(time.time() - st_time)
            if t_sleep <= 0:
                t_sleep = 0
            await send_messages()
            await asyncio.sleep(t_sleep)
        except Exception as e:
            print(e)


async def send_messages():
    try:
        print('start send messages')
        r = get_messages()
        for i in r:
            await bot.send_message(i['cid'], i['message'].split(';')[0])
            await bot.send_document(i['cid'], open(i['message'].split(';')[1], 'rb'))
            delete_message(i['cid'], i['message'])
        await asyncio.sleep(60)
    except Exception as e:
        print(e)