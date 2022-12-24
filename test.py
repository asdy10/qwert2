import asyncio
import time
from collections import Counter
from datetime import timedelta
from itertools import groupby

from utils.db.get_set_info_db import *

# res = get_user(383552200)
# print(res['cid'], res['sub'])
# if not get_user(383552200):
#
#     create_user(383552200, 'login name')
# else:
#     print('user exist')
# update_user(383552200, 100)
from utils.youla_api.get_info import delete_ads_by_owner_async, delete_by_active_sold_ads_async

category1 = ['Вещи, электроника и прочее', 'Запчасти и автотовары']
category2 = {'Женский гардероб': 'zhenskaya-odezhda', 'Мужской гардероб': 'muzhskaya-odezhda',
             'Детский гардероб': 'detskaya-odezhda',
             'Детские товары': 'detskie', 'Хэндмейд': 'hehndmejd', 'Телефоны и планшеты': 'smartfony-planshety',
             'Фото- и видеокамеры': 'foto-video', 'Компьютерная техника': 'kompyutery',
             'ТВ, аудио, видео': 'ehlektronika',
             'Бытовая техника': 'bytovaya-tekhnika', 'Для дома и дачи': 'dom-dacha',
             'Стройматериалы и инструменты': 'remont-i-stroitelstvo',
             'Красота и здоровье': 'krasota-i-zdorove', 'Спорт и отдых': 'sport-otdyh',
             'Хобби и развлечения': 'hobbi-razvlecheniya', 'Прочее': 'prochee'}

avto_moto = {'Запчасти': 'avtozapchasti', 'Шины и диски': 'shiny-diski', 'Масла и автохимия': 'avtohimiya',
             'Автоэлектроника и GPS': 'avtoelektronika-i-gps',
             'Аксессуары и инструменты': 'aksessuary-i-instrumenty',
             'Аудио и видео': 'audio-video','Противоугонные устройства': 'protivougonnye-ustrojstva',
             'Багажные системы и прицепы': 'bagazhniki-farkopy',
             'Мотоэкипировка': 'motoehkipirovka','Другое': 'drugoe'}


