import asyncio
import os
import sys
import time

from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, \
    CallbackQuery
from aiogram.dispatcher import FSMContext

from data.categories import get_names_link_categories, get_arr_cat1
from keyboards.default.markups import *
from loader import dp, db, bot
from filters import IsUser
from states import BuyoutMenuState, MakeTemplateState
from utils.db.get_and_filter_data import get_and_filter, get_and_filter_all
from utils.db.get_set_info_db import *
from aiogram.utils.callback_data import CallbackData
import pandas as pd
cat_cb = CallbackData('somearg', 'category', 'action')
cat2_cb = CallbackData('somearg', 'subcategory', 'action')
temp_cb = CallbackData('somearg', 'tid', 'action')


@dp.message_handler(IsUser(), text=my_templates)
async def process_my_templates(message: Message, state: FSMContext):
    temps = get_templates_cid(message.from_user.id)
    if temps:

        for t in temps:

            markup = InlineKeyboardMarkup()
            btn = InlineKeyboardButton('Спарсить', callback_data=temp_cb.new(tid=t['tid'], action='pars'))
            btn2 = InlineKeyboardButton('Удалить', callback_data=temp_cb.new(tid=t['tid'], action='delete'))
            markup.add(btn, btn2)
            await message.answer(f'Шаблон №{t["tid"]}\nДата публикации: последние {t["published"]} минут\n'
                                 f'Цена от: {t["min_price"]} до: {t["max_price"]}\n'
                                 f'Просмотров от: {t["views_min"]} до: {t["views_max"]}\n'
                                 f'Активных объявлений от: {t["active_ad_min"]} до: {t["active_ad_max"]}\n'
                                 f'Завершенных объявлений от: {t["close_ad_min"]} до: {t["close_ad_max"]}\n', reply_markup=markup)

    else:
        await message.answer('У вас еще нет шаблонов')


@dp.message_handler(IsUser(), text=make_template)
async def process_make_template(message: Message, state: FSMContext):
    await MakeTemplateState.price.set()
    await message.answer('Введите цену в формате от:до, например 1000:10000', reply_markup=cancel_markup())


@dp.message_handler(IsUser(), lambda message: message.text not in [cancel_message], state=MakeTemplateState.price)
async def process_make_template_price(message: Message, state: FSMContext):

    min_price, max_price = check_price(message.text)
    if min_price == -1 and max_price == -1:
        await message.answer('Некорректный формат данных')
    else:
        async with state.proxy() as data:
            data['min_price'] = min_price
            data['max_price'] = max_price
        await MakeTemplateState.next()
        await message.answer('Введите время публикации, последние сколько минут? '
                             'Например, отправленное число 1440, будет означать последние 24 часа', reply_markup=back_markup())


def check_price(m):
    try:
        a, b = m.split(':')
        return int(a), int(b)
    except:
        return -1, -1


def check_count_closed(m):
    try:
        a, b = m.split(':')
        return int(a), int(b)
    except:
        return 0, 0


@dp.message_handler(IsUser(), text=cancel_message, state=MakeTemplateState.price)
async def process_make_template_price_back(message: Message, state: FSMContext):
    await state.finish()
    await message.answer('Выберите пункт меню', reply_markup=user_markup())


@dp.message_handler(IsUser(), lambda message: message.text not in [back_message], state=MakeTemplateState.pub)
async def process_make_template_pub(message: Message, state: FSMContext):
    published = check_pub(message.text)
    if published != 0:
        async with state.proxy() as data:
            data['published'] = published
        await MakeTemplateState.next()
        await message.answer('Введите количество просмотров в формате от:до, например 0:10', reply_markup=back_markup())
    else:
        await message.answer('Некорректный формат данных')


def check_pub(m):
    try:
        return int(m)
    except:
        return 0


@dp.message_handler(IsUser(), text=back_message, state=MakeTemplateState.pub)
async def process_make_template_pub_back(message: Message, state: FSMContext):
    await process_make_template(message, state)


@dp.message_handler(IsUser(), lambda message: message.text not in [back_message], state=MakeTemplateState.views)
async def process_make_template_views(message: Message, state: FSMContext):
    views_min, views_max = check_price(message.text)
    if views_min == -1 and views_max == -1:
        await message.answer('Некорректный формат данных')
    else:
        async with state.proxy() as data:
            data['views_min'] = views_min
            data['views_max'] = views_max
        await MakeTemplateState.next()
        await message.answer('Введите количество активных объявлений у продавца в формате от:до, например 1:3', reply_markup=back_markup())


