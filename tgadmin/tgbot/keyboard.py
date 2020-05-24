from telebot import types
from tgbot.models import CategoryOne, Configuration


def basket_menu(id_product, count, arr, forward=0, down=0, number_str=1, finite_sum=0):
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    but_11 = types.InlineKeyboardButton(text='❌', callback_data='deleting|{}'.format(id_product))
    but_12 = types.InlineKeyboardButton(text='🔺',
                                        callback_data='add|{0}|{1}|{2}|{3}'.format(id_product, forward,
                                                                                   down, number_str))
    but_13 = types.InlineKeyboardButton(text='{} шт.'.format(count), callback_data='empty')
    if count == 1:
        but_14 = types.InlineKeyboardButton(text='🔻', callback_data='empty')
    else:
        but_14 = types.InlineKeyboardButton(text='🔻',
                                            callback_data='r|{0}|{1}|{2}|{3}'.format(id_product, forward,
                                                                                     down, number_str))
    if forward == 0 and down == 0:
        but_21 = types.InlineKeyboardButton(text='◀️', callback_data='empty')
        but_22 = types.InlineKeyboardButton(text='1/{}'.format(arr), callback_data='empty')
        but_23 = types.InlineKeyboardButton(text='▶️', callback_data='empty')
    else:
        but_21 = types.InlineKeyboardButton(text='◀️', callback_data='down|{}'.format(down))
        but_22 = types.InlineKeyboardButton(text='{}/{}'.format(number_str, arr), callback_data='empty')
        but_23 = types.InlineKeyboardButton(text='▶️', callback_data='first|{}'.format(forward))
    min_sum = Configuration.objects.get(id=1).min_sum
    if min_sum > finite_sum:
        but_31 = types.InlineKeyboardButton(text=f'✅ Оформить заказ на {finite_sum} ₽',
                                            callback_data=f'min_sum|{min_sum}')
    else:
        but_31 = types.InlineKeyboardButton(text=f'✅ Оформить заказ на {finite_sum} ₽',
                                            callback_data='order_registration')
    keyboard.add(but_11, but_12, but_13, but_14)
    keyboard.add(but_21, but_22, but_23)
    keyboard.add(but_31)
    return keyboard


def keyboard_time():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('✅ Верно')
    keyboard.row('Как можно скорее')
    keyboard.row('🏠 Начало', '⬅️ Назад')
    return keyboard


def keyboard_back():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('🏠 Начало', '⬅️ Назад')
    return keyboard


def keyboard_back_admin():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('⬅️ Назад')
    return keyboard


def keyboard_admin():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('✏️Изменить новость')
    keyboard.row('📰Посмотреть текущую новость')
    keyboard.row('📩Сделать рассылку текущей новости')
    keyboard.row('📧Сделать разовую рассылку')
    keyboard.row('🔙Выйти из админ панели')
    return keyboard


def submenu():
    back = types.ReplyKeyboardMarkup(True, False)
    back.row('✅ Верно')
    back.row('🏠 Начало', '⬅️ Назад')
    return back


def keyboard_delivery():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('✅ Верно')
    keyboard.row('🏃 Заберу сам', '🚗 Привезти')
    keyboard.row('🏠 Начало', '⬅️ Назад')
    return keyboard


def keyboard_sum():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('🏠 Начало', '🍴 Меню')
    return keyboard


def keyboard_number():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('✅ Верно')
    button_phone = types.KeyboardButton(text="Отправить мой номер телефона ☎️", request_contact=True)
    keyboard.add(button_phone)
    keyboard.row('🏠 Начало', '⬅️ Назад')
    return keyboard


def keyboard_no_mobile():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    button_phone = types.KeyboardButton(text="Отправить мой номер телефона ☎️", request_contact=True)
    keyboard.add(button_phone)
    keyboard.row('🏠 Начало', '⬅️ Назад')
    return keyboard


def keyboard_help():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('✉️Вопрос оператору')
    keyboard.row('🏠 Начало')
    return keyboard


def keyboard_setting():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('Имя', 'Моб.', 'Адрес')
    keyboard.row('🏠 Начало')
    return keyboard


def keyboard_down():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('🏠 Начало')
    return keyboard


def menu():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for i in CategoryOne.objects.all():
        if i.categorytwo_set.count() != 0:
            but = types.InlineKeyboardButton(text=i.name, callback_data=f'm1|{i.id}')
        else:
            if i.name == 'Пицца':
                but = types.InlineKeyboardButton(text=i.name, callback_data=f'pizza|{i.id}')
            else:
                but = types.InlineKeyboardButton(text=i.name, callback_data=f'sm|{i.id}')
        keyboard.add(but)
    return keyboard


def keyboard_confirm():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('✅ Подтвердить и отправить')
    keyboard.row('🏠 Начало', '⬅️ Назад')
    return keyboard



def keyboard_of_menu():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('🏠', '🍴', '🛍')
    return keyboard


def start_menu():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('🍴 Меню', '🛍 Корзина')
    keyboard.row('📦 Заказы', '📢 Новости')
    keyboard.row('⚙️ Настройки', '❓ Помощь')
    return keyboard


def update_object_menu(price, volume, count, callback):
    keyboard = types.InlineKeyboardMarkup()
    if volume is None:
        keyboard.add(types.InlineKeyboardButton(text='1шт - {} ₽ ({} шт.)'.format(price, count),
                                                callback_data=callback))
    else:
        keyboard.add(types.InlineKeyboardButton(text='{}шт - {} ₽ ({} шт.)'.format(volume, price, count),
                                                callback_data=callback))
    keyboard.add(types.InlineKeyboardButton(text='🛍 Корзина', callback_data="Korzina"))
    return keyboard


def menu_two(count, arr):
    keyboard = types.InlineKeyboardMarkup()
    if count % 2 == 0:
        for i in range(0, count, 2):
            but_1 = types.InlineKeyboardButton(text=arr[i].name, callback_data=f'm2|{arr[i].id}')
            but_2 = types.InlineKeyboardButton(text=arr[i + 1].name, callback_data=f'm2|{arr[i + 1].id}')
            keyboard.add(but_1, but_2)
    else:
        but_0 = types.InlineKeyboardButton(text=arr[0].name, callback_data=f'm2|{arr[0].id}')
        keyboard.add(but_0)
        for i in range(1, count, 2):
            but_1 = types.InlineKeyboardButton(text=arr[i].name, callback_data=f'm2|{arr[i].id}')
            but_2 = types.InlineKeyboardButton(text=arr[i + 1].name, callback_data=f'm2|{arr[i + 1].id}')
            keyboard.add(but_1, but_2)
    but_down = types.InlineKeyboardButton(text='В начало меню', callback_data='vnachalo')
    keyboard.add(but_down)
    return keyboard
