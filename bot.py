import telebot
from telebot import types
from telebot import apihelper

bot = telebot.TeleBot('1084734847:AAHiD4HulHbQGRmJ2U5iWqU-wJSKUCZzLNs')
apihelper.proxy = {'https': 'socks5h://PrhZ8F:eebLU48kCY@188.130.129.144:5501'}

def menu():
    glavmenu = types.InlineKeyboardMarkup(row_width=1)
    but_1 = types.InlineKeyboardButton(text='Японское меню', callback_data='yponmenu')
    but_2 = types.InlineKeyboardButton(text='Европейское меню', callback_data='evropmenu')
    but_3 = types.InlineKeyboardButton(text='Пицца', callback_data='pizza')
    glavmenu.add(but_1, but_2, but_3)
    return glavmenu


@bot.message_handler(commands=['start'])
def startpg(message):
    startmenu = types.ReplyKeyboardMarkup(True, False)
    startmenu.row('🍴 Меню', '🛍 Корзина')
    startmenu.row('📦 Заказы', '📢 Новости')
    startmenu.row('⚙️ Настройки', '❓ Помощь')
    bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=startmenu)

@bot.message_handler(content_types=['text'])
def osnov(message):
    if message.text == '🏠 Начало':
        global nachalo
        nachalo = 'nachalo'
        startpg(message)
    elif message.text == '🏠':
        startpg(message)
    elif message.text == '🍴 Меню':
        back = types.ReplyKeyboardMarkup(True, False)
        back.row('🏠 Начало')
        bot.send_message(message.chat.id, 'Меню', reply_markup=back)
        bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд:', reply_markup=menu())
    elif message.text == '🍴':
        back = types.ReplyKeyboardMarkup(True, False)
        back.row('🏠 Начало')
        bot.send_message(message.chat.id, 'Меню', reply_markup=back)
        bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд:', reply_markup=menu())
    elif message.text == '📢 Новости':
        back = types.ReplyKeyboardMarkup(True, False)
        back.row('🏠 Начало')
        bot.send_message(message.chat.id, 'заплати 50к и будет бот твоим', reply_markup=back)
    elif message.text == '❓ Помощь':
        back = types.ReplyKeyboardMarkup(True, False)
        back.row('🏠 Начало')
        bot.send_message(message.chat.id, 'Ваш будущий список команд:', reply_markup=back)
    elif message.text == '⚙️ Настройки':
        back = types.ReplyKeyboardMarkup(True, False)
        back.row('🏠 Начало')
        bot.send_message(message.chat.id, 'Ваши настройки:',reply_markup=back)


@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    if c.data == 'yponmenu':
        yaponmenu = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text='Гунканы', callback_data='gunkani')
        but_2 = types.InlineKeyboardButton(text='Закуски и салаты', callback_data='zakuskiisalat')
        but_3 = types.InlineKeyboardButton(text='Лапша и рис', callback_data='lapshairis')
        but_4 = types.InlineKeyboardButton(text='Нигири-суши', callback_data='nigirisushi')
        but_5 = types.InlineKeyboardButton(text='Основные блюда', callback_data='osnovbluda')
        but_6 = types.InlineKeyboardButton(text='Роллы', callback_data='rolli')
        but_7 = types.InlineKeyboardButton(text='В начало меню', callback_data='vnachalo')
        yaponmenu.add(but_1)
        yaponmenu.add(but_2)
        yaponmenu.add(but_3, but_4)
        yaponmenu.add(but_5, but_6)
        yaponmenu.add(but_5, but_6)
        yaponmenu.add(but_7)
        bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id, reply_markup=yaponmenu)
#Японское меню
    elif c.data == 'gunkani':
        gunkani1 = types.ReplyKeyboardMarkup(True, False)
        gunkani1.row('🏠', '🍴', '🛍', 'Еще 5')
        bot.send_message(c.message.chat.id, 'Гунканы:', reply_markup=gunkani1)
        gunkani11 = types.InlineKeyboardMarkup()
        but_11 = types.InlineKeyboardButton(text='1шт-69', callback_data='gunkani11')
        gunkani11.add(but_11)
        bot.send_photo(c.message.chat.id, 'https://sxodim.com/uploads/almaty/2018/06/bonito.jpg', caption='Икура\nИкра лосося\nВес: 28г\nОбъем: 1шт', reply_markup=gunkani11)
        gunkani12 = types.InlineKeyboardMarkup()
        but_12 = types.InlineKeyboardButton(text='1шт-75', callback_data='gunkani12')
        gunkani12.add(but_12)
        bot.send_photo(c.message.chat.id, 'https://domskidok.com/media/coupony/coupon/2015/07/13/sushi-rolly-vasabi-imbir-ris.jpg', caption='Нику темпура\nСыр эдам, бекон, соус авокадо\nВес: 150/30г', reply_markup=gunkani12)
    elif c.data == 'zakuskiisalat':
        zakuski1 = types.ReplyKeyboardMarkup(True, False)
        zakuski1.row('🏠', '🍴', '🛍')
        bot.send_message(c.message.chat.id, 'Гунканы:', reply_markup=zakuski1)
        zakuski11 = types.InlineKeyboardMarkup()
        but_11 = types.InlineKeyboardButton(text='210 Р', callback_data='zakuski11')
        zakuski11.add(but_11)
        bot.send_photo(c.message.chat.id, 'AgADAgADyKoxG_gXEUqcRXYCnY42BIFZOQ8ABJgZTnJccpiY7L0BAAEC', caption='Икура\nИкра лосося\nВес: 28г\nОбъем: 1шт', reply_markup=zakuski11)
        zakuski12 = types.InlineKeyboardMarkup()
        but_12 = types.InlineKeyboardButton(text='145', callback_data='zakuski12')
        zakuski12.add(but_12)
        bot.send_photo(c.message.chat.id, 'AgADAgADyaoxG_gXEUquYUd-Mlx4vMJmXw8ABGcU7DtW9U-VJPkAAgI', caption='Чука салат\nВодоросли и ореховый соус\nВес: 75/30г', reply_markup=zakuski12)
#В начало
    elif c.data == 'vnachalo':
        bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id, reply_markup=menu())
#Европейское меню
    elif c.data == 'evropmenu':
        evropmenu1 = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text='Гарниры', callback_data='garni')
        but_2 = types.InlineKeyboardButton(text='Десерты', callback_data='desert')
        but_3 = types.InlineKeyboardButton(text='Дополнительно', callback_data='dopol')
        but_4 = types.InlineKeyboardButton(text='Закуски', callback_data='zakus')
        but_5 = types.InlineKeyboardButton(text='Паста', callback_data='pasta')
        but_6 = types.InlineKeyboardButton(text='Рыба', callback_data='riba')
        but_7 = types.InlineKeyboardButton(text='В начало меню', callback_data='vnachalo')
        evropmenu1.add(but_1, but_2)
        evropmenu1.add(but_2)
        evropmenu1.add(but_3, but_4)
        evropmenu1.add(but_5, but_6)
        evropmenu1.add(but_5, but_6)
        evropmenu1.add(but_7)
        bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id, reply_markup=evropmenu1)

bot.polling()