full_array = {'Женский гардероб': {'Аксессуары': 'aksessuary', 'Блузы и рубашки': 'bluzy-rubashki', 'Будущим мамам': 'dlya-beremennyh', 'Верхняя одежда': 'verhnyaya', 'Головные уборы': 'golovnye-ubory', 'Домашняя одежда': 'domashnyaya', 'Комбинезоны': 'kombinezony', 'Купальники': 'kupalniki', 'Нижнее белье': 'bele-kupalniki', 'Обувь': 'obuv', 'Пиджаки и костюмы': 'pidzhaki-kostyumy', 'Платья и юбки': 'platya-yubki', 'Свитеры и толстовки': 'svitery-tolstovki', 'Спортивная одежда': 'sportivnaya', 'Футболки и топы': 'futbolki-topy', 'Штаны и шорты': 'dzhinsy-bryuki', 'Другое': 'drugoe'},
              'Мужской гардероб': {'Аксессуары': 'aksessuary', 'Верхняя одежда': 'verhnyaya', 'Головные уборы': 'golovnye-ubory', 'Домашняя одежда': 'domashnyaya', 'Комбинезоны': 'kombinezony', 'Нижнее белье': 'nizhnee-bele-plavki', 'Обувь': 'obuv', 'Пиджаки и костюмы': 'pidzhaki-kostyumy', 'Рубашки': 'rubashki', 'Свитеры и толстовки': 'svitery-tolstovki', 'Спецодежда': 'specodezhda', 'Спортивная одежда': 'sportivnaya', 'Футболки и поло': 'futbolki-polo', 'Штаны и шорты': 'dzhinsy-bryuki', 'Другое': 'drugoe'},
              'Детский гардероб': {'Аксессуары': 'aksessuary', 'Блузы и рубашки': 'bluzy-i-rubashki', 'Верхняя одежда': 'verhnyaya-odezhda', 'Головные уборы': 'golovnye-ubory', 'Домашняя одежда': 'domashnyaya-odezhda', 'Комбинезоны и боди': 'kombinezony-i-bodi', 'Конверты': 'konverty', 'Нижнее белье': 'nizhnee-bele', 'Обувь': 'obuv', 'Пиджаки и костюмы': 'pidzhaki-i-kostyumy', 'Платья и юбки': 'platya-i-yubki', 'Ползунки и распашонки': 'polzunki-i-raspashonki', 'Свитеры и толстовки': 'svitery-i-tolstovki', 'Спортивная одежда': 'sportivnaya-odezhda', 'Футболки': 'futbolki', 'Штаны и шорты': 'shtany-i-shorty', 'Другое': 'drugoe'},
              'Детские товары': {'Автокресла': 'avtokresla', 'Здоровье и уход': 'zdorove-i-uhod', 'Игрушки и игры': 'kukly-igrushki', 'Коляски': 'kolyaski', 'Кормление и питание': 'kormlenie-pitanie', 'Купание': 'kupanie', 'Обустройство детской': 'mebel', 'Подгузники и горшки': 'podguzniki-pelenki', 'Радио- и видеоняни': 'radio-i-videonyani', 'Товары для мам': 'tovary-dlya-mam', 'Товары для учебы': 'tovary-dlya-ucheby', 'Другое': 'drugoe'},
              'Хэндмейд': {'Косметика': 'kosmetika', 'Украшения': 'ukrasheniya', 'Куклы и игрушки': 'kukly-igrushki', 'Оформление интерьера': 'oformlenie-interera', 'Аксессуары': 'aksessuary', 'Оформление праздников': 'oformlenie-prazdnikov', 'Канцелярия': 'kancelyarskie-tovary', 'Посуда': 'posuda', 'Другое': 'drugoe'},
              'Телефоны и планшеты': {'Мобильные телефоны': 'smartfony', 'Планшеты': 'planshety', 'Умные часы и браслеты': 'umnye-chasy', 'Стационарные телефоны': 'stacionarnye-telefony', 'Рации и спутниковые телефоны': 'racii-i-sputnikovye-telefony', 'Запчасти': 'zapchasti', 'Внешние аккумуляторы': 'vneshnie-akkumulyatory', 'Зарядные устройства': 'zaryadnye-ustrojstva', 'Чехлы': 'chekhly', 'Аксессуары': 'aksessuary'},
              'Фото- и видеокамеры': {'Фотоаппараты': 'fotoapparaty', 'Видеокамеры': 'videokamery', 'Видеонаблюдение': 'videonablyudenie', 'Объективы': 'obektivy', 'Фотовспышки': 'fotovspyshki', 'Аксессуары': 'aksessuary', 'Штативы и стабилизаторы': 'shtativy-monopody', 'Студийное оборудование': 'studyinoe-oborudovanie', 'Цифровые фоторамки': 'fotoramki', 'Компактные фотопринтеры': 'fotoprintery', 'Бинокли и оптические приборы': 'binokli-teleskopy'},
              'Компьютерная техника': {'Ноутбуки': 'noutbuki', 'Компьютеры': 'monobloki', 'Мониторы': 'monitory', 'Клавиатуры и мыши': 'klaviatury-i-myshi', 'Оргтехника и расходники': 'printery-i-skanery', 'Сетевое оборудование': 'setevoe-oborudovanie', 'Мультимедиа': 'multimedia', 'Накопители данных и картридеры': 'nakopiteli-dannyh-i-kartridery', 'Программное обеспечение': 'programmnoe-obespechenie', 'Рули, джойстики, геймпады': 'ruli-dzhoistiki-geympady', 'Комплектующие и запчасти': 'komplektuyushchie', 'Аксессуары': 'aksessuary'},
              'ТВ, аудио, видео': {'Телевизоры': 'televizory-proektory', 'Проекторы': 'proektory', 'Акустика, колонки, сабвуферы': 'akusticheskie-sistemy', 'Домашние кинотеатры': 'domashnie-kinoteatry', 'DVD, Blu-ray и медиаплееры': 'mediapleery', 'Музыкальные центры и магнитолы': 'muzykalnye-centry-i-magnitoly', 'MP3-плееры и портативное аудио': 'mp3-pleery', 'Электронные книги': 'ehlektronnye-knigi', 'Спутниковое и цифровое ТВ': 'sputnikovoe-i-cifrovoe-tv', 'Аудиоусилители и ресиверы': 'usiliteli-resivery', 'Наушники': 'naushniki', 'Микрофоны': 'mikrofony', 'Аксессуары': 'aksessuary'},
              'Бытовая техника': {'Весы': 'vesy', 'Вытяжки': 'vytyazhki', 'Измельчение и смешивание': 'izmelchenie-i-smeshivanie', 'Климатическая техника': 'klimaticheskaya', 'Кулеры и фильтры для воды': 'kulery-i-filtry-dlya-vody', 'Плиты и духовые шкафы': 'plity', 'Посудомоечные машины': 'posudomoechnye-mashiny', 'Приготовление еды': 'prigotovlenie-edy', 'Приготовление напитков': 'prigotovlenie-napitkov', 'Пылесосы и пароочистители': 'pylesosy', 'Стиральные машины': 'stiralnye-mashiny', 'Утюги и уход за одеждой': 'utyugi', 'Холодильники': 'holodilniki', 'Швейное оборудование': 'shvejnoe-oborudovanie'},
              'Для дома и дачи': {'Бытовая химия': 'bitovaya-himiya', 'Диваны и кресла': 'divany-kresla', 'Кровати и матрасы': 'krovati', 'Кухонные гарнитуры': 'kuhonnaya-mebel', 'Освещение': 'osveshchenie', 'Оформление интерьера': 'oformlenie-interera', 'Охрана и сигнализации': 'ohrana-signalizaciya', 'Подставки и тумбы': 'podstavki-tumby', 'Посуда': 'posuda', 'Растения и семена': 'rasteniya', 'Сад и огород': 'sad-ogorod', 'Садовая мебель': 'sadovaya-mebel', 'Столы и стулья': 'stoly-stulya', 'Текстиль и ковры': 'tekstil-kovry', 'Шкафы и комоды': 'shkafy-komody', 'Другое': 'drugoe'},
              'Стройматериалы и инструменты': {'Двери': 'dveri', 'Измерительные инструменты': 'izmeritelnye-instrumenty', 'Окна': 'okna', 'Отопление и вентиляция': 'otoplenie-ventilyaciya', 'Потолки': 'potolki', 'Ручные инструменты': 'ruchnye-instrumenty', 'Сантехника и водоснабжение': 'santekhnika', 'Стройматериалы': 'strojmaterialy', 'Электрика': 'ehlektrika', 'Электроинструменты': 'ehlektroinstrumenty', 'Другое': 'drugoe'},
              'Красота и здоровье': {'Макияж': 'makiyazh', 'Маникюр и педикюр': 'manikyur-pedikyur', 'Товары для здоровья': 'medicinskie-tovary', 'Парфюмерия': 'parfyumeriya', 'Стрижка и удаление волос': 'strizhka-brite', 'Уход за волосами': 'uhod-za-volosami', 'Уход за кожей': 'uhod-za-licom', 'Фены и укладка': 'feny-ukladka', 'Тату и татуаж': 'tatu-i-tatuazh', 'Солярии и загар': 'solyarii-i-zagar', 'Средства для гигиены': 'sredstva-dlya-gigieny', 'Другое': 'drugoe'},
              'Спорт и отдых': {'Спортивная защита': 'sportivnaya-zashhita', 'Велосипеды': 'velosipedy-samokaty', 'Ролики и скейтбординг': 'roliki-skejtbording', 'Самокаты и гироскутеры': 'samokaty-i-giroskutery', 'Бильярд и боулинг': 'bilyard-i-bouling', 'Водные виды спорта': 'vodnye-vidy', 'Единоборства': 'edinoborstva', 'Зимние виды спорта': 'zimnie-vidy', 'Игры с мячом': 'igry-s-myachom', 'Охота и рыбалка': 'ohota-rybalka', 'Туризм и отдых на природе': 'turizm', 'Теннис, бадминтон, дартс': 'tennis-badminton-ping-pong', 'Тренажеры и фитнес': 'trenazhery-fitnes', 'Спортивное питание': 'sportivnoe-pitanie', 'Другое': 'drugoe'},
              'Хобби и развлечения': {'Билеты': 'bilety', 'Видеофильмы': 'filmy', 'Игровые приставки': 'konsoli-igry', 'Игры для приставок и ПК': 'igry-dlya-pristavok-i-pk', 'Книги и журналы': 'knigi-zhurnaly', 'Коллекционирование': 'kollekcionirovanie', 'Материалы для творчества': 'materialy-dlya-tvorchestva', 'Музыка': 'muzyka', 'Музыкальные инструменты': 'muzykalnye-instrumenti', 'Настольные игры': 'nastolnye-igry', 'Другое': 'drugoe'},
              'Прочее': {'Другое': 'drugoe'}}