@dp.message_handler(IsUser(), text=back_message, state=MakeTemplateState.views)
async def process_make_template_views_back(message: Message, state: FSMContext):
    await MakeTemplateState.pub.set()
    await message.answer('Введите время публикации, последние сколько минут? '
                         'Например, отправленное число 1440, будет означать последние 24 часа', reply_markup=back_markup())


@dp.message_handler(IsUser(), lambda message: message.text not in [back_message], state=MakeTemplateState.active_ads)
async def process_make_template_active_ads(message: Message, state: FSMContext):
    active_ad_min, active_ad_max = check_price(message.text)
    if active_ad_min == -1 and active_ad_max == -1:
        await message.answer('Некорректный формат данных')
    else:
        async with state.proxy() as data:
            data['active_ad_min'] = active_ad_min
            data['active_ad_max'] = active_ad_max
        await MakeTemplateState.next()
        await message.answer('Введите количество завершенных объявлений у продавца в формате от:до, например 0:3', reply_markup=back_markup())


@dp.message_handler(IsUser(), text=back_message, state=MakeTemplateState.active_ads)
async def process_make_template_active_ads_back(message: Message, state: FSMContext):
    await MakeTemplateState.views.set()
    await message.answer('Введите количество просмотров в формате от:до, например 0:10', reply_markup=back_markup())


@dp.message_handler(IsUser(), lambda message: message.text not in [back_message], state=MakeTemplateState.close_ads)
async def process_make_template_close_ads(message: Message, state: FSMContext):
    close_ad_min, close_ad_max = check_price(message.text)
    if close_ad_min == -1 and close_ad_max == -1:
        await message.answer('Некорректный формат данных')
    else:
        async with state.proxy() as data:
            data['close_ad_min'] = close_ad_min
            data['close_ad_max'] = close_ad_max
        await MakeTemplateState.next()
        await message.answer('Проверьте правильность шаблона и нажмите "✅ Подтвердить".\n'
                             'Категорию нужно будет выбрать перед самим парсингом', reply_markup=confirm_markup())


@dp.message_handler(IsUser(), text=back_message, state=MakeTemplateState.close_ads)
async def process_make_template_close_ads_back(message: Message, state: FSMContext):
    await MakeTemplateState.active_ads.set()
    await message.answer('Введите количество активных объявлений у продавца в формате от:до, например 1:3', reply_markup=back_markup())


