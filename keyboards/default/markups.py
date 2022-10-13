from aiogram.types import ReplyKeyboardMarkup

back_message = '👈 Назад'
confirm_message = '✅ Подтвердить'
all_right_message = '✅ Все верно'
cancel_message = '🚫 Отменить'
change_message = '✍️  Изменить'
ready_message = '✅  Готово'

account_info = 'Мой аккаунт'
continue_subscribe = 'Продлить подписку'
notices = 'Уведомления'

balance = '💰 Баланс'
add_balance = 'Пополнить баланс'
make_payment = '💳 Оплатить'
link_for_payment = '🔗 Ссылка на оплату'


archive_buyouts = '🔺 Архивные выкупы'


templates = '📂 Шаблоны'
my_templates = '🗂Мои шаблоны'
make_template = '✅  Создать шаблон'

timetable_buyouts = '📆 Графики выкупов'
my_timetable = '🗓 Мои графики'
make_timetable = '✅ Создать график'

info = '📚 Информация'
user_stat = '📊 Статистика рефералов'

admin_set_sub = 'Добавить подписку'
admin_set_bonus = 'Добавить реф бонус'


notice_choice_template = 'Выбрать шаблон для уведомлений'
notice_off = 'Отключить уведомления'


def user_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    #markup.add(account_info)
    markup.add(my_templates, make_template)
    markup.add(notice_choice_template, notice_off)

    return markup


def confirm_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(confirm_message)
    markup.add(back_message)

    return markup


def back_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)

    return markup


def cancel_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(cancel_message)

    return markup


def check_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(back_message, all_right_message)

    return markup


def submit_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(cancel_message, all_right_message)

    return markup


def admin_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(admin_set_sub, admin_set_bonus)
    return markup