arr_names = []
for i in full_array:
    for j in full_array[i]:
        arr_names.append(full_array[i][j])
arr_ = Counter(arr_names)
arr_new_names = ['svitery-i-tolstovki', 'konverty', 'bluzy-i-rubashki', 'nizhnee-bele',
                 'sportivnaya-odezhda', 'verhnyaya-odezhda', 'platya-yubki', 'kupalniki', 'zdorove-i-uhod',
                 'radio-i-videonyani', 'ukrasheniya', 'kupanie', 'tovary-dlya-mam', 'futbolki',
                 'domashnyaya-odezhda', 'pidzhaki-i-kostyumy', 'platya-i-yubki',
                 'polzunki-i-raspashonki',
                 'kombinezony-i-bodi', 'shtany-i-shorty', 'tovary-dlya-ucheby']
for i in arr_:
    if arr_[i] > 1:
        arr_new_names.append(i)


def check_count_ads():
    params = {}
    task_array = []
    full_names_array = []
    for cat in avto_moto:

        params['default_category'] = 'avto-moto'
        if avto_moto[cat] in arr_new_names:
            params['category'] = f'avto-moto-{avto_moto[cat]}'

        else:
            params['category'] = f'{avto_moto[cat]}'
        task_array.append(params.copy())

        full_names_array.append([{'Запчасти и автотовары': 'avto-moto'}, {cat: params['category']}])
        params = {}
        # print(params['category'])
    for cat in category2:
        params['default_category'] = category2[cat]
        for cat2 in full_array[cat]:
            if full_array[cat][cat2] in arr_new_names:
                params['category'] = f'{category2[cat]}-{full_array[cat][cat2]}'
            else:
                params['category'] = f'{full_array[cat][cat2]}'
            # print(params['category'])
            if params['category'] == 'muzhskaya-odezhda-domashnyaya':
                params['category'] = 'domashnyaya'
            if params['category'] == 'ehlektronika-aksessuary':
                params['category'] = 'aksessuary'
            full_names_array.append([{cat: category2[cat]}, {cat2: params['category']}])
            task_array.append(params.copy())
            params = {}

    # for tab in task_array:
    #     print(tab, tab['category'])
    arr = []
    for i in full_names_array:
        print(i)
        # if [j for j in i.keys()][0] not in arr:
        #     arr.append([j for j in i.keys()][0])
    # for i in arr:
    #     print(i)