@dp.message_handler(IsUser(), text=confirm_message, state=MakeTemplateState.confirm)
async def process_make_template_confirm(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['cid'] = message.from_user.id
        temps = get_templates_cid(message.from_user.id)
        if temps:
            data['tid'] = temps[-1]['tid'] + 1
        else:
            data['tid'] = 1
        create_template(data)
    await state.finish()
    await message.answer('Сохранено', reply_markup=user_markup())


@dp.message_handler(IsUser(), text=back_message, state=MakeTemplateState.confirm)
async def process_make_template_confirm_back(message: Message, state: FSMContext):
    await MakeTemplateState.close_ads.set()
    await message.answer('Введите количество завершенных объявлений у продавца в формате от:до, например 0:3', reply_markup=back_markup())


'''Start Parse'''


@dp.callback_query_handler(IsUser(), temp_cb.filter(action='parasss'))
async def process_pars(query: CallbackQuery, callback_data: dict, state: FSMContext):

    tid = int(callback_data['tid'])
    temp = get_template_cid_tid(query.from_user.id, tid)
    async with state.proxy() as data:
        data['max_price'] = temp['max_price']
        data['min_price'] = temp['min_price']
        data['published'] = temp['published']
        data['active_ad_min'] = temp['active_ad_min']
        data['active_ad_max'] = temp['active_ad_max']
        data['close_ad_min'] = temp['close_ad_min']
        data['close_ad_max'] = temp['close_ad_max']
        data['views_min'] = temp['views_min']
        data['views_max'] = temp['views_max']





















    arr = get_names_link_categories()
    names_cat1 = get_arr_cat1(arr)
    # for i in names_cat1:
    #     print(i)
    markup = InlineKeyboardMarkup(row_width=1)
    btn = InlineKeyboardButton('🔥Все категории(VIP)🔥', callback_data=cat_cb.new(category='all', action='all_cat0'))
    markup.add(btn)
    for i in range(len(names_cat1)):
        btn = InlineKeyboardButton(names_cat1[i], callback_data=cat_cb.new(category=i, action='add_cat1'))
        markup.add(btn)
    btn = InlineKeyboardButton('👈 Назад', callback_data=cat_cb.new(category='back', action='back1'))
    markup.add(btn)
    await query.message.answer('Выберите категорию', reply_markup=markup)


@dp.callback_query_handler(IsUser(), temp_cb.filter(action='delete'))
async def process_temp_delete(query: CallbackQuery, callback_data: dict, state: FSMContext):
    delete_template(int(callback_data['tid']))
    await query.message.delete()
    await query.message.answer('Удалено')


@dp.callback_query_handler(IsUser(), cat_cb.filter(action='back1'))
async def process_choice_cat2_back(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.message.delete()


@dp.callback_query_handler(IsUser(), temp_cb.filter(action='pars'))
async def process_all_cat0(query: CallbackQuery, callback_data: dict, state: FSMContext):
    #arr = get_names_link_categories()

    tid = int(callback_data['tid'])
    temp = get_template_cid_tid(query.from_user.id, tid)
    async with state.proxy() as data:
        data['max_price'] = temp['max_price']
        data['min_price'] = temp['min_price']
        data['published'] = temp['published']
        data['active_ad_min'] = temp['active_ad_min']
        data['active_ad_max'] = temp['active_ad_max']
        data['close_ad_min'] = temp['close_ad_min']
        data['close_ad_max'] = temp['close_ad_max']
        data['views_min'] = temp['views_min']
        data['views_max'] = temp['views_max']
    new_arr_links = ['full']
    # for i in arr:
    #     new_arr_links.append(i[1][[j for j in i[1].keys()][0]])
    user = get_user(query.from_user.id)
    if str(user['sub']) == '1':
        await query.message.answer('Данные собираются, ожидайте...')
        st_time = time.time()
        async with state.proxy() as data:
            params = {}
            params['max_price'] = data['max_price']
            params['min_price'] = data['min_price']
            params['published'] = data['published']
            params['active_ad_min'] = data['active_ad_min']
            params['active_ad_max'] = data['active_ad_max']
            params['close_ad_min'] = data['close_ad_min']
            params['close_ad_max'] = data['close_ad_max']
            params['views_min'] = data['views_min']
            params['views_max'] = data['views_max']
            m = f"цена |{params['min_price']}:{params['max_price']}|\n" \
                f"публикация |{params['published']}|\n" \
                f"активных |{params['active_ad_min']}:{params['active_ad_max']}|\n" \
                f"завершенных |{params['close_ad_min']}:{params['close_ad_max']}|\n" \
                f"просмотров |{params['views_min']}:{params['views_max']}|"
        full_ads = []
        # params['category'] = new_arr_links
        name1 = f'full'
        try:
            res = pd.read_excel(f'{name1}.xlsx', sheet_name='Result')
            def_arr = res.values.tolist()
        except:
            def_arr = []
        print('start1')

        ads = await get_and_filter_all(params, new_arr_links, def_arr)
        full_ads += ads
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
                            [i['link'], i['name'], i['price'], i['views'], i['seller'], i['phone'], i['active_count'],
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
                    await query.message.answer(
                        f'Готово. Найдено: {count_new_ads} объявлений, время сбора: {round(time.time() - st_time, 2)} секунд\n{m}')
                    await query.message.answer_document(open(f'{name_to_send}.xlsx', 'rb'))
                    os.remove(f'{name_to_send}.xlsx')
                else:
                    await query.message.answer('Новых объявлений с такими параметрами не найдено')
            except:
                df = pd.DataFrame({'Link': [i['link'] for i in full_ads],
                                   'Name': [i['name'] for i in full_ads],
                                   'Price': [i['price'] for i in full_ads],
                                   'Views': [i['views'] for i in full_ads],
                                   'Seller': [i['seller'] for i in full_ads],
                                   'Phone': [i['phone'] for i in full_ads],
                                   'Active count': [i['active_count'] for i in full_ads],
                                   'Sold count': [i['sold_count'] for i in full_ads]})
                df.to_excel(f'{name1}.xlsx', sheet_name='Result', index=False)
                await query.message.answer(f'Готово. Найдено: {len(full_ads)} объявлений, время сбора: {round(time.time() - st_time, 2)} секунд\n{m}')
                await query.message.answer_document(open(f'{name1}.xlsx', 'rb'))
        else:
            await query.message.answer('Объявлений с такими параметрами не найдено')
        col = db.collection('orders')
        db.insert_one_record(col, {'cid': query.from_user.id, 'category': 'full',
                                   'date': datetime.today().strftime("%d.%m.%Y %H:%M:%S")})
    else:
        await query.message.answer('Нет доступа.')


@dp.callback_query_handler(IsUser(), cat_cb.filter(action='add_cat1'))
async def process_choice_cat2(query: CallbackQuery, callback_data: dict, state: FSMContext):

    cat1 = int(callback_data['category'])
    async with state.proxy() as data:
        data['category'] = cat1
    arr = get_names_link_categories()
    names_cat1 = get_arr_cat1(arr)
    name = names_cat1[cat1]
    new_arr_names = []
    new_arr_links = []

    for i in arr:
        if name in i[0].keys():
            new_arr_links.append(i[1][[j for j in i[1].keys()][0]])
            new_arr_names.append([j for j in i[1].keys()][0])

    markup = InlineKeyboardMarkup(row_width=1)
    btn = InlineKeyboardButton('🔥Вся категория(VIP)🔥', callback_data=cat2_cb.new(subcategory=cat1, action='all_cat1'))
    markup.add(btn)
    for i, j in zip(new_arr_names, new_arr_links):
        btn = InlineKeyboardButton(i, callback_data=cat2_cb.new(subcategory=j, action='add_cat2'))
        markup.add(btn)
    btn = InlineKeyboardButton('👈 Назад', callback_data=cat2_cb.new(subcategory='back', action='back2'))
    markup.add(btn)
    await query.message.edit_reply_markup(markup)


@dp.callback_query_handler(IsUser(), cat2_cb.filter(action='all_cat1'))
async def process_all_cat(query: CallbackQuery, callback_data: dict, state: FSMContext):
    cat1 = int(callback_data['subcategory'])
    arr = get_names_link_categories()
    names_cat1 = get_arr_cat1(arr)
    name = names_cat1[cat1]
    new_arr_links = []
    for i in arr:
        if name in i[0].keys():
            new_arr_links.append(i[1][[j for j in i[1].keys()][0]])
    user = get_user(query.from_user.id)
    if str(user['sub']) == '1':
        await query.message.answer('Данные собираются, ожидайте...')
        st_time = time.time()
        async with state.proxy() as data:
            params = {}
            params['max_price'] = data['max_price']
            params['min_price'] = data['min_price']
            params['published'] = data['published']
            params['active_ad_min'] = data['active_ad_min']
            params['active_ad_max'] = data['active_ad_max']
            params['close_ad_min'] = data['close_ad_min']
            params['close_ad_max'] = data['close_ad_max']
            params['views_min'] = data['views_min']
            params['views_max'] = data['views_max']
        full_ads = []
        #params['category'] = new_arr_links
        name1 = f'{name}'
        try:
            res = pd.read_excel(f'{name1}.xlsx', sheet_name='Result')
            def_arr = res.values.tolist()
        except:
            def_arr = []
        ads = await get_and_filter_all(params, new_arr_links, def_arr)
        full_ads += ads
        if len(ads) > 0:

            try:
                res = pd.read_excel(f'{name1}.xlsx', sheet_name='Result')
                def_arr = res.values.tolist()
                new_arr = []
                count_new_ads = 0
                for i in full_ads:
                    if i['idx'] not in str(def_arr):
                        new_arr.append(i)
                        def_arr.append([i['link'], i['name'], i['price'], i['views'], i['seller'], i['phone'], i['active_count'], i['sold_count']])
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
                    await query.message.answer(f'Готово. Найдено: {count_new_ads} объявлений, время сбора: {round(time.time() - st_time, 2)} секунд')
                    await query.message.answer_document(open(f'{name_to_send}.xlsx', 'rb'))
                    os.remove(f'{name_to_send}.xlsx')
                else:
                    await query.message.answer('Новых объявлений с такими параметрами не найдено')
            except:
                df = pd.DataFrame({'Link': [i['link'] for i in full_ads],
                                   'Name': [i['name'] for i in full_ads],
                                   'Price': [i['price'] for i in full_ads],
                                   'Views': [i['views'] for i in full_ads],
                                   'Seller': [i['seller'] for i in full_ads],
                                   'Phone': [i['phone'] for i in full_ads],
                                   'Active count': [i['active_count'] for i in full_ads],
                                   'Sold count': [i['sold_count'] for i in full_ads]})
                df.to_excel(f'{name1}.xlsx', sheet_name='Result', index=False)
                await query.message.answer(f'Готово. Найдено: {len(full_ads)} объявлений, время сбора: {round(time.time() - st_time, 2)} секунд')
                await query.message.answer_document(open(f'{name1}.xlsx', 'rb'))
        else:
            await query.message.answer('Объявлений с такими параметрами не найдено')
        col = db.collection('orders')
        db.insert_one_record(col, {'cid': query.from_user.id, 'category': f'{name}', 'date' : datetime.today().strftime("%d.%m.%Y %H:%M:%S")})
    else:
        await query.message.answer('Нет доступа.')


@dp.callback_query_handler(IsUser(), cat2_cb.filter(action='back2'))
async def process_choice_cat3_back(query: CallbackQuery, callback_data: dict, state: FSMContext):
    arr = get_names_link_categories()
    names_cat1 = get_arr_cat1(arr)
    # for i in names_cat1:
    #     print(i)
    markup = InlineKeyboardMarkup(row_width=1)
    for i in range(len(names_cat1)):
        btn = InlineKeyboardButton(names_cat1[i], callback_data=cat_cb.new(category=i, action='add_cat1'))
        markup.add(btn)
    btn = InlineKeyboardButton('👈 Назад', callback_data=cat_cb.new(category='back', action='back1'))
    markup.add(btn)
    await query.message.edit_reply_markup(markup)


@dp.callback_query_handler(IsUser(), cat2_cb.filter(action='add_cat2'))
async def process_choice_cat3(query: CallbackQuery, callback_data: dict, state: FSMContext):
    cat2 = callback_data['subcategory']
    user = get_user(query.from_user.id)
    if str(user['sub']) == '1':
        await query.message.answer('Данные собираются, ожидайте...')
        st_time = time.time()
        async with state.proxy() as data:
            params = {}
            params['category'] = cat2
            params['max_price'] = data['max_price']
            params['min_price'] = data['min_price']
            params['published'] = data['published']
            params['active_ad_min'] = data['active_ad_min']
            params['active_ad_max'] = data['active_ad_max']
            params['close_ad_min'] = data['close_ad_min']
            params['close_ad_max'] = data['close_ad_max']
            params['views_min'] = data['views_min']
            params['views_max'] = data['views_max']
            ads = await get_and_filter(params)

        df = pd.DataFrame({'Link': [i['link'] for i in ads],
                           'Name': [i['name'] for i in ads],
                           'Price': [i['price'] for i in ads],
                           'Views': [i['views'] for i in ads],
                           'Seller': [i['seller'] for i in ads],
                           'Phone': [' ' for i in ads],
                           'Active count': [i['active_count'] for i in ads],
                           'Sold count': [i['sold_count'] for i in ads]})
        if len(ads) > 0:

            name = f'{cat2}{round(time.time())}'
            df.to_excel(f'{name}.xlsx', sheet_name='Result', index=False)
            await query.message.answer(f'Готово. Найдено: {len(ads)} объявлений, время сбора: {round(time.time() - st_time, 2)} секунд')
            await query.message.answer_document(open(f'{name}.xlsx', 'rb'))
            os.remove(f'{name}.xlsx')
        else:
            await query.message.answer('Объявлений с такими параметрами не найдено')
        col = db.collection('orders')
        db.insert_one_record(col, {'cid': query.from_user.id, 'category': f'{params["category"]}'})
    else:
        await query.message.answer('Нет доступа.')