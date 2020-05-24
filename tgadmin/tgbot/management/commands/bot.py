from django.core.management.base import BaseCommand
import telebot
from telebot import types
from telebot import apihelper
from django.db.models import F, IntegerField
import re
from django.db.models import Sum
from tgbot.models import CategoryOne, CategoryTwo, AllMenu, Users, Basket, Configuration
from tgadmin.settings import BOT
from tgbot.keyboard import start_menu, basket_menu, submenu, keyboard_number, menu, keyboard_down, keyboard_of_menu, menu_two, update_object_menu,keyboard_setting,keyboard_time
from tgbot.keyboard import keyboard_sum, keyboard_delivery, keyboard_no_mobile, keyboard_back, keyboard_confirm, keyboard_help,keyboard_admin, keyboard_back_admin


class Command(BaseCommand):
    help = "ТЕлеграмм бот"

    def handle(self, *args, **options):
        bot = telebot.TeleBot(BOT)
        apihelper.proxy = {'https': 'socks5h://PrhZ8F:eebLU48kCY@188.130.129.144:5501'}

        def category_one_or_two(category, c):
            bot.send_message(c.message.chat.id, category.name, reply_markup=keyboard_of_menu())
            bot.answer_callback_query(c.id, text="")
            for i in category.allmenu_set.all():
                menu_category = types.InlineKeyboardMarkup()
                if i.volume is None and i.weight is None:
                    menu_category.add(types.InlineKeyboardButton(text='1шт - {} ₽'.format(i.price),
                                                                 callback_data=f'm3|{i.id}'))
                    text = "*{}*\n{}".format(i.name, i.structure, i.weight)
                elif i.volume is None:
                    menu_category.add(types.InlineKeyboardButton(text='1шт - {} ₽'.format(i.price),
                                                                 callback_data=f'm3|{i.id}'))
                    text = "*{}*\n{}\nВес: {}г".format(i.name, i.structure, i.weight)
                elif i.weight is None:
                    menu_category.add(types.InlineKeyboardButton(text='{}шт - {} ₽'.format(i.volume, i.price),
                                                                 callback_data=f'm3|{i.id}'))
                    text = "*{}*\n{}\nОбъем: {}шт.".format(i.name, i.structure, i.volume)
                else:
                    menu_category.add(types.InlineKeyboardButton(text='{}шт - {} ₽'.format(i.volume, i.price),
                                                                 callback_data=f'm3|{i.id}'))
                    text = "*{}*\n{}\nОбъем: {}шт.\nВес: {}г".format(i.name, i.structure, i.volume, i.weight)

                bot.send_photo(c.message.chat.id, i.photo, caption=text, reply_markup=menu_category,
                               parse_mode='markdown')

        def preparing_the_bucket(user, chat_id):
            arr = user.basket_set.count()
            if arr > 0:
                object_menu = user.basket_set.all()[0]
                menu_sum = object_menu.count * object_menu.price
                final_sum = user.basket_set.aggregate(sum=Sum(F('count') * F('price'), output_field=IntegerField()))
                if arr > 1:
                    arr_id = user.basket_set.values_list('id', flat=True)
                    bot.send_message(chat_id, text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                                   f'{object_menu.count}шт [*] {object_menu.price} ₽ = {menu_sum} ₽ ',
                                     reply_markup=basket_menu(object_menu.id, object_menu.count, arr, forward=arr_id[1],
                                                              down=arr_id[arr - 1], finite_sum=final_sum['sum']),
                                     parse_mode='markdown')
                else:
                    bot.send_message(chat_id, text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                                   f' {object_menu.count}шт [*] {object_menu.price} ₽ = {menu_sum} ₽ ',
                                     reply_markup=basket_menu(object_menu.id, object_menu.count, arr,
                                                              finite_sum=final_sum['sum']),
                                     parse_mode='markdown')
            else:

                bot.send_message(chat_id,
                                 'В корзине пусто 😔\nПосмотрите /menu, там много интересного',
                                 reply_markup=start_menu())

        def withdrawal_of_orders(user, chat_id):
            count = user.orders_set.count()
            back = types.ReplyKeyboardMarkup(True, False)
            back.row('🏠 Начало')
            product = types.InlineKeyboardMarkup(row_width=3)
            if count > 0:
                object_one = user.orders_set.all()[0]
                if count == 1:
                    but_21 = types.InlineKeyboardButton(text='◀️', callback_data='empty')
                    but_22 = types.InlineKeyboardButton(text='1/{}'.format(count), callback_data='empty')
                    but_23 = types.InlineKeyboardButton(text='▶️', callback_data='empty')
                    product.add(but_21, but_22, but_23)
                else:
                    arr_id = user.orders_set.values_list('id', flat=True)
                    but_21 = types.InlineKeyboardButton(text='◀️', callback_data=f'td|{arr_id[count - 1]}')
                    but_22 = types.InlineKeyboardButton(text='1/{}'.format(count), callback_data='empty')
                    but_23 = types.InlineKeyboardButton(text='▶️', callback_data=f'tn|{arr_id[1]}')
                    product.add(but_21, but_22, but_23)
                bot.send_message(chat_id, text='Заказы:', reply_markup=back)
                date_time = object_one.data.strftime("%d-%m-%Y %H:%M")
                if object_one.type_delivery == '🚗 Привезти':
                    bot.send_message(chat_id, text=f'Дата: {date_time}\n'
                                                   f'Сумма: {object_one.amount_to_pay} ₽\n'
                                                   f'Доставка: {object_one.type_delivery} '
                                                   f' {object_one.time_delivery}\n'
                                                   f'Адрес: {object_one.address_delivery}\n\n'
                                                   f'Блюда:\n{object_one.food}',
                                     reply_markup=product, parse_mode='markdown')
                else:
                    bot.send_message(chat_id, text=f'Дата: {date_time}\n'
                                                   f'Сумма: {object_one.amount_to_pay} ₽\n'
                                                   f'Доставка: {object_one.type_delivery} '
                                                   f' {object_one.time_delivery}\n\n'
                                                   f'Блюда:\n{object_one.food}',
                                     reply_markup=product, parse_mode='markdown')
            else:
                bot.send_message(chat_id, text='Вы еще не заказывали')

        @bot.message_handler(commands=['start'])
        def startpg(message):
            user, _ = Users.objects.get_or_create(name=message.chat.id,
                                                  defaults={'nickname': message.from_user.first_name})
            user.status = '1'
            user.save(update_fields=["status"])
            bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=start_menu())

        @bot.message_handler(commands=['cart'])
        def commands_cart(message):
            user = Users.objects.get(name=message.chat.id)
            user.status = '1'
            user.save(update_fields=["status"])
            preparing_the_bucket(user, message.chat.id)

        @bot.message_handler(commands=['menu'])
        def commands_menu(message):
            Users.objects.filter(name=message.chat.id).update(status='1')
            bot.send_message(message.chat.id, 'Меню', reply_markup=keyboard_down())
            bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд:', reply_markup=menu())

        @bot.message_handler(commands=['history'])
        def commands_history(message):
            user = Users.objects.get(name=message.chat.id)
            user.status = '1'
            user.save(update_fields=["status"])
            withdrawal_of_orders(user, message.chat.id)

        @bot.message_handler(commands=['settings'])
        def commands_settings(message):
            Users.objects.filter(name=message.chat.id).update(status='1')
            bot.send_message(message.chat.id, 'Ваши настройки:', reply_markup=keyboard_setting())

        @bot.message_handler(commands=['news'])
        def commands_news(message):
            Users.objects.filter(name=message.chat.id).update(status='1')
            news = Configuration.objects.get(id=1).news.split('|')
            len_news = len(news)
            if len_news == 1:
                bot.send_message(message.chat.id, text=news, parse_mode='markdown', reply_markup=keyboard_down())
            elif len_news == 2:
                bot.send_photo(message.chat.id, photo=news[1], parse_mode='markdown', reply_markup=keyboard_down())
            else:
                bot.send_photo(message.chat.id, photo=news[1], caption=news[2], parse_mode='markdown',
                               reply_markup=keyboard_down())

        @bot.message_handler(commands=['admin_news'])
        def update_news(message):
            if Users.objects.get(id=1).name == int(message.chat.id):
                Users.objects.filter(id=1).update(status='a')
                bot.send_message(message.chat.id, 'Админ панель новостей', reply_markup=keyboard_admin())

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '2')
        def choice_of_delivery(message):
            user = Users.objects.get(name=message.chat.id)
            min_sum = Configuration.objects.get(id=1).min_sum
            if message.text == '🏠 Начало':
                startpg(message)
            elif message.text == '⬅️ Назад':
                user.status = '1'
                user.save(update_fields=["status"])
                bot.send_message(chat_id=message.chat.id, text='Главное меню', reply_markup=start_menu())
                preparing_the_bucket(user, message.chat.id)
            elif min_sum > user.basket_sum:
                user.status = '1'
                user.save(update_fields=["status"])
                bot.send_message(chat_id=message.chat.id, text=f'Минимальная сумма заказа {min_sum} ₽. '
                                 f'Закажите ещё что-нибудь /menu  ', reply_markup=keyboard_sum())
            elif message.text == '✅ Верно':
                user.status = '6'
                user.save(update_fields=["status"])
                bot.send_message(chat_id=message.chat.id, text=f'{user.delivery}\nСтоимость - 0 ₽')
                if user.delivery == '🏃 Заберу сам':
                    text_message = f'Укажите к какому времени приготовить заказ:\nСейчас: {user.time_delivery}'
                else:
                    text_message = f'Укажите время доставки:\nСейчас: {user.time_delivery}'
                bot.send_message(chat_id=message.chat.id, text=text_message, reply_markup=keyboard_time())
            elif message.text == '🏃 Заберу сам' or message.text == '🚗 Привезти':
                user.delivery = message.text
                user.status = '6'
                user.save(update_fields=["delivery", "status"])
                bot.send_message(chat_id=message.chat.id, text=f'{message.text}\nСтоимость - 0 ₽')
                if message.text == '🏃 Заберу сам':
                    text_message = f'Укажите к какому времени приготовить заказ:\nСейчас: {user.time_delivery}'
                else:
                    text_message = f'Укажите время доставки:\nСейчас: {user.time_delivery}'
                bot.send_message(chat_id=message.chat.id, text=text_message, reply_markup=keyboard_time())
            else:
                bot.send_message(chat_id=message.chat.id, text='Выберите один из предложенных вариантов')

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '6')
        def processing_delivery(message):
            user = Users.objects.get(name=message.chat.id)
            min_sum = Configuration.objects.get(id=1).min_sum
            if min_sum > user.basket_sum:
                user.status = '1'
                user.save(update_fields=["status"])
                bot.send_message(chat_id=message.chat.id, text=f'Минимальная сумма заказа {min_sum} ₽. '
                                 f'Закажите ещё что-нибудь /menu  ', reply_markup=keyboard_sum())
            elif message.text == '✅ Верно':
                user.status = '7'
                user.save(update_fields=["status"])
                bot.send_message(chat_id=message.chat.id, text=f'Укажите ваше имя:\nСейчас:{user.nickname}',
                                 reply_markup=submenu())
            elif message.text == '⬅️ Назад':
                user.status = '2'
                user.save(update_fields=["status"])
                bot.send_message(message.chat.id, f'Укажите вариант доставки\nНа данный момент: {user.delivery}',
                                 reply_markup=keyboard_delivery())
            elif message.text == '🏠 Начало':
                startpg(message)
            elif message.text == 'Как можно скорее':
                user.time_delivery = 'Как можно скорее'
                user.status = '7'
                user.save(update_fields=["time_delivery", "status"])
                bot.send_message(chat_id=message.chat.id, text=f'Укажите ваше имя:\nСейчас:{user.nickname}',
                                 reply_markup=submenu())
            else:
                new_time = re.match(r'(2[0-3]|[0-1]\d):[0-5]\d', message.text)
                if new_time is None:
                    bot.send_message(chat_id=message.chat.id, text=f'Введите корректно время в формате(14:30)\n'
                                                                   f'Сейчас:{user.delivery}')
                else:
                    user.time_delivery = new_time.group(0)
                    user.status = '7'
                    user.save(update_fields=["time_delivery", "status"])
                    bot.send_message(chat_id=message.chat.id, text=f'Укажите ваше имя:\nСейчас:{user.nickname}',
                                     reply_markup=submenu())

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '7')
        def name_processing(message):
            user = Users.objects.get(name=message.chat.id)
            min_sum = Configuration.objects.get(id=1).min_sum
            if min_sum > user.basket_sum:
                user.status = '1'
                user.save(update_fields=["status"])
                bot.send_message(chat_id=message.chat.id, text=f'Минимальная сумма заказа {min_sum} ₽. '
                                                               f'Закажите ещё что-нибудь /menu  ',
                                 reply_markup=keyboard_sum())
            elif message.text == '✅ Верно':
                user.status = '8'
                user.save(update_fields=["status"])
                if user.mobile is None:
                    text = f'Укажите ваш мобильный телефон:\nСейчас:не указан'
                    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard_no_mobile())
                else:
                    text = f'Укажите ваш мобильный телефон:\nСейчас:{user.mobile}'
                bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard_number())
            elif message.text == '⬅️ Назад':
                user.status = '6'
                user.save(update_fields=["status"])
                bot.send_message(chat_id=message.chat.id, text=f'Укажите время доставки в формате(12:30)\n'
                                                               f'Сейчас: {user.time_delivery}',
                                 reply_markup=keyboard_time())
            elif message.text == '🏠 Начало':
                startpg(message)
            elif message.text.isalpha() and len(message.text) < 30:
                user.nickname = message.text
                user.status = '8'
                user.save(update_fields=["nickname", "status"])
                if user.mobile is not None:
                    bot.send_message(chat_id=message.chat.id,
                                     text=f'Укажите ваш мобильный телефон:\nСейчас:{user.mobile}',
                                     reply_markup=keyboard_number())
                else:
                    bot.send_message(chat_id=message.chat.id,
                                     text=f'Укажите ваш мобильный телефон:\nСейчас:не указан',
                                     reply_markup=keyboard_no_mobile())
            else:
                bot.send_message(message.chat.id, 'Введите корректное имя')

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '8')
        def phone_number(message):
            user = Users.objects.get(name=message.chat.id)
            min_sum = Configuration.objects.get(id=1).min_sum
            if min_sum > user.basket_sum:
                user.status = '1'
                user.save(update_fields=["status"])
                bot.send_message(chat_id=message.chat.id, text=f'Минимальная сумма заказа {min_sum} ₽. '
                                                               f'Закажите ещё что-нибудь /menu  ',
                                 reply_markup=keyboard_sum())
            elif message.text == '✅ Верно':
                if user.delivery == '🚗 Привезти':
                    user.status = '9'
                    user.save(update_fields=["status"])
                    if user.address == "" or user.address is None:
                        bot.send_message(chat_id=message.chat.id, text=f'Укажите адрес доставки \n'
                                                                       f'Улицу, дом, подъезд, квартиру и этаж:\n'
                                                                       f'Сейчас:не указан',
                                         reply_markup=keyboard_back())
                    else:
                        bot.send_message(chat_id=message.chat.id, text=f'Укажите адрес доставки \n'
                                                                       f' Улицу, дом, подъезд, квартиру и этаж:\n'
                                                                       f' Сейчас:{user.address}',
                                         reply_markup=submenu())
                else:
                    user.status = 'q'
                    user.save(update_fields=["status"])
                    bot.send_message(message.chat.id, f'*Данные заказа*:\nСумма заказа: {user.basket_sum} ₽\n'
                                                      f'Покупатель: {user.nickname}\nТелефон: {user.mobile}\n'
                                                      f'Доставка: {user.delivery}',
                                     reply_markup=keyboard_confirm(), parse_mode='markdown')
            elif message.text == '⬅️ Назад':
                user.status = '7'
                user.save(update_fields=["status"])
                bot.send_message(chat_id=message.chat.id, text=f'Укажите ваше имя:\nСейчас:{user.nickname}',
                                 reply_markup=submenu())
            elif message.text == '🏠 Начало':
                startpg(message)
            elif message.contact is not None:
                user.mobile = message.contact.phone_number
                if user.delivery == '🚗 Привезти':
                    user.status = '9'
                    user.save(update_fields=["status"])
                    if user.address == '' or user.address is None:
                        bot.send_message(chat_id=message.chat.id, text=f'Укажите адрес доставки \n'
                                                                       f'Улицу, дом, подъезд, квартиру и этаж:\n'
                                                                       f'Сейчас:не указан',
                                         reply_markup=keyboard_sum())
                    else:
                        bot.send_message(chat_id=message.chat.id, text=f'Укажите адрес доставки\n'
                                                                       f'Улицу, дом, подъезд, квартиру и этаж:\n'
                                                                       f'Сейчас:{user.address}',
                                         reply_markup=submenu())
                else:
                    user.status = 'q'
                    user.save(update_fields=["status"])
                    bot.send_message(message.chat.id, f'*Данные заказа:*\nСумма заказа: {user.basket_sum}₽\n'
                                                      f'Покупатель: {user.nickname}\nТелефон: {user.mobile} \n'
                                                      f'Доставка: {user.delivery}',
                                     reply_markup=keyboard_confirm(), parse_mode='markdown')
            elif message.text[1:].isdigit() and len(message.text) == 12 and message.text[:2] == '+7':
                user.mobile = message.text
                user.save(update_fields=["mobile"])
                if user.delivery == '🚗 Привезти':
                    user.status = '9'
                    user.save(update_fields=["status"])
                    if user.address == '' or user.address is None:
                        bot.send_message(chat_id=message.chat.id, text=f'Укажите адрес доставки\n'
                                                                       f'Улицу, дом, подъезд, квартиру и этаж:\n'
                                                                       f'Сейчас:не указан',
                                         reply_markup=keyboard_back())
                    else:
                        bot.send_message(chat_id=message.chat.id, text=f'Укажите адрес доставки\n'
                                                                       f' Улицу, дом, подъезд, квартиру и этаж:\n'
                                                                       f' Сейчас:{user.address}',
                                         reply_markup=submenu())
                else:
                    user.status = 'q'
                    user.save(update_fields=["status"])
                    bot.send_message(message.chat.id, f'*Данные заказа:*\n'
                                                      f'Сумма заказа: {user.basket_sum}₽\n'
                                                      f'Покупатель: {user.nickname}\nТелефон: {user.mobile}\n'
                                                      f'Доставка: {user.delivery}',
                                     reply_markup=keyboard_confirm(), parse_mode='markdown')

            else:
                bot.send_message(message.chat.id, 'Введите корректно номер через +7')

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '9')
        def address_processing(message):
            user = Users.objects.get(name=message.chat.id)
            min_sum = Configuration.objects.get(id=1).min_sum
            if min_sum > user.basket_sum:
                user.status = '1'
                user.save(update_fields=["status"])
                bot.send_message(chat_id=message.chat.id, text=f'Минимальная сумма заказа {min_sum} ₽. '
                                                               f'Закажите ещё что-нибудь /menu  ',
                                 reply_markup=keyboard_back())
            elif message.text == '✅ Верно':
                user.status = 'q'
                user.save(update_fields=["status"])
                bot.send_message(message.chat.id, f'*Данные заказа:*\nСумма заказа: {user.basket_sum}₽\n'
                                                  f'Покупатель: {user.nickname}\nТелефон: {user.mobile}\n'
                                                  f'Доставка: {user.delivery}\nАдрес: {user.address}\n',
                                 reply_markup=keyboard_confirm(), parse_mode='markdown')
            elif message.text == '⬅️ Назад':
                user.status = '8'
                user.save(update_fields=["status"])
                bot.send_message(chat_id=message.chat.id, text=f'Укажите ваш мобильный телефон:\nСейчас:{user.mobile}',
                                 reply_markup=keyboard_number())

            elif message.text == '🏠 Начало':
                startpg(message)
            elif message.text[0] == "\'" or message.text.isdigit() or len(message.text) > 40:
                bot.send_message(chat_id=message.chat.id, text=f'Укажите корректно адрес доставки\n'
                                                               f'Улицу, дом, подъезд, квартиру и этаж:\n'
                                                               f'Сейчас:{user.address}',
                                 reply_markup=submenu())

            else:
                user.address = message.text
                user.status = 'q'
                user.save(update_fields=["address", "status"])
                bot.send_message(message.chat.id, f'*Данные заказа:*\nСумма заказа: {user.basket_sum}₽\n'
                                                  f'Покупатель: {user.nickname}\nТелефон: {user.mobile}\n'
                                                  f'Доставка: {user.delivery}\nАдрес: {user.address} \n',
                                 reply_markup=keyboard_confirm(), parse_mode='markdown')

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == 'q')
        def ordering_process(message):
            user = Users.objects.get(name=message.chat.id)
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            if message.text == '✅ Подтвердить и отправить':
                basket = user.basket_set.all()
                foods = ''
                for i in basket:
                    sum_food = i.count * i.price
                    foods += '{} - {}шт. = {} ₽\n'.format(i.name_product, i.count, sum_food)
                user.orders_set.create(amount_to_pay=user.basket_sum, type_delivery=user.delivery,
                                       address_delivery=user.address, food=foods, time_delivery=user.time_delivery)
                chat_id = Configuration.objects.get(id=1).id_channel_orders
                if user.delivery == '🚗 Привезти':

                    text = f'❗️ *Вам пришел заказ*\n\n👤 Данные покупателя:\n{user.nickname}, {user.mobile}\n\n'\
                           f'📦 Доставка:\n{user.delivery}\nАдрес: {user.address}\nВремя: {user.time_delivery}\n\n' \
                           f'*---*\n🛒  Товары:\n{foods}\n*---*\n*💰 Сумма заказа {user.basket_sum} ₽*'
                else:
                    text = f'❗️ *Вам пришел заказ*\n\n👤 Данные покупателя:\n{user.nickname}, {user.mobile}\n\n'\
                           f'📦 Доставка:\n{user.delivery}\nВремя: {user.time_delivery}\n\n*---*\n'\
                           f'🛒  Товары:\n{foods}\n*---*\n*💰 Сумма заказа {user.basket_sum} ₽*'
                bot.send_message(chat_id=chat_id, text=text, parse_mode='markdown')
                user.basket_sum = 0
                user.status = '1'
                user.basket_set.all().delete()
                user.save(update_fields=["basket_sum", "status"])
                bot.send_message(message.chat.id, 'Ваш заказ принят, ожидайте', reply_markup=start_menu())
            elif message.text == '⬅️ Назад':
                if user.delivery == '🚗 Привезти':
                    user.status = '9'
                    user.save(update_fields=["status"])
                    bot.send_message(chat_id=message.chat.id, text=f'Укажите адрес доставки\n'
                                                                   f'Улицу, дом, подъезд, квартиру и этаж:\n'
                                                                   f'Сейчас:{user.address}',
                                     reply_markup=submenu())
                else:
                    user.status = '8'
                    user.save(update_fields=["status"])
                    bot.send_message(chat_id=message.chat.id,
                                     text=f'Укажите ваш мобильный телефон:\nСейчас:{user.mobile}',
                                     reply_markup=keyboard_number())
            elif message.text == '🏠 Начало':
                startpg(message)

            else:
                bot.send_message(chat_id=message.chat.id, text='Выбирите одну из кнопок для дальнейшего действия',
                                 reply_markup=keyboard_confirm())

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == 'r')
        def feedback(message):
            if message.text == '🏠 Начало':
                Users.objects.filter(name=message.chat.id).update(status='1')
                startpg(message)
            else:
                id_channel_help = Configuration.objects.get(1).id_channel_help
                bot.forward_message(id_channel_help, message.chat.id, message.message_id)
                Users.objects.filter(name=message.chat.id).update(status='1')
                bot.send_message(message.chat.id, 'Вопрос успешно отправлен', reply_markup=start_menu())

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '3')
        def replacing_address(message):
            user = Users.objects.get(name=message.chat.id)
            if message.text == '🏠 Начало':
                user.status = '1'
                user.save(update_fields=["status"])
                startpg(message)
            elif message.text[0] == "/" or message.text.isdigit() or \
                    message.text.lower() == 'адрес' or len(message.text) > 40:
                bot.send_message(chat_id=message.chat.id,
                                 text=f'Укажите корректно адрес доставки\n'
                                      f'Улицу, дом, подъезд, квартиру и этаж:\n',
                                 reply_markup=keyboard_down())
            else:
                user.address = message.text
                user.status = '1'
                user.save(update_fields=["status", "address"])
                bot.send_message(message.chat.id, 'Адрес успешно изменен')
                commands_settings(message)

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '4')
        def number_processing(message):
            p = Users.objects.get(name=message.chat.id)
            if message.text == '🏠 Начало':
                p.status = '1'
                p.save(update_fields=["status"])
                startpg(message)
            elif message.contact is not None:
                p.mobile = message.contact.phone_number
                p.status = '1'
                p.save(update_fields=["status", "mobile"])
                bot.send_message(message.chat.id, 'Номер успешно изменен')
                commands_settings(message)
            elif message.text.isdigit() and len(message.text) == 11 and message.text[0] == '7':
                p.mobile = message.text
                p.status = '1'
                p.save(update_fields=["status", "mobile"])
                bot.send_message(message.chat.id, 'Номер успешно изменен')
                commands_settings(message)
            else:
                bot.send_message(message.chat.id, 'Введите корректное номер через 7')

        @bot.message_handler(content_types="contact")
        def handler_all(message):
            user = Users.objects.get(name=message.chat.id)
            if user.status == '8':
                user.mobile = message.contact.phone_number
                if user.delivery == '🚗 Привезти':
                    user.status = '9'
                    user.save(update_fields=["status", "mobile"])
                    if user.address == '' or user.address is None:
                        bot.send_message(chat_id=message.chat.id, text=f'Укажите адрес доставки\n'
                                                                       f'Улицу, дом, подъезд, квартиру и этаж:\n'
                                                                       f'Сейчас:не указан',
                                         reply_markup=keyboard_back())
                    else:
                        bot.send_message(chat_id=message.chat.id, text=f'Укажите адрес доставки\n'
                                                                       f' Улицу, дом, подъезд, квартиру и этаж:\n'
                                                                       f' Сейчас:{user.address}',
                                         reply_markup=submenu())
                else:
                    user.status = 'q'
                    user.save(update_fields=["status", "mobile"])
                    bot.send_message(message.chat.id, f'*Данные заказа:*\n'
                                                      f'Сумма заказа: {user.basket_sum}₽\n'
                                                      f'Покупатель: {user.nickname}\nТелефон: {user.mobile}\n'
                                                      f'Доставка: {user.delivery}',
                                     reply_markup=keyboard_confirm(), parse_mode='markdown')
            elif user.status == '4':
                user.status = '1'
                user.mobile = message.contact.phone_number
                user.save(update_fields=["status", "mobile"])
                bot.send_message(message.chat.id, 'Номер успешно изменен')
                commands_settings(message)

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '5')
        def new_name(message):
            p = Users.objects.get(name=message.chat.id)
            if message.text == '🏠 Начало':
                p.status = '1'
                p.save(update_fields=["status"])
                startpg(message)
            elif message.text.isalpha() and len(message.text) < 30 and message.text.lower() != 'имя':
                p.status = '1'
                p.nickname = message.text
                p.save(update_fields=["status", "nickname"])
                bot.send_message(message.chat.id, 'Имя сохранено успешно')
                commands_settings(message)
            else:
                bot.send_message(message.chat.id, 'Введите корректное имя')

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == 'a')
        def admin_news(message):
            if message.text == '✏️Изменить новость':
                Users.objects.filter(name=message.chat.id).update(status='a1')
                bot.send_message(message.chat.id, 'Для встроенной ссылки в слово используйте\n'
                                                  '[ ваш текст](ваша ссылка).\nДля выделения <b>жирным</b>\n'
                                                  '*ваш текст*\n'
                                                  'Для  текста с <i>наклоном</i>\n_ваш текст_ ',
                                 reply_markup=keyboard_back_admin(), parse_mode='html')
            elif message.text == '📧Сделать разовую рассылку':
                Users.objects.filter(name=message.chat.id).update(status='a2')
                bot.send_message(message.chat.id, 'Для встроенной ссылки в слово используйте\n'
                                                  '[ ваш текст](ваша ссылка).\nДля выделения <b>жирным</b>\n'
                                                  '*ваш текст*\n'
                                                  'Для  текста с <i>наклоном</i>\n_ваш текст_ ',
                                 reply_markup=keyboard_back_admin(), parse_mode='html')
            elif message.text == '📰Посмотреть текущую новость':
                news = Configuration.objects.get(id=1).news.split('|')
                len_news = len(news)
                try:
                    if len_news == 1:
                        bot.send_message(message.chat.id, text=news, parse_mode='markdown')
                    elif len_news == 2:
                        bot.send_photo(message.chat.id,photo=news[1],parse_mode='markdown')
                    else:
                        bot.send_photo(message.chat.id, photo=news[1], caption=news[2], parse_mode='markdown')
                except apihelper.ApiException:
                    bot.send_message(message.chat.id, 'При написании текста вы допустили ошибку и забыли '
                                                      'выдялемое слово закрыть * или _\nИсправьте пожалуйста')
            elif message.text == '📩Сделать рассылку текущей новости':
                news = Configuration.objects.get(id=1).news.split('|')
                len_news = len(news)
                users = Users.objects.in_bulk()
                for i in users:
                    try:
                        if len_news == 1:
                            bot.send_message(users[i].name, text=news, parse_mode='markdown')
                        elif len_news == 2:
                            bot.send_photo(users[i].name, photo=news[1], parse_mode='markdown')
                        else:
                            bot.send_photo(users[i].name, photo=news[1], caption=news[2], parse_mode='markdown')
                    except apihelper.ApiException:
                        continue
                bot.send_message(message.chat.id, 'Рассылка завершена')
            elif message.text == '🔙Выйти из админ панели':
                startpg(message)
            else:
                bot.delete_message(message.chat.id, message_id=message.message_id)

        @bot.message_handler(content_types=['text', 'photo'], func=lambda message: Users.objects.get(name=message.chat.id).status == 'a1')
        def admin_news_update(message):
            Users.objects.filter(id=1).update(status='a')
            if message.text == '⬅️ Назад':
                bot.send_message(message.chat.id, 'Админ панель новостей', reply_markup=keyboard_admin())
            elif message.content_type == 'text':
                Configuration.objects.filter(id=1).update(news=message.text)
                bot.send_message(message.chat.id, 'Вы обновили новость успешно', reply_markup=keyboard_admin())
            elif message.content_type == 'photo':
                if message.caption is None:
                    text = f'photo|{message.photo[-1].file_id}'
                else:
                    text = f'photo|{message.photo[-1].file_id}|{message.caption}'
                Configuration.objects.filter(id=1).update(news=text)
                bot.send_message(message.chat.id, 'Вы обновили новость успешно', reply_markup=keyboard_admin())

        @bot.message_handler(content_types=['text', 'photo'],
                             func=lambda message: Users.objects.get(name=message.chat.id).status == 'a2')
        def admin_news_update(message):
            Users.objects.filter(id=1).update(status='a')
            if message.text == '⬅️ Назад':
                bot.send_message(message.chat.id, 'Админ панель новостей', reply_markup=keyboard_admin())
            elif message.content_type == 'text':
                users = Users.objects.in_bulk()
                for i in users:
                    try:
                        user = users[i].name
                        bot.send_message(user, message.text)
                    except apihelper.ApiException:
                        continue
                bot.send_message(message.chat.id, 'Рассылка завершена', reply_markup=keyboard_admin())
            elif message.content_type == 'photo':
                if message.caption is None:
                    users = Users.objects.in_bulk()
                    for i in users:
                        try:
                            user = users[i].name
                            bot.send_photo(user, photo=message.photo[-1].file_id)
                        except apihelper.ApiException:
                            continue
                    bot.send_message(message.chat.id, 'Рассылка завершена', reply_markup=keyboard_admin())
                else:
                    users = Users.objects.in_bulk()
                    for i in users:
                        try:
                            user = users[i].name
                            bot.send_photo(user, photo=message.photo[-1].file_id, caption=message.caption)
                        except apihelper.ApiException:
                            continue
                    bot.send_message(message.chat.id, 'Рассылка завершена', reply_markup=keyboard_admin())

        @bot.message_handler(content_types=['text'])
        def main_menu(message):
            if message.text == '🏠 Начало' or message.text == '🏠':
                startpg(message)
            elif message.text == '🍴 Меню' or message.text == '🍴':
                commands_menu(message)
            elif message.text == '📢 Новости':
                commands_news(message)
            elif message.text == '❓ Помощь':
                bot.send_message(message.chat.id, 'список команд:\n/menu - Меню\n/cart - Корзина\n'
                                                  '/history - История заказов\n/news - Наши новости и акции\n'
                                                  '/start - Главное меню',
                                 reply_markup=keyboard_help())
            elif message.text == '⚙️ Настройки':
                commands_settings(message)

            elif message.text == '📦 Заказы':
                user = Users.objects.get(name=message.chat.id)
                withdrawal_of_orders(user, message.chat.id)

            elif message.text == '🛍 Корзина' or message.text == '🛍':
                user = Users.objects.get(name=message.chat.id)
                preparing_the_bucket(user, message.chat.id)

            elif message.text == 'Имя':
                user = Users.objects.get(name=message.chat.id)
                user.status = '5'
                user.save(update_fields=["status"])
                bot.send_message(message.chat.id, 'Ваше имя: {}\nНовое назначение:'.format(user.nickname),
                                 reply_markup=keyboard_down)

            elif message.text == 'Моб.':
                user = Users.objects.get(name=message.chat.id)
                user.status = '4'
                user.save(update_fields=["status"])
                back = types.ReplyKeyboardMarkup(True, False)
                button_phone = types.KeyboardButton(text="Отправить мой номер телефона ☎️", request_contact=True)
                back.add(button_phone)
                back.row('🏠 Начало')
                if user.mobile is None:
                    text = 'Ваш мобильный телефон:'
                else:
                    text = 'Ваш мобильный телефон:{}\nНовой номер:'.format(user.mobile)
                bot.send_message(message.chat.id, text=text, reply_markup=back)

            elif message.text == 'Адрес':
                user = Users.objects.get(name=message.chat.id)
                user.status = '3'
                user.save(update_fields=["status"])
                if user.address is None:
                    bot.send_message(message.chat.id, 'Ваш адрес для доставок: не назначен',
                                     reply_markup=keyboard_down())
                else:
                    bot.send_message(message.chat.id,
                                     f'Ваш адрес для доставок: {user.address}\nВведите новый адрес:',
                                     reply_markup=keyboard_down())
            elif message.forward_from_chat is not None:
                channel = Configuration.objects.get(id=1)
                if message.forward_from_chat.title == channel.channel_orders:
                    channel.id_channel_orders = message.forward_from_chat.id
                    channel.save(update_fields=['id_channel_orders'])
                    bot.send_message(message.chat.id, 'Сохранено')
                elif message.forward_from_chat.title == channel.channel_help:
                    channel.id_channel_help = message.forward_from_chat.id
                    channel.save(update_fields=['id_channel_help'])
                    bot.send_message(message.chat.id, 'Сохранено')
            elif message.text == '✉️Вопрос оператору':
                Users.objects.filter(name=message.chat.id).update(status='r')
                bot.send_message(message.chat.id, 'Вам ответят в ближайшее время', keyboard_down())

        @bot.callback_query_handler(func=lambda c: True)
        def inline(c):
            print(c.data)
            # Выводим категорию-2 у объектов из all_menu, которые соединены с categoryTwo по fk
            user = Users.objects.get(name=c.message.chat.id)
            if c.data.split('|')[0] == 'm1':
                category_one = CategoryOne.objects.get(id=c.data.split('|')[1])
                arr = category_one.categorytwo_set.all()
                count = len(arr)
                bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                              reply_markup=menu_two(count, arr))
            elif c.data == 'empty':
                bot.answer_callback_query(c.id, text="")
            elif c.data.split('|')[0] == 'min_sum':
                bot.answer_callback_query(c.id, text=f"Минимальная сумма заказа {c.data.split('|')[1]} ₽")

            # Обработка вывода категории пиццы,разбит на отдельный кусок для упрощения
            elif c.data.split('|')[0] == 'pizza':
                keyboard = types.InlineKeyboardMarkup()
                category_one = CategoryOne.objects.get(id=c.data.split('|')[1])
                object_menu = category_one.allmenu_set.all().order_by('name')
                count = len(object_menu)
                bot.send_message(c.message.chat.id, text=f'{category_one.name}', reply_markup=keyboard_of_menu())
                for i in range(count):
                    if i < (count - 1):
                        if object_menu[i].name == object_menu[i + 1].name:
                            but = types.InlineKeyboardButton(text=f'{object_menu[i].volume}см -'
                                                                  f' {object_menu[i].price} ₽',
                                                             callback_data=f'm3|{object_menu[i].id}')
                            keyboard.add(but)
                        else:
                            but = types.InlineKeyboardButton(text=f'{object_menu[i].volume}см -'
                                                                  f' {object_menu[i].price} ₽',
                                                             callback_data=f'm3|{object_menu[i].id}')
                            keyboard.add(but)
                            if object_menu[i].weight is not None:
                                bot.send_photo(chat_id=c.message.chat.id, photo=object_menu[i].photo,
                                               caption=f'*{object_menu[i].name}*\n\nСостав:{object_menu[i].structure}\n'
                                                       f'Вес:{object_menu[i].weight} г',
                                               reply_markup=keyboard, parse_mode='markdown')
                                keyboard = types.InlineKeyboardMarkup()
                            else:
                                bot.send_photo(chat_id=c.message.chat.id, photo=object_menu[i].photo,
                                               caption=f'*{object_menu[i].name}*\n\n'
                                                       f'Состав:{object_menu[i].structure}',
                                               reply_markup=keyboard, parse_mode='markdown')
                                keyboard = types.InlineKeyboardMarkup()
                    else:
                        but = types.InlineKeyboardButton(text=f'{object_menu[i].volume}см - {object_menu[i].price} ₽',
                                                         callback_data=f'm3|{object_menu[i].id}')
                        keyboard.add(but)
                        if object_menu[i].weight is not None:
                            text = f'*{object_menu[i].name}*\n\nСостав:{object_menu[i].structure}\n' \
                                   f'Вес:{object_menu[i].weight} г'
                        else:
                            text = f'*{object_menu[i].name}*\n\nСостав:{object_menu[i].structure}'
                        bot.send_photo(chat_id=c.message.chat.id, photo=object_menu[i].photo,
                                       caption=text,
                                       reply_markup=keyboard, parse_mode='markdown')

            # выводим меню по ключу и добавляем статическием кнопки
            elif c.data.split('|')[0] == 'm2':
                category_two = CategoryTwo.objects.get(id=c.data.split('|')[1])
                category_one_or_two(category_two, c)
            elif c.data.split('|')[0] == 'sm':
                category_one = CategoryOne.objects.get(id=c.data.split('|')[1])
                category_one_or_two(category_one, c)

            # Обрабатываем нажатый товар ,добавляем его в корзину и добавляем инлай кнопку корзины
            elif c.data.split('|')[0] == 'm3':
                if user.basket_set.filter(product_id=c.data.split('|')[1]).exists():
                    user.basket_set.filter(product_id=c.data.split('|')[1]).update(count=F('count') + 1)
                else:
                    object_menu = AllMenu.objects.get(id=c.data.split('|')[1])
                    basket, _ = Basket.objects.get_or_create(
                        product_id=c.data.split('|')[1], count=1, baskUser=user, name_product=object_menu.name,
                        photo=object_menu.photo, price=object_menu.price)
                count = user.basket_set.get(product_id=c.data.split('|')[1]).count
                dish = AllMenu.objects.get(id=c.data.split('|')[1])
                bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                              reply_markup=update_object_menu(dish.price, dish.volume, count, c.data))
            elif c.data == 'Korzina':
                arr = user.basket_set.count()
                if arr > 0:
                    final_sum = user.basket_set.aggregate(sum=Sum(F('count') * F('price'), output_field=IntegerField()))
                    object_menu = user.basket_set.all()[0]
                    menu_sum = object_menu.count * object_menu.price
                    user.basket_sum = final_sum['sum']
                    user.save(update_fields=["basket_sum"])
                    if arr > 1:
                        arr_id = user.basket_set.values_list('id', flat=True)
                        bot.send_message(c.message.chat.id,
                                         text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                              f'{object_menu.count}шт [*] {object_menu.price} ₽ = {menu_sum} ₽ ',
                                         reply_markup=basket_menu(object_menu.id, object_menu.count, arr, arr_id[1],
                                                                  arr_id[arr - 1], finite_sum=final_sum['sum']),
                                         parse_mode='markdown')
                    else:
                        bot.send_message(c.message.chat.id, text=f'{object_menu.name_product}[.]({object_menu.photo})'
                                                                 f'{object_menu.count}шт [*] '
                                                                 f'{object_menu.price} ₽ = {menu_sum} ₽ ',
                                         reply_markup=basket_menu(object_menu.id, object_menu.count,
                                                                  arr, finite_sum=final_sum['sum']),
                                         parse_mode='markdown')
                else:

                    bot.send_message(c.message.chat.id,
                                     'В корзине пусто 😔\nПосмотрите /menu, там много интересного',
                                     reply_markup=start_menu())

            elif c.data.split('|')[0] == 'deleting':
                try:
                    user.basket_set.get(id=c.data.split('|')[1]).delete()
                    arr = user.basket_set.count()
                    forward = 0
                    down = 0
                    if arr > 0:
                        object_menu = user.basket_set.all()[0]
                        menu_sum = object_menu.count * object_menu.price
                        final_sum = user.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                              output_field=IntegerField()))
                        user.basket_sum = final_sum["sum"]
                        user.save(update_fields=["basket_sum"])
                        if arr > 1:
                            arr_id = user.basket_set.values_list('id', flat=True)
                            forward = arr_id[1]
                            down = arr_id[arr - 1]
                        bot.edit_message_text(text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                                   f' {object_menu.count}шт [*] {object_menu.price} ₽ = {menu_sum} ₽ ',
                                              chat_id=c.message.chat.id, message_id=c.message.message_id,
                                              reply_markup=basket_menu(object_menu.id, object_menu.count, arr,
                                                                       forward, down, finite_sum=final_sum['sum']),
                                              parse_mode='markdown')
                    else:
                        user.basket_sum = 0
                        user.save(update_fields=["basket_sum"])
                        bot.answer_callback_query(c.id, text="")
                        bot.clear_step_handler_by_chat_id(chat_id=c.message.chat.id)
                        bot.send_message(c.message.chat.id, 'В корзине пусто 😔\n'
                                                            'Посмотрите /menu, там много интересного',
                                         reply_markup=start_menu())
                except Exception:
                    bot.answer_callback_query(c.id, text="")

            elif c.data.split('|')[0] == 'add':
                arr = user.basket_set.count()
                if arr == 0:
                    bot.answer_callback_query(c.id, text="")
                else:
                    object_menu = user.basket_set.get(id=c.data.split('|')[1])
                    object_menu.count += 1
                    object_menu.save(update_fields=["count"])
                    menu_sum = object_menu.count * object_menu.price
                    final_sum = user.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                          output_field=IntegerField()))
                    user.basket_sum = final_sum["sum"]
                    user.save(update_fields=["basket_sum"])
                    bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                          text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                               f'{object_menu.count}шт [*] {object_menu.price} ₽ = {menu_sum} ₽ ',
                                          reply_markup=basket_menu(object_menu.id, object_menu.count, arr,
                                                                   int(c.data.split('|')[2]),
                                                                   int(c.data.split('|')[3]),
                                                                   int(c.data.split('|')[4]),
                                                                   finite_sum=final_sum['sum']),
                                          parse_mode='markdown')

            elif c.data.split('|')[0] == 'r':
                try:
                    arr = user.basket_set.count()
                    object_menu = user.basket_set.get(id=c.data.split('|')[1])
                    product = types.InlineKeyboardMarkup(row_width=4)
                    but_11 = types.InlineKeyboardButton(text='❌', callback_data='deleting|{}'.format(object_menu.id))
                    but_12 = types.InlineKeyboardButton(text='🔺',
                                                        callback_data='add|{0}|{1}|{2}|{3}'.format(object_menu.id,
                                                                                                   int(c.data.split(
                                                                                                       '|')[
                                                                                                           2]),
                                                                                                   int(c.data.split(
                                                                                                       '|')[
                                                                                                           3]),
                                                                                                   int(c.data.split(
                                                                                                       '|')[
                                                                                                           4])))
                    if object_menu.count == 1:
                        but_13 = types.InlineKeyboardButton(text='{} шт.'.format(object_menu.count),
                                                            callback_data='empty')
                        but_14 = types.InlineKeyboardButton(text='🔻', callback_data='empty')

                    else:
                        object_menu.count -= 1
                        object_menu.save(update_fields=["count"])
                        but_13 = types.InlineKeyboardButton(text='{} шт.'.format(object_menu.count),
                                                            callback_data='empty')
                        but_14 = types.InlineKeyboardButton(text='🔻',
                                                            callback_data='r|{0}|{1}|{2}|{3}'.format(object_menu.id,
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
                    final_sum = user.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                          output_field=IntegerField()))
                    user.basket_sum = final_sum["sum"]
                    user.save(update_fields=["basket_sum"])
                    but_31 = types.InlineKeyboardButton(text=f'✅ Оформить заказ на {final_sum["sum"]} ₽',
                                                        callback_data='order_registration')
                    product.add(but_11, but_12, but_13, but_14)
                    product.add(but_21, but_22, but_23)
                    product.add(but_31)
                    menu_sum = object_menu.count * object_menu.price
                    bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                          text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                               f' {object_menu.count}шт [*] {object_menu.price} ₽ = {menu_sum} ₽ ',
                                          reply_markup=product,
                                          parse_mode='markdown')
                except Exception:
                    bot.answer_callback_query(c.id, text="")

            elif c.data.split('|')[0] == 'down':
                try:
                    object_menu = user.basket_set.get(id=c.data.split('|')[1])
                    arr_id = user.basket_set.values_list('id', flat=True)
                    arr = len(arr_id)
                    menu_sum = object_menu.count * object_menu.price
                    final_sum = user.basket_set.aggregate(sum=Sum(F('count') * F('price'), output_field=IntegerField()))
                    user.basket_sum = final_sum["sum"]
                    user.save(update_fields=["basket_sum"])
                    up, down, number_str = 0, 0, 0
                    if object_menu.id == arr_id[0]:
                        up = arr_id[1]
                        number_str = 1
                        down = arr_id[arr - 1]

                    elif object_menu.id == arr_id[arr - 1]:
                        up = arr_id[0]
                        number_str = arr
                        down = arr_id[arr - 2]

                    else:
                        for i in range(1, arr):
                            if object_menu.id == arr_id[i]:
                                up = arr_id[i + 1]
                                number_str = i + 1
                                down = arr_id[i - 1]
                    bot.edit_message_text(text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                               f' {object_menu.count}шт [*] {object_menu.price} ₽ = {menu_sum} ₽ ',
                                          chat_id=c.message.chat.id, message_id=c.message.message_id,
                                          reply_markup=basket_menu(object_menu.id, object_menu.count, arr, up, down,
                                                                   number_str, finite_sum=final_sum['sum']),
                                          parse_mode='markdown')
                except Exception:
                    bot.answer_callback_query(c.id, text="")
            elif c.data.split('|')[0] == 'first':
                try:
                    forward, down = 0, 0
                    object_menu = user.basket_set.get(id=c.data.split('|')[1])
                    arr = user.basket_set.count()
                    arr_id = user.basket_set.values_list('id', flat=True)
                    number_str = 1

                    menu_sum = object_menu.count * object_menu.price
                    final_sum = user.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                          output_field=IntegerField()))
                    user.basket_sum = final_sum["sum"]
                    user.save(update_fields=["basket_sum"])
                    if object_menu.id == arr_id[arr - 1]:
                        number_str = arr
                        forward = arr_id[0]
                        down = arr_id[arr - 2]

                    elif object_menu.id == arr_id[0]:
                        forward = arr_id[1]
                        down = arr_id[arr - 1]
                    else:
                        for i in range(0, arr):
                            if arr_id[i] == object_menu.id:
                                forward = arr_id[i + 1]
                                number_str = i + 1
                                down = arr_id[i - 1]
                    bot.edit_message_text(text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                               f' {object_menu.count}шт [*] {object_menu.price} ₽ = {menu_sum} ₽ ',
                                          chat_id=c.message.chat.id, message_id=c.message.message_id,
                                          reply_markup=basket_menu(object_menu.id, object_menu.count,
                                                                   arr, forward, down, number_str, final_sum['sum']),
                                          parse_mode='markdown')
                except Exception:
                    bot.answer_callback_query(c.id, text="")

            elif c.data.split('|')[0] == 'tn' or c.data.split('|')[0] == 'td':
                try:
                    id_order = int(c.data.split('|')[1])
                    arr_id = user.orders_set.values_list('id', flat=True)
                    count = len(arr_id)
                    object_one = user.orders_set.get(id=id_order)
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
                    date_time = object_one.data.strftime("%d-%m-%Y %H:%M")
                    bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                          text=f'Дата: {date_time} \n'
                                               f'Сумма: {object_one.amount_to_pay} ₽ \n'
                                               f'Доставка: {object_one.type_delivery} '
                                               f' {object_one.time_delivery} \n'
                                               f'Адрес: {object_one.address_delivery}\n \n'
                                               f'Блюда: \n{object_one.food}',
                                          reply_markup=product, parse_mode='markdown')
                except Exception:
                    bot.answer_callback_query(c.id, text="")

            elif c.data == 'order_registration' and user.status == '1':
                bot.answer_callback_query(c.id, text="")
                user.status = '2'
                user.save(update_fields=["status"])
                bot.clear_step_handler_by_chat_id(chat_id=c.message.chat.id)
                if user.basket_set.count() == 0:
                    bot.answer_callback_query(c.id, text="")
                    bot.enable_save_next_step_handlers(delay=2)
                else:
                    back = types.ReplyKeyboardMarkup(True, False)
                    back.row('✅ Верно')
                    back.row('🏃 Заберу сам', '🚗 Привезти')
                    back.row('🏠 Начало', '⬅️ Назад')
                    bot.send_message(c.message.chat.id,
                                     f'Укажите вариант доставки \nНа данный момент: {user.delivery}',
                                     reply_markup=back)

            # В начало
            elif c.data == 'vnachalo':
                bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                              reply_markup=menu())
            else:
                bot.answer_callback_query(c.id, text="")

        bot.polling(none_stop=True)