def test():
    st_full_time = time.time()
    params = {}
    params['name'] = 'bluzy-rubashki'
    params['category'] = params['name']
    params['max_price'] = 20000
    params['min_price'] = 1000
    params['published'] = 3600
    params['close_ad_min'] = 0
    params['close_ad_max'] = 10
    params['active_ad_min'] = 0
    params['active_ad_max'] = 10
    params['views_min'] = 0
    params['views_max'] = 10
    st_time = time.time()
    ads = get_table(params)
    ads = [el for el, _ in groupby(ads)]
    mid_time = time.time()
    ads = asyncio.get_event_loop().run_until_complete(delete_ads_by_owner_async(ads, params))
    print('filtered by owner          ', len(ads), round(time.time() - mid_time, 4), params['category'])
    # mid_time = time.time()
    # ads = asyncio.get_event_loop().run_until_complete(delete_by_active_sold_ads_async(ads, params))
    # print('filtered by active and sold', len(ads), round(time.time() - mid_time, 4), params['category'])
    print('end', time.time() - st_full_time)
    return ads

def t(add_days):
    print(time.time() - 1650174726)
    date = datetime.today() + timedelta(days=add_days)
    print(date)
    res = date.strftime("%d.%m.%Y %H:%M:%S")
    print('res_date', res)
    date_time = datetime.strptime(res, '%d.%m.%Y %H:%M:%S')
    print('chek date', date_time)
    if date_time > datetime.today():
        print('yes')

if __name__ == '__main__':
    print(1634175284)
    print(datetime.fromtimestamp(1634175284))
