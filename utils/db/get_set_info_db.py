import time
from datetime import datetime, timedelta

from loader import db

'''Telegram Bot'''

'''Users'''


def create_user(cid, login, ref):
    col = db.collection('users')
    # date = datetime.today() + timedelta(days=1)
    # res = date.strftime("%d.%m.%Y %H:%M:%S")
    db.insert_one_record(col, {'cid': cid, 'login': login, 'referal': ref, 'bonus': 0, 'sub': '0', 'notice': 0})


def get_user(cid):
    col = db.collection('users')
    return db.find_one_record(col, {'cid': int(cid)})


def get_users():
    col = db.collection('users')
    return db.find_records(col, {})


def update_user_sub(cid, add_days):
    col = db.collection('users')
    # sub_date = db.find_one_record(col, {'cid': int(cid)})['sub']
    #
    # date_time = datetime.strptime(sub_date, '%d.%m.%Y %H:%M:%S')
    # if date_time > datetime.today():
    #     date = date_time + timedelta(days=int(add_days))
    # else:
    #     date = datetime.today() + timedelta(days=int(add_days))
    # res = date.strftime("%d.%m.%Y %H:%M:%S")
    db.update_one_record(col, {'cid': int(cid)}, {'$set': {'sub': add_days}})


def update_user_bonus(cid, bonus):
    col = db.collection('users')
    user = db.find_one_record(col, {'cid': int(cid)})
    bonus = float(bonus)
    bonus += float(user['bonus'])
    db.update_one_record(col, {'cid': int(cid)}, {'$set': {'bonus': round(bonus, 2)}})


def update_user_notice(cid, notice):
    col = db.collection('users')
    db.update_one_record(col, {'cid': int(cid)}, {'$set': {'notice': notice}})


'''Templates'''


def create_template(params):
    col = db.collection('templates')
    db.insert_one_record(col,
                         {'cid': int(params['cid']), 'tid': int(params['tid']), 'min_price': int(params['min_price']),
                          'max_price': int(params['max_price']),
                          'published': int(params['published']), 'close_ad_min': int(params['close_ad_min']),
                          'close_ad_max': int(params['close_ad_max']), 'active_ad_min': int(params['active_ad_min']),
                          'active_ad_max': int(params['active_ad_max']), 'views_min': int(params['views_min']),
                          'views_max': int(params['views_max'])})


def get_templates_cid(cid):
    col = db.collection('templates')
    res = db.find_records(col, {'cid': int(cid)})
    ads = []
    for i in res:
        i['_id'] = '123'
        ads.append(i)
    return ads


def get_template_cid_tid(cid, tid):
    col = db.collection('templates')
    return db.find_one_record(col, {'tid': int(tid), 'cid': int(cid)})


def delete_template(tid):
    col = db.collection('templates')
    db.delete_one_record(col, {'tid': tid})


'''Orders'''


def create_order():
    pass


'''Pars info'''


def get_table(params):
    category = params['category']
    max_price = params['max_price']
    min_price = params['min_price']
    published = params['published'] * 60
    close_ad_min = params['close_ad_min']
    close_ad_max = params['close_ad_max']
    views_min = params['views_min']
    views_max = params['views_max']
    pub = round(time.time() - published)
    col = db.collection(category)
    cond = {'pub_date': {'$gt': pub}, 'price': {'$gte': min_price, '$lte': max_price},
            'views': {'$gte': views_min, '$lte': views_max},
            'sold_count': {'$gte': close_ad_min, '$lte': close_ad_max}}
    st = time.time()
    res = db.find_records(col, cond)

    print(time.time() - st)
    # ads = []
    # for i in res:
    #     i['_id'] = '123'
    #     if i['pub_date'] > pub and min_price <= i['price'] <= max_price:
    #         ads.append(i)
    return res


def get_full_table():
    col = db.collection('full')
    res = db.find_records(col, {})
    return [i for i in res]


def get_ad_by_id(idx, category):
    col = db.collection(category)
    cond = {'idx': idx}
    res = db.find_records(col, cond)
    ads = []
    for i in res:
        i['_id'] = '123'
        ads.append(i)
    return ads


def create_message(cid, m):
    col = db.collection('messages')
    print(cid, m)
    db.insert_one_record(col, {'cid': cid, 'message': m})


def get_messages():
    col = db.collection('messages')
    return db.find_records(col, {})


def delete_message(cid, m):
    col = db.collection('messages')
    db.delete_one_record(col, {'cid': cid, 'message': m})


'''Buffer'''


def get_from_buffer():
    col = db.collection('buffer')
    result = db.find_records(col, {})
    # db.delete_records(col, {})
    return [i for i in result]


def clear_buffer():
    col = db.collection('buffer')
    db.delete_records(col, {})


'''Telegram Bot End'''



