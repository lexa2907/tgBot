from telebot import types
import json
from tgbot.models import CategoryOne


def newmenu(id_product, count, arr, forward=0, down=0, number_str=1, finite_sum=0):
    product = types.InlineKeyboardMarkup(row_width=4)
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
    with open('sum.json', 'r') as f:
        max_sum = json.load(f)
    if max_sum["max_sum"] > finite_sum:
        but_31 = types.InlineKeyboardButton(text=f'✅ Оформить заказ на {finite_sum} ₽',
                                            callback_data=f'max_sum|{max_sum["max_sum"]}')
    else:
        but_31 = types.InlineKeyboardButton(text=f'✅ Оформить заказ на {finite_sum} ₽',
                                            callback_data='order_registration')
    product.add(but_11, but_12, but_13, but_14)
    product.add(but_21, but_22, but_23)
    product.add(but_31)
    return product


def submenu():
    back = types.ReplyKeyboardMarkup(True, False)
    back.row('✅ Верно')
    back.row('🏠 Начало', '⬅️ Назад')
    return back


def keyboard_number():
    back = types.ReplyKeyboardMarkup(True, False)
    back.row('✅ Верно')
    button_phone = types.KeyboardButton(text="Отправить мой номер телефона ☎️", request_contact=True)
    back.add(button_phone)
    back.row('🏠 Начало', '⬅️ Назад')
    return back


def menu():
    glavmenu = types.InlineKeyboardMarkup(row_width=1)
    for i in CategoryOne.objects.all():
        if i.name == 'Пицца':
            but = types.InlineKeyboardButton(text=i.name, callback_data=f'pizza')
        else:
            but = types.InlineKeyboardButton(text=i.name, callback_data=f'm1|{i.id}')
        glavmenu.add(but)
    return glavmenu


def startmenu():
    startmenu = types.ReplyKeyboardMarkup(True, False)
    startmenu.row('🍴 Меню', '🛍 Корзина')
    startmenu.row('📦 Заказы', '📢 Новости')
    startmenu.row('⚙️ Настройки', '❓ Помощь')
    return startmenu