import asyncio
import time

import aiohttp


async def delete_ads_by_owner_async(ads, params):

    global counter
    counter = 0
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in ads:
            task = asyncio.create_task(get_owner_async(session, i['idx']))
            tasks.append(task)
        res = await asyncio.gather(*tasks)
    new_ads_ = []

    for i, owner_param in zip(ads, res):
        try:
            if params['active_ad_min'] <= owner_param['prods_active_cnt'] <= params['active_ad_max']\
                    and params['close_ad_min'] <= owner_param['prods_sold_cnt'] <= params['close_ad_max'] \
                    and params['views_min'] <= owner_param['views'] <= params['views_max']:
                i['active_count'] = owner_param['prods_active_cnt']
                new_ads_.append(i)
        except:
            pass
    return new_ads_


async def get_owner_async(session, pid):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    url = f'https://api.youla.io/api/v1/product/{pid}'
    arr = {}
    f = False
    async with asyncio.Semaphore(500):
        try:
            response = await session.get(url=url, headers=headers)
            try:
                res1 = await response.json(content_type='application/json')
                f = True
            except:
                f = False
        except Exception as e:
            #print(e)
            pass
    if f:
        try:
            res = res1['data']
            owner = res['owner']
            try:
                arr['date_created'] = res['date_created']
            except:
                arr['date_created'] = 1658000000
            arr['prods_active_cnt'] = owner['prods_active_cnt']
            arr['prods_sold_cnt'] = owner['prods_sold_cnt']
            arr['owner_id'] = owner['id']
            arr['views'] = res['views']
            arr['price'] = res['discounted_price']
        except:
            f = False
    if not f:
        arr['prods_active_cnt'] = 1000000
        arr['prods_sold_cnt'] = 1000000
        arr['owner_id'] = 1000000
        arr['views'] = 1000000
        arr['price'] = 1000000
        arr['date_created'] = 1658000000

    return arr


async def delete_by_active_sold_ads_async(ads, params):
    new_ads = []
    global counter
    counter = 0
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in ads:
            task = asyncio.create_task(get_products_owner_async(session, i['seller']))
            tasks.append(task)
        res = await asyncio.gather(*tasks)
    for i, active_sold in zip(ads, res):
        count_active = 0
        count_sold = 0
        arr_active, arr_sold = active_sold
        for j in arr_active:
            if params['count_active_ad_by_price_price_min'] <= j <= params['count_active_ad_by_price_price_max']:
                count_active += 1
        for j in arr_sold:
            if params['count_sold_ad_by_price_price_min'] <= j <= params['count_sold_ad_by_price_price_max']:
                count_sold += 1
        if params['count_active_ad_by_price_min'] <= count_active <= params['count_active_ad_by_price_max'] \
                and params['count_sold_ad_by_price_min'] <= count_sold <= params['count_sold_ad_by_price_max']:
            new_ads.append(i)
    return new_ads


async def get_products_owner_async(session, id):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    timestamp = round(time.time() * 100)
    active_product_url = f'https://api.youla.io/api/v1/user/{id}/profile/products?app_id=web/3&uid=62d5752869b72&timestamp={timestamp}&limit=1000&show_inactive=0&features='
    sold_product_url = f'https://api.youla.io/api/v1/user/{id}/profile/soldproducts?app_id=web/3&uid=62d5752869b72&timestamp={timestamp}&limit=1000'
    f, f2 = False, False
    async with asyncio.Semaphore(500):
        try:
            response = await session.get(url=active_product_url, headers=headers)
            try:
                res1 = await response.json(content_type='application/json')
                f = True
            except:
                f = False
        except Exception as e:
            #print(e)
            pass
    if f:
        try:
            res = res1['data']
        except:
            f = False
    async with asyncio.Semaphore(500):
        try:
            response = await session.get(url=sold_product_url, headers=headers)
            try:
                res1 = await response.json(content_type='application/json')
                f2 = True
            except:
                f2 = False
        except Exception as e:
            #print(e)
            pass
    if f2:
        try:
            res2 = res1['data']
        except:
            f2 = False
    if f and f2:
        arr_active = [i['discounted_price'] / 100 for i in res]
        arr_sold = [i['discounted_price'] / 100 for i in res2]
    else:
        arr_active = []
        arr_sold = []
    global counter
    global ads
    counter += 1
    #sys.stderr.write(f'check active and sold {counter}/{len(ads)}\r')
    return arr_active, arr_sold


async def get_phones_async(ads):

    global counter
    counter = 0
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in ads:
            task = asyncio.create_task(get_phones(session, i['seller']))
            tasks.append(task)
        res = await asyncio.gather(*tasks)

    for i, phone in zip(ads, res):
        i['phone'] = phone

    return ads


async def get_phones(session, uid):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    url = f'https://api.youla.io/api/v1/users/{uid}/contact_info'
    arr = {}
    f = False
    async with asyncio.Semaphore(500):
        try:
            response = await session.get(url=url, headers=headers)
            try:
                res = await response.json()
                f = True
            except:
                f = False
        except Exception as e:
            #print(e)
            pass
    if f:
        try:
            print(res['data']['phone']['legacy'])
            return res['data']['phone']['legacy']
        except:
            return 0
    else:
        return 0

#
# def get_phone(uid):
#     headers = {
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
#     }
#     url = f'https://api.youla.io/api/v1/users/{uid}/contact_info'
#     res = requests.get(url=url, headers=headers)
#     print(res)
#     print(res.json())
