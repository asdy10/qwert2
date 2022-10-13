import asyncio
import time
from itertools import groupby

from utils.db.get_set_info_db import get_table
from utils.youla_api.get_info import delete_ads_by_owner_async, get_phones_async


async def get_and_filter(params):
    st_full_time = time.time()
    ads = get_table(params)
    ads2 = []
    ads_idx = []
    for i in ads:
        if i['idx'] not in ads_idx:
            ads2.append(i)
            ads_idx.append(i['idx'])
    ads = ads2.copy()
    mid_time = time.time()
    ads = await delete_ads_by_owner_async(ads, params)
    print('filtered by owner          ', len(ads), round(time.time() - mid_time, 4), params['category'])
    # mid_time = time.time()
    # ads = asyncio.get_event_loop().run_until_complete(delete_by_active_sold_ads_async(ads, params))
    # print('filtered by active and sold', len(ads), round(time.time() - mid_time, 4), params['category'])
    print('end', time.time() - st_full_time)
    return ads


async def get_and_filter_all(params, new_arr_links, def_arr):
    st_full_time = time.time()
    ads = []
    print('start get info from db')
    for i in new_arr_links:
        params['category'] = i
        ads += get_table(params)
    ads2 = []
    ads_idx = []
    print('get all from db', len(ads), time.time() - st_full_time)
    mid_time = time.time()
    for i in ads:
        if i['seller'] not in ads_idx :#and i['idx'] not in str(def_arr)
            ads2.append(i)
            ads_idx.append(i['seller'])
    ads = ads2.copy()
    print('filtered db', len(ads), time.time() - mid_time)
    mid_time = time.time()
    ads = await delete_ads_by_owner_async(ads, params)
    #ads = await get_phones_async(ads)
    print('filtered by owner          ', len(ads), round(time.time() - mid_time, 4), params['category'])
    # mid_time = time.time()
    # ads = asyncio.get_event_loop().run_until_complete(delete_by_active_sold_ads_async(ads, params))
    # print('filtered by active and sold', len(ads), round(time.time() - mid_time, 4), params['category'])
    print('end', time.time() - st_full_time)
    return ads