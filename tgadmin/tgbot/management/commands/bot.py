from django.core.management.base import BaseCommand
import telebot
from telebot import types
from telebot import apihelper
from django.db.models import F, IntegerField
import re
from django.db.models import Sum
from tgbot.models import Arrr, Category1, Meni, Users, Basket


class Command(BaseCommand):
    help = "ТЕлеграмм бот"

    def handle(self, *args, **options):
        bot = telebot.TeleBot('1084734847:AAHiD4HulHbQGRmJ2U5iWqU-wJSKUCZzLNs')
        apihelper.proxy = {'https': 'socks5h://PrhZ8F:eebLU48kCY@188.130.129.144:5501'}

        def newmenu(id, count, arr, nextt=0, down=0, str=1, finite_sum=0):
            product = types.InlineKeyboardMarkup(row_width=4)
            but_11 = types.InlineKeyboardButton(text='❌', callback_data='deleting|{}'.format(id))
            but_12 = types.InlineKeyboardButton(text='🔺',
                                                callback_data='add|{0}|{1}|{2}|{3}'.format(id, nextt, down, str))
            but_13 = types.InlineKeyboardButton(text='{} шт.'.format(count), callback_data='empty')
            if count == 1:
                but_14 = types.InlineKeyboardButton(text='🔻', callback_data='empty')
            else:
                but_14 = types.InlineKeyboardButton(text='🔻',
                                                    callback_data='r|{0}|{1}|{2}|{3}'.format(id, nextt, down, str))
            if nextt == 0 and down == 0:
                but_21 = types.InlineKeyboardButton(text='◀️', callback_data='empty')
                but_22 = types.InlineKeyboardButton(text='1/{}'.format(arr), callback_data='empty')
                but_23 = types.InlineKeyboardButton(text='▶️', callback_data='empty')
            else:
                but_21 = types.InlineKeyboardButton(text='◀️', callback_data='down|{}'.format(down))
                but_22 = types.InlineKeyboardButton(text='{}/{}'.format(str, arr), callback_data='empty')
                but_23 = types.InlineKeyboardButton(text='▶️', callback_data='first|{}'.format(nextt))
            but_31 = types.InlineKeyboardButton(text=f'✅ Оформить заказ на {finite_sum} ₽',
                                                callback_data='order_registration')
            product.add(but_11, but_12, but_13, but_14)
            product.add(but_21, but_22, but_23)
            product.add(but_31)
            return product

        def menu():
            glavmenu = types.InlineKeyboardMarkup(row_width=1)
            for i in Arrr.objects.all():
                but = types.InlineKeyboardButton(text=i.name, callback_data=i.unic)
                glavmenu.add(but)
            return glavmenu

        def startmenu():
            startmenu = types.ReplyKeyboardMarkup(True, False)
            startmenu.row('🍴 Меню', '🛍 Корзина')
            startmenu.row('📦 Заказы', '📢 Новости')
            startmenu.row('⚙️ Настройки', '❓ Помощь')
            return startmenu

        @bot.message_handler(commands=['start'])
        def startpg(message):
            p, _ = Users.objects.get_or_create(name=message.chat.id,
                                               defaults={'nickname': message.from_user.first_name})
            bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=startmenu())

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
                back.row('Имя', 'Моб.', 'Адрес')
                back.row('🏠 Начало')
                bot.send_message(message.chat.id, 'Ваши настройки:', reply_markup=back)
            elif message.text == '📦 Заказы':
                p = Users.objects.get(name=message.chat.id)
                count = p.orders_set.count()
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало')
                product = types.InlineKeyboardMarkup(row_width=3)
                if count > 0:
                    object_one = p.orders_set.all()[0]
                    if count == 1:
                        but_21 = types.InlineKeyboardButton(text='◀️', callback_data='empty')
                        but_22 = types.InlineKeyboardButton(text='1/{}'.format(count), callback_data='empty')
                        but_23 = types.InlineKeyboardButton(text='▶️', callback_data='empty')
                        product.add(but_21, but_22, but_23)
                    else:
                        arr_id = p.orders_set.values_list('id', flat=True)
                        but_21 = types.InlineKeyboardButton(text='◀️', callback_data=f'td|{arr_id[count - 1]}')
                        but_22 = types.InlineKeyboardButton(text='1/{}'.format(count), callback_data='empty')
                        but_23 = types.InlineKeyboardButton(text='▶️', callback_data=f'tn|{arr_id[1]}')
                        product.add(but_21, but_22, but_23)
                    bot.send_message(message.chat.id, text='Заказы:', reply_markup=back)
                    if object_one.type_delivery == '🚗 Привезти':
                        bot.send_message(message.chat.id, text=f'Дата: {object_one.data} \n'
                                                               f'Сумма: {object_one.amount_to_pay} ₽ \n'
                                                               f'Доставка: {object_one.type_delivery} '
                                                               f' {object_one.time_delivery} \n'
                                                               f'Адрес: {object_one.address_delivery}\n \n'
                                                               f'Блюда: \n{object_one.food}',
                                         reply_markup=product, parse_mode='markdown')
                    else:
                        bot.send_message(message.chat.id, text=f'Дата: {object_one.data} \n'
                                                               f'Сумма: {object_one.amount_to_pay} ₽ \n'
                                                               f'Доставка: {object_one.type_delivery} '
                                                               f' {object_one.time_delivery} \n \n'
                                                               f'Блюда: \n{object_one.food}',
                                         reply_markup=product, parse_mode='markdown')
                else:
                    bot.send_message(message.chat.id, text='Вы еще не заказывали')

            elif message.text == '🛍 Корзина' or message.text == '🛍':
                p = Users.objects.get(name=message.chat.id)
                arr = p.basket_set.count()
                if arr > 0:
                    tovar = p.basket_set.all()[0]
                    sum = tovar.count * tovar.price
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'), output_field=IntegerField()))
                    if arr > 1:
                        arr_id = p.basket_set.values_list('id', flat=True)
                        bot.send_message(message.chat.id,
                                         text=f'{tovar.name_product}[.]({tovar.photo})\n'
                                              f' {tovar.count}шт [*] {tovar.price} ₽ = {sum} ₽ ',
                                         reply_markup=newmenu(tovar.id, tovar.count, arr, nextt=arr_id[1],
                                                              down=arr_id[arr - 1], finite_sum=final_sum['sum']),
                                         parse_mode='markdown')
                    else:
                        bot.send_message(message.chat.id,
                                         text=f'{tovar.name_product}[.]({tovar.photo})\n'
                                              f' {tovar.count}шт [*] {tovar.price} ₽ = {sum} ₽ ',
                                         reply_markup=newmenu(tovar.id, tovar.count, arr,finite_sum=final_sum['sum']),
                                         parse_mode='markdown')
                else:

                    bot.send_message(message.chat.id,
                                     'В корзине пусто 😔\nПосмотрите /menu, там много интересного',
                                     reply_markup=startmenu())

            elif message.text == 'Имя':
                p = Users.objects.get(name=message.chat.id)
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало')
                new_name = bot.send_message(message.chat.id,
                                            'Ваше имя: {} \nНовое назначение:'.format(p.nickname),
                                            reply_markup=back)
                bot.register_next_step_handler(new_name, newName)

            elif message.text == 'Моб.':
                p = Users.objects.get(name=message.chat.id)
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало')
                if p.mobile is None:
                    new_number = bot.send_message(message.chat.id,
                                                  'Ваш мобильный телефон:',
                                                  reply_markup=back)
                    bot.register_next_step_handler(new_number, number_processing)
                else:
                    new_number = bot.send_message(message.chat.id,
                                                  'Ваш мобильный телефон:{}\n Новой номер:'.format(p.mobile),
                                                  reply_markup=back)
                    bot.register_next_step_handler(new_number, number_processing)

            elif message.text == 'Адрес':
                p = Users.objects.get(name=message.chat.id)
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало')
                if p.address is None:
                    new_address = bot.send_message(message.chat.id,
                                                   'Ваш адрес для доставок: не назначен',
                                                   reply_markup=back)
                    bot.register_next_step_handler(new_address, replacing_address)
                else:
                    new_address = bot.send_message(message.chat.id,
                                                   f'Ваш адрес для доставок: {p.address} \n Введите новый адрес:',
                                                   reply_markup=back)
                    bot.register_next_step_handler(new_address, replacing_address)

        def replacing_address(message):
            p = Users.objects.get(name=message.chat.id)
            if message.text == '🏠 Начало':
                startpg(message)
            elif message.text[0] == "/" or message.text.isdigit() or message.text.lower() == 'адрес':
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало')
                new_address = bot.send_message(chat_id=message.chat.id,
                                               text=f'Укажите корректно адрес доставки \n'
                                                    f' Улицу, дом, подъезд, квартиру и этаж:\n',
                                               reply_markup=back)
                bot.register_next_step_handler(new_address, replacing_address)
            else:
                p.address = message.text
                p.save()
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('Имя', 'Моб.', 'Адрес')
                back.row('🏠 Начало')
                bot.send_message(message.chat.id, 'Адрес успешно изменен')
                bot.send_message(message.chat.id, 'Выберите настройки,которые хотите поменять', reply_markup=back)


        def number_processing(message):
            if message.text == '🏠 Начало':
                startpg(message)
            elif message.text.isdigit() and len(message.text) == 11 and message.text[0] == '7':
                p = Users.objects.get(name=message.chat.id)
                p.mobile = message.text
                p.save()
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('Имя', 'Моб.', 'Адрес')
                back.row('🏠 Начало')
                bot.send_message(message.chat.id, 'Номер успешно изменен')
                bot.send_message(message.chat.id, 'Выберите настройки,которые хотите поменять', reply_markup=back)

            else:
                new_number = bot.send_message(message.chat.id, 'Введите корректное номер через 7')
                bot.register_next_step_handler(new_number, number_processing)

        def newName(message):
            if message.text == '🏠 Начало':
                startpg(message)
            elif message.text.isalpha():
                p = Users.objects.get(name=message.chat.id)
                p.nickname = message.text
                p.save()
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('Имя', 'Моб.', 'Адрес')
                back.row('🏠 Начало')
                bot.send_message(message.chat.id, 'Выберите настройки,которые хотите поменять', reply_markup=back)
            else:
                new_name = bot.send_message(message.chat.id,
                                            'Введите корректное имя')
                bot.register_next_step_handler(new_name, newName)

        @bot.callback_query_handler(func=lambda c: True)
        def inline(c):
            print(c.data)
            # Выводим категорию2
            p = Users.objects.get(name=c.message.chat.id)
            if Arrr.objects.filter(unic=c.data).exists():
                yaponmenu = types.InlineKeyboardMarkup()
                rr = Arrr.objects.get(unic=c.data)
                count = rr.category1_set.count()
                arr = rr.category1_set.all()
                if count % 2 == 0:
                    for i in range(0, count, 2):
                        but_1 = types.InlineKeyboardButton(text=arr[i].name, callback_data=arr[i].unicс)
                        but_2 = types.InlineKeyboardButton(text=arr[i + 1].name, callback_data=arr[i + 1].unicс)
                        yaponmenu.add(but_1, but_2)
                else:
                    but_0 = types.InlineKeyboardButton(text=arr[0].name, callback_data=arr[0].unicс)
                    yaponmenu.add(but_0)
                    for i in range(1, count, 2):
                        but_1 = types.InlineKeyboardButton(text=arr[i].name, callback_data=arr[i].unicс)
                        but_2 = types.InlineKeyboardButton(text=arr[i + 1].name, callback_data=arr[i + 1].unicс)
                        yaponmenu.add(but_1, but_2)
                but_nazad = types.InlineKeyboardButton(text='В начало меню', callback_data='vnachalo')
                yaponmenu.add(but_nazad)
                bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                              reply_markup=yaponmenu)
            elif c.data == 'empty':
                bot.answer_callback_query(c.id, text="")
            # выводим меню по ключу и добавляем статическием кнопки
            elif Category1.objects.filter(unicс=c.data).exists():
                rr = Category1.objects.get(unicс=c.data)
                gunkani1 = types.ReplyKeyboardMarkup(True, False)
                gunkani1.row('🏠', '🍴', '🛍')
                bot.send_message(c.message.chat.id, rr.name, reply_markup=gunkani1)
                bot.answer_callback_query(c.id, text="")
                for i in rr.meni_set.all():
                    gunkani11 = types.InlineKeyboardMarkup()
                    but_11 = types.InlineKeyboardButton(text='1шт-{}₽'.format(i.price),
                                                        callback_data=i.unic)
                    gunkani11.add(but_11)
                    bot.send_photo(c.message.chat.id, i.photo,
                                   caption="{}\n{}\nВес: {}г".format(i.name, i.structure, i.weight),
                                   reply_markup=gunkani11)

            # Обрабатываем нажатый товар ,добавляем его в корзину и добавляем инлай кнопку корзины

            elif Meni.objects.filter(unic=c.data).exists():
                if p.basket_set.filter(product_id=c.data).exists():
                    p.basket_set.filter(product_id=c.data).update(count=F('count') + 1)
                else:
                    obekt = Meni.objects.get(unic=c.data)
                    nama, _ = Basket.objects.get_or_create(
                        product_id=c.data, count=1, baskUser=p, name_product=obekt.name, photo=obekt.photo,
                        weight=obekt.weight, price=obekt.price)
                gunkani333 = types.InlineKeyboardMarkup()
                price = Meni.objects.get(unic=c.data).price
                but_11 = types.InlineKeyboardButton(text='{}₽({}шт.)'.format(price,
                                                                             p.basket_set.get(product_id=c.data).count),
                                                    callback_data=c.data)
                but_12 = types.InlineKeyboardButton(text='🛍 Корзина', callback_data="Korzina")
                gunkani333.add(but_11)
                gunkani333.add(but_12)
                bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                              reply_markup=gunkani333)
            elif c.data == 'Korzina':
                arr = p.basket_set.count()
                if arr > 0:
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'), output_field=IntegerField()))
                    tovar = p.basket_set.all()[0]
                    sum = tovar.count * tovar.price
                    if arr > 1:
                        arr_id = p.basket_set.values_list('id', flat=True)
                        bot.send_message(c.message.chat.id,
                                         text=f'{tovar.name_product}[.]({tovar.photo})\n'
                                              f' {tovar.count}шт [*] {tovar.price} ₽ = {sum} ₽ ',
                                         reply_markup=newmenu(tovar.id, tovar.count, arr, nextt=arr_id[1],
                                                              down=arr_id[arr - 1], finite_sum=final_sum['sum']),
                                         parse_mode='markdown')
                    else:
                        bot.send_message(c.message.chat.id, text=f'{tovar.name_product}[.]({tovar.photo})'
                                                                 f' {tovar.count}шт [*] {tovar.price} ₽ = {sum} ₽ ',
                                         reply_markup=newmenu(tovar.id, tovar.count, arr, finite_sum=final_sum['sum']),
                                         parse_mode='markdown')
                else:

                    bot.send_message(c.message.chat.id,
                                     'В корзине пусто 😔\nПосмотрите /menu, там много интересного',
                                     reply_markup=startmenu())

            elif c.data.split('|')[0] == 'deleting':
                try:
                    p.basket_set.get(id=c.data.split('|')[1]).delete()
                    arr = p.basket_set.count()
                    nextt = 0
                    down = 0
                    if arr > 0:
                        tovar = p.basket_set.all()[0]
                        sum = tovar.count * tovar.price
                        final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                           output_field=IntegerField()))
                        if arr > 1:
                            arr_id = p.basket_set.values_list('id', flat=True)
                            nextt = arr_id[1]
                            down = arr_id[arr - 1]
                        bot.edit_message_text(text=f'{tovar.name_product}[.]({tovar.photo})\n'
                                                   f' {tovar.count}шт [*] {tovar.price} ₽ = {sum} ₽ ',
                                              chat_id=c.message.chat.id, message_id=c.message.message_id,
                                              reply_markup=newmenu(tovar.id, tovar.count, arr,
                                                                   nextt, down, finite_sum=final_sum['sum']),
                                              parse_mode='markdown')
                    else:
                        bot.answer_callback_query(c.id, text="")
                        bot.clear_step_handler_by_chat_id(chat_id=c.message.chat.id)
                        bot.send_message(c.message.chat.id, 'В корзине пусто 😔\n'
                                                            'Посмотрите /menu, там много интересного',
                                         reply_markup=startmenu())
                except:
                    bot.answer_callback_query(c.id, text="")

            elif c.data.split('|')[0] == 'add':
                arr = p.basket_set.count()
                if arr == 0:
                    bot.answer_callback_query(c.id, text="")
                else:
                    p.basket_set.filter(id=c.data.split('|')[1]).update(count=F('count') + 1)
                    tovar = p.basket_set.get(id=c.data.split('|')[1])
                    sum = tovar.count * tovar.price
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                               output_field=IntegerField()))
                    bot.edit_message_text(chat_id=c.message.chat.id,message_id=c.message.message_id,
                                          text=f'{tovar.name_product}[.]({tovar.photo})\n'
                                               f' {tovar.count}шт [*] {tovar.price} ₽ = {sum} ₽ ',
                                          reply_markup=newmenu(tovar.id, tovar.count, arr,
                                                               int(c.data.split('|')[2]),
                                                               int(c.data.split('|')[3]),
                                                               int(c.data.split('|')[4]),
                                                               finite_sum=final_sum['sum']),
                                          parse_mode='markdown')

            elif c.data.split('|')[0] == 'r':
                try:
                    arr = p.basket_set.count()
                    tovar = p.basket_set.get(id=c.data.split('|')[1])
                    print(tovar.count)
                    product = types.InlineKeyboardMarkup(row_width=4)
                    but_11 = types.InlineKeyboardButton(text='❌', callback_data='deleting|{}'.format(tovar.id))
                    but_12 = types.InlineKeyboardButton(text='🔺',
                                                        callback_data='add|{0}|{1}|{2}|{3}'.format(tovar.id,
                                                                                                   int(c.data.split(
                                                                                                       '|')[
                                                                                                           2]),
                                                                                                   int(c.data.split(
                                                                                                       '|')[
                                                                                                           3]),
                                                                                                   int(c.data.split(
                                                                                                       '|')[
                                                                                                           4])))
                    if tovar.count == 1:
                        count = 1
                        but_13 = types.InlineKeyboardButton(text='{} шт.'.format(tovar.count), callback_data='empty')
                        but_14 = types.InlineKeyboardButton(text='🔻', callback_data='empty')

                    else:
                        p.basket_set.filter(id=c.data.split('|')[1]).update(count=F('count') - 1)
                        count = tovar.count - 1
                        but_13 = types.InlineKeyboardButton(text='{} шт.'.format(tovar.count - 1),
                                                            callback_data='empty')
                        but_14 = types.InlineKeyboardButton(text='🔻',
                                                            callback_data='r|{0}|{1}|{2}|{3}'.format(tovar.id,
                                                                                                     c.data.split('|')[
                                                                                                         2],
                                                                                                     c.data.split('|')[
                                                                                                         3],
                                                                                                     c.data.split('|')[
                                                                                                         4], ))
                    if int(c.data.split('|')[2]) == 0 and int(c.data.split('|')[3]) == 0:
                        but_21 = types.InlineKeyboardButton(text='◀️', callback_data='empty')
                        but_22 = types.InlineKeyboardButton(text='1/{}'.format(arr), callback_data='empty')
                        but_23 = types.InlineKeyboardButton(text='▶️', callback_data='empty')
                    else:
                        but_21 = types.InlineKeyboardButton(text='◀️',
                                                            callback_data='down|{}'.format(int(c.data.split('|')[3])))
                        but_22 = types.InlineKeyboardButton(text='{}/{}'.format(c.data.split('|')[4], arr),
                                                            callback_data='empty')
                        but_23 = types.InlineKeyboardButton(text='▶️',
                                                            callback_data='first|{}'.format(c.data.split('|')[2]))
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                               output_field=IntegerField()))
                    but_31 = types.InlineKeyboardButton(text=f'✅ Оформить заказ на {final_sum["sum"]} ₽',
                                                        callback_data='order_registration')
                    product.add(but_11, but_12, but_13, but_14)
                    product.add(but_21, but_22, but_23)
                    product.add(but_31)
                    sum = count * tovar.price
                    bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                          text=f'{tovar.name_product}[.]({tovar.photo})\n'
                                               f' {count}шт [*] {tovar.price} ₽ = {sum} ₽ ',
                                          reply_markup=product,
                                          parse_mode='markdown')
                except:
                    bot.answer_callback_query(c.id, text="")

            elif c.data.split('|')[0] == 'down':
                try:
                    tovar = p.basket_set.get(id=c.data.split('|')[1])
                    arr = p.basket_set.count()
                    arr_id = p.basket_set.values_list('id', flat=True)
                    sum = tovar.count * tovar.price
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'), output_field=IntegerField()))
                    if tovar.id == arr_id[0]:
                        nextt = arr_id[1]
                        str = 1
                        down = arr_id[arr - 1]

                    elif tovar.id == arr_id[arr - 1]:
                        nextt = arr_id[0]
                        str = arr
                        down = arr_id[arr - 2]

                    else:
                        for i in range(1, arr):
                            if tovar.id == arr_id[i]:
                                nextt = arr_id[i + 1]
                                str = i + 1
                                down = arr_id[i - 1]

                    bot.edit_message_text(text=f'{tovar.name_product}[.]({tovar.photo})\n'
                                               f' {tovar.count}шт [*] {tovar.price} ₽ = {sum} ₽ ',
                                          chat_id=c.message.chat.id, message_id=c.message.message_id,
                                          reply_markup=newmenu(tovar.id, tovar.count,
                                                               arr, nextt, down, str, finite_sum=final_sum['sum']),
                                          parse_mode='markdown')
                except:
                    bot.answer_callback_query(c.id, text="")
            elif c.data.split('|')[0] == 'first':
                try:
                    tovar = p.basket_set.get(id=c.data.split('|')[1])
                    arr = p.basket_set.count()
                    arr_id = p.basket_set.values_list('id', flat=True)
                    str = 1

                    sum = tovar.count * tovar.price
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                               output_field=IntegerField()))
                    if tovar.id == arr_id[arr - 1]:
                        str = arr
                        nextt = arr_id[0]
                        down = arr_id[arr - 2]

                    elif tovar.id == arr_id[0]:
                        nextt = arr_id[1]
                        down = arr_id[arr - 1]
                    else:
                        for i in range(0, arr):
                            if arr_id[i] == tovar.id:
                                nextt = arr_id[i + 1]
                                str = i + 1
                                down = arr_id[i - 1]
                    bot.edit_message_text(text=f'{tovar.name_product}[.]({tovar.photo})\n'
                                               f' {tovar.count}шт [*] {tovar.price} ₽ = {sum} ₽ ',
                                          chat_id=c.message.chat.id, message_id=c.message.message_id,
                                          reply_markup=newmenu(tovar.id, tovar.count,
                                                               arr, nextt=nextt, down=down,
                                                               str=str, finite_sum=final_sum['sum']),
                                          parse_mode='markdown')
                except:
                    bot.answer_callback_query(c.id, text="")
            elif c.data.split('|')[0] == 'tn' or c.data.split('|')[0] == 'td':
                try:
                    id_order = int(c.data.split('|')[1])
                    count = p.orders_set.count()
                    arr_id = p.orders_set.values_list('id', flat=True)
                    object_one = p.orders_set.get(id=id_order)
                    product = types.InlineKeyboardMarkup(row_width=3)
                    if id_order == arr_id[0]:
                        but_21 = types.InlineKeyboardButton(text='◀️', callback_data=f'td|{arr_id[count - 1]}')
                        but_22 = types.InlineKeyboardButton(text='1/{}'.format(count), callback_data='empty')
                        but_23 = types.InlineKeyboardButton(text='▶️', callback_data=f'tn|{arr_id[1]}')
                        product.add(but_21, but_22, but_23)
                    elif id_order == arr_id[count - 1]:
                        but_21 = types.InlineKeyboardButton(text='◀️', callback_data=f'td|{arr_id[count - 2]}')
                        but_22 = types.InlineKeyboardButton(text='{0}/{0}'.format(count), callback_data='empty')
                        but_23 = types.InlineKeyboardButton(text='▶️', callback_data=f'tn|{arr_id[0]}')
                        product.add(but_21, but_22, but_23)
                    else:
                        for i in range(1, count):
                            if id_order == arr_id[i]:
                                but_21 = types.InlineKeyboardButton(text='◀️', callback_data=f'td|{arr_id[i - 1]}')
                                but_22 = types.InlineKeyboardButton(text='{}/{}'.format(i + 1, count),
                                                                    callback_data='empty')
                                but_23 = types.InlineKeyboardButton(text='▶️', callback_data=f'tn|{arr_id[i + 1]}')
                                product.add(but_21, but_22, but_23)
                    bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                          text=f'Дата: {object_one.data} \n'
                                               f'Сумма: {object_one.amount_to_pay} ₽ \n'
                                               f'Доставка: {object_one.type_delivery} '
                                               f' {object_one.time_delivery} \n'
                                               f'Адрес: {object_one.address_delivery}\n \n'
                                               f'Блюда: \n{object_one.food}',
                                          reply_markup=product, parse_mode='markdown')
                except:
                    print('lol')
                    bot.answer_callback_query(c.id, text="")

            elif c.data == 'order_registration':
                if p.basket_set.count() == 0:
                    bot.answer_callback_query(c.id, text="")
                else:
                    bot.clear_step_handler_by_chat_id(chat_id=c.message.chat.id)
                    bot.answer_callback_query(c.id)
                    back = types.ReplyKeyboardMarkup(True, False)
                    back.row('✅ Верно')
                    back.row('🏃 Заберу сам', '🚗 Привезти')
                    back.row('🏠 Начало')
                    type_delivery = bot.send_message(c.message.chat.id,
                                                     f'Укажите вариант доставки \n На данный момент: {p.delivery}',
                                                     reply_markup=back)
                    bot.register_next_step_handler(type_delivery, choice_of_delivery)

            # В начало
            elif c.data == 'vnachalo':
                bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                              reply_markup=menu())

        def choice_of_delivery(message):
            if message.text == '🏠 Начало':
                startpg(message)
            elif message.text == '✅ Верно':
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('🏠 Начало', '⬅️ Назад')
                p = Users.objects.get(name=message.chat.id)
                bot.send_message(chat_id=message.chat.id, text=f'{p.delivery} \n Стоимость - 0 ₽')
                time_delivery = bot.send_message(chat_id=message.chat.id,
                                                 text=f'Укажите время доставки:\n Сейчас: {p.time_delivery}',
                                                 reply_markup=back)
                bot.register_next_step_handler(time_delivery, processing_delivery)
            elif message.text == '🏃 Заберу сам' or message.text == '🚗 Привезти':
                p = Users.objects.get(name=message.chat.id)
                p.delivery = message.text
                p.save()
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('🏠 Начало', '⬅️ Назад')
                bot.send_message(chat_id=message.chat.id, text=f'{message.text} \n Стоимость - 0 ₽')
                time_delivery = bot.send_message(chat_id=message.chat.id,
                                                 text='Укажите время доставки в формате(12:30)\n'
                                                      ' Сейчас: как можно скорее',
                                                 reply_markup=back)
                bot.register_next_step_handler(time_delivery, processing_delivery)
            else:
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('🏃 Заберу сам', '🚗 Привезти')
                back.row('🏠 Начало')
                type_delivery = bot.send_message(chat_id=message.chat.id,
                                                 text='Выберите один из предложенных вариантов',
                                                 reply_markup=back)
                bot.register_next_step_handler(type_delivery, choice_of_delivery)

        def processing_delivery(message):
            p = Users.objects.get(name=message.chat.id)
            if message.text == '✅ Верно':
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('🏠 Начало', '⬅️ Назад')
                new_name = bot.send_message(chat_id=message.chat.id,
                                            text=f'Укажите ваше имя:\n Сейчас:{p.nickname}',
                                            reply_markup=back)
                bot.register_next_step_handler(new_name, name_processing)

            elif message.text == '⬅️ Назад':
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('🏃 Заберу сам', '🚗 Привезти')
                back.row('🏠 Начало')
                type_delivery = bot.send_message(message.chat.id,
                                                 f'Укажите вариант доставки \n На данный момент: {p.delivery}',
                                                 reply_markup=back)
                bot.register_next_step_handler(type_delivery, choice_of_delivery)

            elif message.text == '🏠 Начало':
                startpg(message)

            else:
                new_time = re.match(r'\d\d:\d\d', message.text)
                if new_time is None:
                    time_delivery = bot.send_message(chat_id=message.chat.id,
                                                     text=f'Введите корректно время в формате(14:30)\n'
                                                          f' Сейчас:{p.delivery}')
                    bot.register_next_step_handler(time_delivery, processing_delivery)
                else:
                    p.time_delivery = new_time.group(0)
                    p.save()
                    back = types.ReplyKeyboardMarkup(True, False)
                    back.row('✅ Верно')
                    back.row('🏠 Начало', '⬅️ Назад')
                    new_name = bot.send_message(chat_id=message.chat.id,
                                                text=f'Укажите ваше имя:\n Сейчас:{p.nickname}',
                                                reply_markup=back)
                    bot.register_next_step_handler(new_name, name_processing)

        def name_processing(message):
            p = Users.objects.get(name=message.chat.id)
            if message.text == '✅ Верно':
                back = types.ReplyKeyboardMarkup(True, False)
                if p.mobile is None:
                    back.row('🏠 Начало', '⬅️ Назад')
                    new_number = bot.send_message(chat_id=message.chat.id,
                                                  text=f'Укажите ваш мобильный телефон:\n Сейчас:не указан',
                                                  reply_markup=back)
                    bot.register_next_step_handler(new_number, phone_number)
                else:
                    back.row('✅ Верно')
                    back.row('🏠 Начало', '⬅️ Назад')
                    new_number = bot.send_message(chat_id=message.chat.id,
                                                  text=f'Укажите ваш мобильный телефон:\n Сейчас:{p.mobile}',
                                                  reply_markup=back)
                    bot.register_next_step_handler(new_number, phone_number)
            elif message.text == '⬅️ Назад':
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('🏠 Начало', '⬅️ Назад')
                time_delivery = bot.send_message(chat_id=message.chat.id,
                                                 text=f'Укажите время доставки в формате(12:30)\n'
                                                      f' Сейчас: {p.time_delivery}',
                                                 reply_markup=back)
                bot.register_next_step_handler(time_delivery, processing_delivery)
            elif message.text == '🏠 Начало':
                startpg(message)
            elif message.text.isalpha():
                p.nickname = message.text
                p.save()
                back = types.ReplyKeyboardMarkup(True, False)
                if p.mobile is not None:
                    back.row('✅ Верно')
                    back.row('🏠 Начало', '⬅️ Назад')
                    new_number = bot.send_message(chat_id=message.chat.id,
                                                  text=f'Укажите ваш мобильный телефон:\n Сейчас:{p.mobile}',
                                                  reply_markup=back)
                    bot.register_next_step_handler(new_number, phone_number)
                else:
                    back.row('🏠 Начало', '⬅️ Назад')
                    new_number = bot.send_message(chat_id=message.chat.id,
                                                  text=f'Укажите ваш мобильный телефон:\n Сейчас:не указан',
                                                  reply_markup=back)
                    bot.register_next_step_handler(new_number, phone_number)
            else:
                new_name = bot.send_message(message.chat.id,
                                            'Введите корректное имя')
                bot.register_next_step_handler(new_name, name_processing)

        def phone_number(message):
            p = Users.objects.get(name=message.chat.id)
            if message.text == '✅ Верно':
                if p.delivery == '🚗 Привезти':  # сделать для заберу сам
                    back = types.ReplyKeyboardMarkup(True, False)
                    if p.address == "" or p.address is None:
                        back.row('🏠 Начало', '⬅️ Назад')
                        new_address = bot.send_message(chat_id=message.chat.id,
                                                       text=f'Укажите адрес доставки \n'
                                                            f' Улицу, дом, подъезд, квартиру и этаж:\n'
                                                            f' Сейчас:не указан',
                                                       reply_markup=back)
                    else:
                        back.row('✅ Верно')
                        back.row('🏠 Начало', '⬅️ Назад')
                        new_address = bot.send_message(chat_id=message.chat.id,
                                                       text=f'Укажите адрес доставки \n'
                                                            f' Улицу, дом, подъезд, квартиру и этаж:\n'
                                                            f' Сейчас:{p.address}',
                                                       reply_markup=back)
                    bot.register_next_step_handler(new_address, address_processing)
                else:
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                               output_field=IntegerField()))
                    back = types.ReplyKeyboardMarkup(True, False)
                    back.row('✅ Подтвердить и отправить')
                    back.row('🏠 Начало', '⬅️ Назад')
                    ordering = bot.send_message(message.chat.id, f' *Данные заказа*: \nСумма заказа: {final_sum["sum"]} \n'
                                                                 f'Покупатель: {p.nickname} \nТелефон: {p.mobile} \n'
                                                                 f'Доставка: {p.delivery}',
                                                reply_markup=back,parse_mode='markdown')
                    bot.register_next_step_handler(ordering, ordering_process)

            elif message.text == '⬅️ Назад':
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('🏠 Начало', '⬅️ Назад')
                new_name = bot.send_message(chat_id=message.chat.id,
                                            text=f'Укажите ваше имя:\n Сейчас:{p.nickname}',
                                            reply_markup=back)
                bot.register_next_step_handler(new_name, name_processing)

            elif message.text == '🏠 Начало':
                startpg(message)

            elif message.text.isdigit() and len(message.text) == 11 and message.text[0] == '7':
                p.mobile = message.text
                p.save()
                back = types.ReplyKeyboardMarkup(True, False)
                if p.delivery == '🚗 Привезти':
                    if p.address == '' or p.address is None:
                        back.row('🏠 Начало', '⬅️ Назад')
                        new_address = bot.send_message(chat_id=message.chat.id,
                                                       text=f'Укажите адрес доставки \n'
                                                            f'Улицу, дом, подъезд, квартиру и этаж:\n'
                                                            f'Сейчас:не указан',
                                                       reply_markup=back)
                    else:
                        back.row('✅ Верно')
                        back.row('🏠 Начало', '⬅️ Назад')
                        new_address = bot.send_message(chat_id=message.chat.id,
                                                       text=f'Укажите адрес доставки \n'
                                                            f' Улицу, дом, подъезд, квартиру и этаж:\n'
                                                            f' Сейчас:{p.address}',
                                                       reply_markup=back)

                    bot.register_next_step_handler(new_address, address_processing)
                else:
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                               output_field=IntegerField()))
                    back = types.ReplyKeyboardMarkup(True, False)
                    back.row('✅ Подтвердить и отправить')
                    back.row('🏠 Начало', '⬅️ Назад')
                    ordering = bot.send_message(message.chat.id, f'*Данные заказа:* \nСумма заказа: {final_sum["sum"]}₽\n'
                                                                 f'Покупатель: {p.nickname} \nТелефон: {p.mobile} \n'
                                                                 f'Доставка: {p.delivery}',
                                                reply_markup=back, parse_mode='markdown')
                    bot.register_next_step_handler(ordering, ordering_process)

            else:
                new_number = bot.send_message(message.chat.id, 'Введите корректное номер через 7')
                bot.register_next_step_handler(new_number, phone_number)

        def address_processing(message):
            p = Users.objects.get(name=message.chat.id)
            if message.text == '✅ Верно':
                final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                           output_field=IntegerField()))
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Подтвердить и отправить')
                back.row('🏠 Начало', '⬅️ Назад')
                ordering = bot.send_message(message.chat.id, f'*Данные заказа:* \nСумма заказа: {final_sum["sum"]}₽\n'
                                                             f'Покупатель: {p.nickname} \nТелефон: {p.mobile} \n'
                                                             f'Доставка: {p.delivery} \nАдрес: {p.address} \n',
                                            reply_markup=back, parse_mode='markdown')
                bot.register_next_step_handler(ordering, ordering_process)
            elif message.text == '⬅️ Назад':
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('🏠 Начало', '⬅️ Назад')
                new_number = bot.send_message(chat_id=message.chat.id,
                                              text=f'Укажите ваш мобильный телефон:\n Сейчас:{p.mobile}',
                                              reply_markup=back)
                bot.register_next_step_handler(new_number, phone_number)

            elif message.text == '🏠 Начало':
                startpg(message)
            elif message.text[0] == "\'" or message.text.isdigit():
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('🏠 Начало', '⬅️ Назад')
                new_address = bot.send_message(chat_id=message.chat.id,
                                               text=f'Укажите корректно адрес доставки \n'
                                                    f' Улицу, дом, подъезд, квартиру и этаж:\n'
                                                    f' Сейчас:{p.address}',
                                               reply_markup=back)

                bot.register_next_step_handler(new_address, address_processing)
            else:
                final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                           output_field=IntegerField()))
                p.address = message.text
                p.save()
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Подтвердить и отправить')
                back.row('🏠 Начало', '⬅️ Назад')
                bot.send_message(message.chat.id, f'*Данные заказа:* \nСумма заказа: {final_sum["sum"]}₽ \n'
                                                  f'Покупатель: {p.nickname} \nТелефон: {p.mobile} \n'
                                                  f'Доставка: {p.delivery} \nАдрес: {p.address} \n',
                                 reply_markup=back, parse_mode='markdown' )

        def ordering_process(message):
            p = Users.objects.get(name=message.chat.id)
            if message.text == '✅ Подтвердить и отправить':
                basket = p.basket_set.all()
                final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                           output_field=IntegerField()))
                foods = ''
                for i in basket:
                    sum_food = i.count * i.price
                    foods += '{} - {}шт. = {} ₽ \n'.format(i.name_product, i.count, sum_food)
                    print(foods)
                p.orders_set.create(amount_to_pay=final_sum['sum'], type_delivery=p.delivery,
                                    address_delivery=p.address, food=foods, time_delivery=p.time_delivery)
                p.basket_set.all().delete()
                bot.send_message(message.chat.id, 'Главное меню', reply_markup=startmenu())
            elif message.text == '⬅️ Назад':
                if p.delivery == '🚗 Привезти':
                    back = types.ReplyKeyboardMarkup(True, False)
                    back.row('✅ Верно')
                    back.row('🏠 Начало', '⬅️ Назад')
                    new_address = bot.send_message(chat_id=message.chat.id,
                                                   text=f'Укажите адрес доставки \n'
                                                        f' Улицу, дом, подъезд, квартиру и этаж:\n'
                                                        f' Сейчас:{p.address}',
                                                   reply_markup=back)
                    bot.register_next_step_handler(new_address, address_processing)
                else:
                    back = types.ReplyKeyboardMarkup(True, False)
                    back.row('✅ Верно')
                    back.row('🏠 Начало', '⬅️ Назад')
                    new_number = bot.send_message(chat_id=message.chat.id,
                                                  text=f'Укажите ваш мобильный телефон:\n Сейчас:{p.mobile}',
                                                  reply_markup=back)
                    bot.register_next_step_handler(new_number, phone_number)

            elif message.text == '🏠 Начало':
                startpg(message)

            else:
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Подтвердить и отправить')
                back.row('🏠 Начало', '⬅️ Назад')
                error = bot.send_message(chat_id=message.chat.id,
                                         text='Выбирите одну из кнопок для дальнейшего действия',
                                         reply_markup=back)
                bot.register_next_step_handler(error, ordering_process)

        bot.polling()
