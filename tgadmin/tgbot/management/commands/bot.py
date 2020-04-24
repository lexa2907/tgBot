from django.core.management.base import BaseCommand
import telebot
from telebot import types
from telebot import apihelper
from django.db.models import F, IntegerField
import re
from django.db.models import Sum
from tgbot.models import CategoryOne, CategoryTwo, AllMenu, Users, Basket
from tgadmin.settings import BOT
from tgbot.keyboard import startmenu, newmenu, submenu, keyboard_number, menu
import json


class Command(BaseCommand):
    help = "ТЕлеграмм бот"

    def handle(self, *args, **options):
        bot = telebot.TeleBot(BOT)
        apihelper.proxy = {'https': 'socks5h://PrhZ8F:eebLU48kCY@188.130.129.144:5501'}

        def preparing_the_bucket(p, message):
            arr = p.basket_set.count()
            if arr > 0:
                object_menu = p.basket_set.all()[0]
                sum = object_menu.count * object_menu.price
                final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'), output_field=IntegerField()))
                if arr > 1:
                    arr_id = p.basket_set.values_list('id', flat=True)
                    bot.send_message(message.chat.id,
                                     text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                          f'{object_menu.count}шт [*] {object_menu.price} ₽ = {sum} ₽ ',
                                     reply_markup=newmenu(object_menu.id, object_menu.count, arr, forward=arr_id[1],
                                                          down=arr_id[arr - 1], finite_sum=final_sum['sum']),
                                     parse_mode='markdown')
                else:
                    bot.send_message(message.chat.id,
                                     text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                          f' {object_menu.count}шт [*] {object_menu.price} ₽ = {sum} ₽ ',
                                     reply_markup=newmenu(object_menu.id, object_menu.count, arr,
                                                          finite_sum=final_sum['sum']),
                                     parse_mode='markdown')
            else:

                bot.send_message(message.chat.id,
                                 'В корзине пусто 😔\nПосмотрите /menu, там много интересного',
                                 reply_markup=startmenu())

        def withdrawal_of_orders(p, message):
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
                date_time = object_one.data.strftime("%d-%m-%Y %H:%M")
                if object_one.type_delivery == '🚗 Привезти':
                    bot.send_message(message.chat.id, text=f'Дата: {date_time}\n'
                                                           f'Сумма: {object_one.amount_to_pay} ₽\n'
                                                           f'Доставка: {object_one.type_delivery} '
                                                           f' {object_one.time_delivery}\n'
                                                           f'Адрес: {object_one.address_delivery}\n\n'
                                                           f'Блюда:\n{object_one.food}',
                                     reply_markup=product, parse_mode='markdown')
                else:
                    bot.send_message(message.chat.id, text=f'Дата: {date_time}\n'
                                                           f'Сумма: {object_one.amount_to_pay} ₽\n'
                                                           f'Доставка: {object_one.type_delivery} '
                                                           f' {object_one.time_delivery}\n\n'
                                                           f'Блюда:\n{object_one.food}',
                                     reply_markup=product, parse_mode='markdown')
            else:
                bot.send_message(message.chat.id, text='Вы еще не заказывали')

        def update_sum(message):
            if message.text == '🏠 Начало':
                startpg(message)
            elif message.text.isdigit():
                bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
                min_sum = {'max_sum': int(message.text)}
                new_min_sum = json.dumps(min_sum, ensure_ascii=False)
                with open('sum.json', 'w', encoding="utf-8") as f:
                    f.write(new_min_sum)
                bot.send_message(message.chat.id, 'Вы обновили минимальную сумму успешно', reply_markup=startmenu())
            else:
                error = bot.send_message(message.chat.id, 'Введите только целое число')
                bot.register_next_step_handler(error, update_sum)

        def changing_the_news(message):
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            if message.text == '🏠 Начало':
                startpg(message)
            else:
                news = {'news': f'{message.text}'}
                new_news = json.dumps(news, ensure_ascii=False)
                with open('data.json', 'w', encoding="utf-8") as f:
                    f.write(new_news)
                bot.send_message(message.chat.id, 'Вы обновили новость успешно', reply_markup=startmenu())

        @bot.message_handler(commands=['start'])
        def startpg(message):
            p, _ = Users.objects.get_or_create(name=message.chat.id,
                                               defaults={'nickname': message.from_user.first_name})
            bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=startmenu())

        @bot.message_handler(commands=['cart'])
        def commands_cart(message):
            p = Users.objects.get(name=message.chat.id)
            preparing_the_bucket(p, message)

        @bot.message_handler(commands=['menu'])
        def commands_menu(message):
            back = types.ReplyKeyboardMarkup(True, False)
            back.row('🏠 Начало')
            bot.send_message(message.chat.id, 'Меню', reply_markup=back)
            bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд:', reply_markup=menu())

        @bot.message_handler(commands=['history'])
        def commands_history(message):
            p = Users.objects.get(name=message.chat.id)
            withdrawal_of_orders(p, message)

        @bot.message_handler(commands=['settings'])
        def commands_settings(message):
            back = types.ReplyKeyboardMarkup(True, False)
            back.row('Имя', 'Моб.', 'Адрес')
            back.row('🏠 Начало')
            bot.send_message(message.chat.id, 'Ваши настройки:', reply_markup=back)

        @bot.message_handler(commands=['news'])
        def commands_news(message):
            with open('data.json', "r", encoding="utf-8") as file:
                f = json.load(file)
            back = types.ReplyKeyboardMarkup(True, False)
            back.row('🏠 Начало')
            bot.send_message(message.chat.id, f'{f["news"]}', reply_markup=back, parse_mode='markdown')

        @bot.message_handler(commands=['admin_min_sum'])
        def update_min_sum(message):
            if Users.objects.get(id=1).name == int(message.chat.id):
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало')
                with open('sum.json', 'r') as f:
                    max_sum = json.load(f)
                new_min_sum = bot.send_message(message.chat.id, f'Введите минимальную сумму для заказов:\n'
                                                                f'Сейчас: {max_sum["max_sum"]} ₽',
                                               reply_markup=back)
                bot.register_next_step_handler(new_min_sum, update_sum)

        @bot.message_handler(commands=['admin_news'])
        def update_news(message):
            if Users.objects.get(id=1).name == int(message.chat.id):
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало')
                new_news = bot.send_message(message.chat.id, 'Для встроенной ссылки в слово используйте\n'
                                                             '[ ваш текст](ваша ссылка).\nДля выделения <b>жирным</b>\n'
                                                             '*ваш текст*\n'
                                                             'Для  текста с <i>наклоном</i>\n_ваш текст_ ',
                                            reply_markup=back, parse_mode='html')
                bot.register_next_step_handler(new_news, changing_the_news)

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '2')
        def choice_of_delivery(message):
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            p = Users.objects.get(name=message.chat.id)
            p.status = '1'
            p.save(update_fields=["status"])
            with open('sum.json', 'r') as f:
                max_sum = json.load(f)
            if message.text == '🏠 Начало':
                startpg(message)

            elif message.text == '⬅️ Назад':
                bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
                bot.send_message(chat_id=message.chat.id, text='Главное меню', reply_markup=startmenu())
                preparing_the_bucket(p, message)

            elif max_sum["max_sum"] > p.basket_sum:

                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало', '🍴 Меню')
                bot.send_message(chat_id=message.chat.id, text=f'Минимальная сумма заказа {max_sum["max_sum"]} ₽. '
                                 f'Закажите ещё что-нибудь /menu  ', reply_markup=back)

            elif message.text == '✅ Верно':
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('Как можно скорее')
                back.row('🏠 Начало', '⬅️ Назад')
                bot.send_message(chat_id=message.chat.id, text=f'{p.delivery}\nСтоимость - 0 ₽')
                if p.delivery == '🏃 Заберу сам':
                    text_message = f'Укажите к какому времени приготовить заказ:\nСейчас: {p.time_delivery}'
                else:
                    text_message = f'Укажите время доставки:\nСейчас: {p.time_delivery}'
                time_delivery = bot.send_message(chat_id=message.chat.id,
                                                 text=text_message,
                                                 reply_markup=back)
                bot.register_next_step_handler(time_delivery, processing_delivery)

            elif message.text == '🏃 Заберу сам' or message.text == '🚗 Привезти':
                p.delivery = message.text
                p.save(update_fields=["delivery"])
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('Как можно скорее')
                back.row('🏠 Начало', '⬅️ Назад')
                bot.send_message(chat_id=message.chat.id, text=f'{message.text}\nСтоимость - 0 ₽')
                if message.text == '🏃 Заберу сам':
                    text_message = f'Укажите к какому времени приготовить заказ:\nСейчас: {p.time_delivery}'
                else:
                    text_message = f'Укажите время доставки:\nСейчас: {p.time_delivery}'
                time_delivery = bot.send_message(chat_id=message.chat.id, text=text_message, reply_markup=back)
                bot.register_next_step_handler(time_delivery, processing_delivery)
            else:
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('🏃 Заберу сам', '🚗 Привезти')
                back.row('🏠 Начало', '⬅️ Назад')
                type_delivery = bot.send_message(chat_id=message.chat.id,
                                                 text='Выберите один из предложенных вариантов',
                                                 reply_markup=back)
                bot.register_next_step_handler(type_delivery, choice_of_delivery)

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '3')
        def replacing_address(message):
            p = Users.objects.get(name=message.chat.id)
            if message.text == '🏠 Начало':
                p.status = '1'
                p.save(update_fields=["status"])
                startpg(message)
            elif message.text[0] == "/" or message.text.isdigit() or \
                    message.text.lower() == 'адрес' or len(message.text) > 40:
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало')
                bot.send_message(chat_id=message.chat.id,
                                 text=f'Укажите корректно адрес доставки\n'
                                      f'Улицу, дом, подъезд, квартиру и этаж:\n',
                                 reply_markup=back)
            else:
                p.address = message.text
                p.status = '1'
                p.save(update_fields=["status","address"])
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
                p.mobile = message.contact.phone_number[1:]
                p.status = '1'
                p.save(update_fields=["status","mobile"])
                bot.send_message(message.chat.id, 'Номер успешно изменен')
                commands_settings(message)
            elif message.text.isdigit() and len(message.text) == 11 and message.text[0] == '7':
                p.mobile = message.text
                p.status = '1'
                p.save(update_fields=["status","mobile"])
                bot.send_message(message.chat.id, 'Номер успешно изменен')
                commands_settings(message)
            else:
                bot.send_message(message.chat.id, 'Введите корректное номер через 7')

        @bot.message_handler(content_types="contact")
        def handler_all(message):
            p = Users.objects.get(name=message.chat.id)
            p.mobile = message.contact.phone_number[1:]
            p.status = '1'
            p.save(update_fields=["status","mobile"])
            bot.send_message(message.chat.id, 'Номер успешно изменен')
            commands_settings(message)

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '5')
        def newName(message):
            p = Users.objects.get(name=message.chat.id)
            if message.text == '🏠 Начало':
                p.status = '1'
                p.save(update_fields=["status"])
                startpg(message)
            elif message.text.isalpha() and len(message.text) < 30 and message.text.lower() != 'имя':
                p.status = '1'
                p.nickname = message.text
                p.save(update_fields=["status","nickname"])
                bot.send_message(message.chat.id, 'Имя сохранено успешно')
                commands_settings(message)
            else:
                bot.send_message(message.chat.id, 'Введите корректное имя')

        @bot.message_handler(content_types=['text'])
        def osnov(message):
            if message.text == '🏠 Начало':
                global nachalo
                nachalo = 'nachalo'
                startpg(message)

            elif message.text == '🏠':
                startpg(message)

            elif message.text == '🍴 Меню' or message.text == '🍴':
                commands_menu(message)

            elif message.text == '📢 Новости':
                commands_news(message)

            elif message.text == '❓ Помощь':
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало')
                bot.send_message(message.chat.id, 'список команд:\n/menu - Меню\n/cart - Корзина\n'
                                                  '/history - История заказов\n/news - Наши новости и акции\n'
                                                  '/start - Главное меню',
                                 reply_markup=back)
            elif message.text == '⚙️ Настройки':
                commands_settings(message)

            elif message.text == '📦 Заказы':
                p = Users.objects.get(name=message.chat.id)
                withdrawal_of_orders(p, message)

            elif message.text == '🛍 Корзина' or message.text == '🛍':
                p = Users.objects.get(name=message.chat.id)
                preparing_the_bucket(p, message)

            elif message.text == 'Имя':
                p = Users.objects.get(name=message.chat.id)
                p.status = '5'
                p.save(update_fields=["status"])
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало')
                bot.send_message(message.chat.id, 'Ваше имя: {}\nНовое назначение:'.format(p.nickname),
                                 reply_markup=back)

            elif message.text == 'Моб.':
                p = Users.objects.get(name=message.chat.id)
                p.status = '4'
                p.save(update_fields=["status"])
                back = types.ReplyKeyboardMarkup(True, False)
                button_phone = types.KeyboardButton(text="Отправить мой номер телефона ☎️", request_contact=True)
                back.add(button_phone)
                back.row('🏠 Начало')
                if p.mobile is None:
                    bot.send_message(message.chat.id, 'Ваш мобильный телефон:', reply_markup=back)
                else:
                    bot.send_message(message.chat.id,'Ваш мобильный телефон:{}\nНовой номер:'.format(p.mobile),
                                     reply_markup=back)

            elif message.text == 'Адрес':
                p = Users.objects.get(name=message.chat.id)
                p.status = '3'
                p.save(update_fields=["status"])
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало')
                if p.address is None:
                    bot.send_message(message.chat.id, 'Ваш адрес для доставок: не назначен', reply_markup=back)
                else:
                    bot.send_message(message.chat.id,
                                     f'Ваш адрес для доставок: {p.address}\nВведите новый адрес:', reply_markup=back)

        @bot.callback_query_handler(func=lambda c: True)
        def inline(c):
            print(c.data)
            # Выводим категорию2
            p = Users.objects.get(name=c.message.chat.id)
            print(p.status)
            if c.data.split('|')[0] == 'm1':
                menu_two = types.InlineKeyboardMarkup()
                rr = CategoryOne.objects.get(id=c.data.split('|')[1])
                count = rr.categorytwo_set.count()
                arr = rr.categorytwo_set.all()
                if count % 2 == 0:
                    for i in range(0, count, 2):
                        but_1 = types.InlineKeyboardButton(text=arr[i].name, callback_data=f'm2|{arr[i].id}')
                        but_2 = types.InlineKeyboardButton(text=arr[i + 1].name, callback_data=f'm2|{arr[i+1].id}')
                        menu_two.add(but_1, but_2)
                else:
                    but_0 = types.InlineKeyboardButton(text=arr[0].name, callback_data=f'm2|{arr[0].id}')
                    menu_two.add(but_0)
                    for i in range(1, count, 2):
                        but_1 = types.InlineKeyboardButton(text=arr[i].name, callback_data=f'm2|{arr[i].id}')
                        but_2 = types.InlineKeyboardButton(text=arr[i + 1].name, callback_data=f'm2|{arr[i+1].id}')
                        menu_two.add(but_1, but_2)
                but_down = types.InlineKeyboardButton(text='В начало меню', callback_data='vnachalo')
                menu_two.add(but_down)
                bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                              reply_markup=menu_two)
            elif c.data == 'empty':
                bot.answer_callback_query(c.id, text="")

            elif c.data.split('|')[0] == 'max_sum':
                bot.answer_callback_query(c.id, text=f"Минимальная сумма заказа {c.data.split('|')[1]} ₽")

            # elif c.data == 'pizza':
            #     menu_category = types.InlineKeyboardMarkup()
            #     menu_pizza = CategoryTwo.objects.get(name='Пицца')
            #     pizza = menu_pizza.allmenu_set.all().order_by('name')
            #     count = len(pizza)
            #     menu_three = types.ReplyKeyboardMarkup(True, False)
            #     menu_three.row('🏠', '🍴', '🛍')
            #     bot.send_message(c.message.chat.id, text='Пицца', reply_markup=menu_three)
            #     for i in range(count):
            #         if i < (count - 1):
            #             if pizza[i].name == pizza[i + 1].name:
            #                 but = types.InlineKeyboardButton(text=f'{pizza[i].volume}см - {pizza[i].price} ₽',
            #                                                  callback_data='empty')
            #                 menu_category.add(but)
            #             else:
            #                 but = types.InlineKeyboardButton(text=f'{pizza[i].volume}см - {pizza[i].price} ₽',
            #                                                  callback_data='empty')
            #                 menu_category.add(but)
            #                 if pizza[i].weight is not None:
            #                     bot.send_photo(chat_id=c.message.chat.id, photo=pizza[i].photo,
            #                                    caption=f'{pizza[i].name}\n\n'
            #                                            f'Состав:{pizza[i].structure}\nВес:{pizza[i].weight} г',
            #                                    reply_markup=menu_category)
            #                     menu_category = types.InlineKeyboardMarkup()
            #                 else:
            #                     bot.send_photo(chat_id=c.message.chat.id, photo=pizza[i].photo,
            #                                    caption=f'{pizza[i].name}\n\n'
            #                                            f'Состав:{pizza[i].structure}', reply_markup=menu_category)
            #                     menu_category = types.InlineKeyboardMarkup()
            #         else:
            #             but = types.InlineKeyboardButton(text=f'{pizza[i].volume}см - {pizza[i].price} ₽',
            #                                              callback_data='empty')
            #             menu_category.add(but)
            #             if pizza[i].weight is not None:
            #                 bot.send_photo(chat_id=c.message.chat.id, photo=pizza[i].photo,
            #                                caption=f'{pizza[i].name}\n\n'
            #                                        f'Состав:{pizza[i].structure}\nВес:{pizza[i].weight} г',
            #                                reply_markup=menu_category)
            #             else:
            #                 bot.send_photo(chat_id=c.message.chat.id, photo=pizza[i].photo,
            #                                caption=f'{pizza[i].name}\n\n'
            #                                        f'Состав:{pizza[i].structure}', reply_markup=menu_category)
            # elif c.data.split('|')[0] == 'add_pizza':

            # выводим меню по ключу и добавляем статическием кнопки
            elif c.data.split('|')[0] == 'm2':
                rr = CategoryTwo.objects.get(id=c.data.split('|')[1])
                menu_three = types.ReplyKeyboardMarkup(True, False)
                menu_three.row('🏠', '🍴', '🛍')
                bot.send_message(c.message.chat.id, rr.name, reply_markup=menu_three)
                bot.answer_callback_query(c.id, text="")
                for i in rr.allmenu_set.all():
                    menu_category = types.InlineKeyboardMarkup()
                    if i.volume is None:
                        but_11 = types.InlineKeyboardButton(text='1шт - {} ₽'.format(i.price),
                                                            callback_data=f'm3|{i.id}')
                        menu_category.add(but_11)
                        bot.send_photo(c.message.chat.id, i.photo,
                                       caption="{}\n{}\nВес: {}г".format(i.name, i.structure, i.weight),
                                       reply_markup=menu_category)
                    elif i.weight is None:
                        but_11 = types.InlineKeyboardButton(text='{}шт - {} ₽'.format(i.volume, i.price),
                                                            callback_data=f'm3|{i.id}')
                        menu_category.add(but_11)
                        bot.send_photo(c.message.chat.id, i.photo,
                                       caption="{}\n{}\nОбъем: {}шт.".format(i.name, i.structure, i.volume),
                                       reply_markup=menu_category)
                    else:
                        but_11 = types.InlineKeyboardButton(text='{}шт - {} ₽'.format(i.volume, i.price),
                                                            callback_data=f'm3|{i.id}')
                        menu_category.add(but_11)
                        bot.send_photo(c.message.chat.id, i.photo,
                                       caption="{}\n{}\nОбъем: {}шт.\nВес: {}г".format(i.name, i.structure,
                                                                                       i.volume, i.weight),
                                       reply_markup=menu_category)
            # Обрабатываем нажатый товар ,добавляем его в корзину и добавляем инлай кнопку корзины

            elif c.data.split('|')[0] == 'm3':
                if p.basket_set.filter(product_id=c.data.split('|')[1]).exists():
                    p.basket_set.filter(product_id=c.data.split('|')[1]).update(count=F('count') + 1)
                else:
                    object_menu = AllMenu.objects.get(id=c.data.split('|')[1])
                    basket, _ = Basket.objects.get_or_create(
                        product_id=c.data.split('|')[1], count=1, baskUser=p, name_product=object_menu.name,
                        photo=object_menu.photo, price=object_menu.price)
                object_product = types.InlineKeyboardMarkup()
                count = p.basket_set.get(product_id=c.data.split('|')[1]).count
                dish = AllMenu.objects.get(id=c.data.split('|')[1])
                if dish.volume is None:

                    but_11 = types.InlineKeyboardButton(text='1шт - {} ₽ ({} шт.)'.format(dish.price, count),
                                                        callback_data=c.data)
                else:
                    but_11 = types.InlineKeyboardButton(text='{}шт - {} ₽ ({} шт.)'.format(dish.volume, dish.price,
                                                                                           count),
                                                        callback_data=c.data)
                but_12 = types.InlineKeyboardButton(text='🛍 Корзина', callback_data="Korzina")
                object_product.add(but_11)
                object_product.add(but_12)
                bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                              reply_markup=object_product)
            elif c.data == 'Korzina':
                arr = p.basket_set.count()
                if arr > 0:
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'), output_field=IntegerField()))
                    object_menu = p.basket_set.all()[0]
                    sum = object_menu.count * object_menu.price
                    if arr > 1:
                        arr_id = p.basket_set.values_list('id', flat=True)
                        bot.send_message(c.message.chat.id,
                                         text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                              f' {object_menu.count}шт [*] {object_menu.price} ₽ = {sum} ₽ ',
                                         reply_markup=newmenu(object_menu.id, object_menu.count, arr, forward=arr_id[1],
                                                              down=arr_id[arr - 1], finite_sum=final_sum['sum']),
                                         parse_mode='markdown')
                    else:
                        bot.send_message(c.message.chat.id, text=f'{object_menu.name_product}[.]({object_menu.photo})'
                                                                 f' {object_menu.count}шт [*] '
                                                                 f'{object_menu.price} ₽ = {sum} ₽ ',
                                         reply_markup=newmenu(object_menu.id, object_menu.count,
                                                              arr, finite_sum=final_sum['sum']),
                                         parse_mode='markdown')
                else:

                    bot.send_message(c.message.chat.id,
                                     'В корзине пусто 😔\nПосмотрите /menu, там много интересного',
                                     reply_markup=startmenu())

            elif c.data.split('|')[0] == 'deleting':
                try:
                    p.basket_set.get(id=c.data.split('|')[1]).delete()
                    arr = p.basket_set.count()
                    forward = 0
                    down = 0
                    if arr > 0:
                        object_menu = p.basket_set.all()[0]
                        sum = object_menu.count * object_menu.price
                        final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                           output_field=IntegerField()))
                        p.basket_sum = final_sum["sum"]
                        p.save(update_fields=["basket_sum"])
                        if arr > 1:
                            arr_id = p.basket_set.values_list('id', flat=True)
                            forward = arr_id[1]
                            down = arr_id[arr - 1]
                        bot.edit_message_text(text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                                   f' {object_menu.count}шт [*] {object_menu.price} ₽ = {sum} ₽ ',
                                              chat_id=c.message.chat.id, message_id=c.message.message_id,
                                              reply_markup=newmenu(object_menu.id, object_menu.count, arr,
                                                                   forward, down, finite_sum=final_sum['sum']),
                                              parse_mode='markdown')
                    else:
                        p.basket_sum = 0
                        p.save(update_fields=["basket_sum"])
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
                    object_menu = p.basket_set.get(id=c.data.split('|')[1])
                    sum = object_menu.count * object_menu.price
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                               output_field=IntegerField()))
                    p.basket_sum = final_sum["sum"]
                    p.save(update_fields=["basket_sum"])
                    bot.edit_message_text(chat_id=c.message.chat.id,message_id=c.message.message_id,
                                          text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                               f' {object_menu.count}шт [*] {object_menu.price} ₽ = {sum} ₽ ',
                                          reply_markup=newmenu(object_menu.id, object_menu.count, arr,
                                                               int(c.data.split('|')[2]),
                                                               int(c.data.split('|')[3]),
                                                               int(c.data.split('|')[4]),
                                                               finite_sum=final_sum['sum']),
                                          parse_mode='markdown')

            elif c.data.split('|')[0] == 'r':
                try:
                    arr = p.basket_set.count()
                    object_menu = p.basket_set.get(id=c.data.split('|')[1])
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
                        count = 1
                        but_13 = types.InlineKeyboardButton(text='{} шт.'.format(object_menu.count),
                                                            callback_data='empty')
                        but_14 = types.InlineKeyboardButton(text='🔻', callback_data='empty')

                    else:
                        p.basket_set.filter(id=c.data.split('|')[1]).update(count=F('count') - 1)
                        count = object_menu.count - 1
                        but_13 = types.InlineKeyboardButton(text='{} шт.'.format(object_menu.count - 1),
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
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                               output_field=IntegerField()))
                    p.basket_sum = final_sum["sum"]
                    p.save(update_fields=["basket_sum"])
                    but_31 = types.InlineKeyboardButton(text=f'✅ Оформить заказ на {final_sum["sum"]} ₽',
                                                        callback_data='order_registration')
                    product.add(but_11, but_12, but_13, but_14)
                    product.add(but_21, but_22, but_23)
                    product.add(but_31)
                    sum = count * object_menu.price
                    bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                          text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                               f' {count}шт [*] {object_menu.price} ₽ = {sum} ₽ ',
                                          reply_markup=product,
                                          parse_mode='markdown')
                except:
                    bot.answer_callback_query(c.id, text="")

            elif c.data.split('|')[0] == 'down':
                try:
                    object_menu = p.basket_set.get(id=c.data.split('|')[1])
                    arr = p.basket_set.count()
                    arr_id = p.basket_set.values_list('id', flat=True)
                    sum = object_menu.count * object_menu.price
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'), output_field=IntegerField()))
                    p.basket_sum = final_sum["sum"]
                    p.save(update_fields=["basket_sum"])
                    if object_menu.id == arr_id[0]:
                        forward = arr_id[1]
                        number_str = 1
                        down = arr_id[arr - 1]

                    elif object_menu.id == arr_id[arr - 1]:
                        forward = arr_id[0]
                        number_str = arr
                        down = arr_id[arr - 2]

                    else:
                        for i in range(1, arr):
                            if object_menu.id == arr_id[i]:
                                forward = arr_id[i + 1]
                                number_str = i + 1
                                down = arr_id[i - 1]

                    bot.edit_message_text(text=f'{object_menu.name_product}[.]({object_menu.photo})\n'
                                               f' {object_menu.count}шт [*] {object_menu.price} ₽ = {sum} ₽ ',
                                          chat_id=c.message.chat.id, message_id=c.message.message_id,
                                          reply_markup=newmenu(object_menu.id, object_menu.count,
                                                               arr, forward, down, number_str,
                                                               finite_sum=final_sum['sum']),
                                          parse_mode='markdown')
                except:
                    bot.answer_callback_query(c.id, text="")
            elif c.data.split('|')[0] == 'first':
                try:
                    object_menu = p.basket_set.get(id=c.data.split('|')[1])
                    arr = p.basket_set.count()
                    arr_id = p.basket_set.values_list('id', flat=True)
                    number_str = 1

                    sum = object_menu.count * object_menu.price
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                               output_field=IntegerField()))
                    p.basket_sum = final_sum["sum"]
                    p.save(update_fields=["basket_sum"])
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
                                               f' {object_menu.count}шт [*] {object_menu.price} ₽ = {sum} ₽ ',
                                          chat_id=c.message.chat.id, message_id=c.message.message_id,
                                          reply_markup=newmenu(object_menu.id, object_menu.count,
                                                               arr, forward, down, number_str, final_sum['sum']),
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
                    date_time = object_one.data.strftime("%d-%m-%Y %H:%M")
                    bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                          text=f'Дата: {date_time} \n'
                                               f'Сумма: {object_one.amount_to_pay} ₽ \n'
                                               f'Доставка: {object_one.type_delivery} '
                                               f' {object_one.time_delivery} \n'
                                               f'Адрес: {object_one.address_delivery}\n \n'
                                               f'Блюда: \n{object_one.food}',
                                          reply_markup=product, parse_mode='markdown')
                except:
                    bot.answer_callback_query(c.id, text="")

            elif c.data == 'order_registration' and p.status == '1':
                bot.answer_callback_query(c.id, text="")
                p.status = '2'
                p.save(update_fields=["status"])
                bot.clear_step_handler_by_chat_id(chat_id=c.message.chat.id)
                    # dick = types.InlineKeyboardMarkup(row_width=3)
                    # dick.add(types.InlineKeyboardButton(text='Идет оформление заказа', callback_data='empty'))
                    # bot.edit_message_reply_markup(c.message.chat.id, message_id=c.message.message_id, reply_markup=dick)
                if p.basket_set.count() == 0:
                    bot.answer_callback_query(c.id, text="")
                    bot.enable_save_next_step_handlers(delay=2)
                else:
                    back = types.ReplyKeyboardMarkup(True, False)
                    back.row('✅ Верно')
                    back.row('🏃 Заберу сам', '🚗 Привезти')
                    back.row('🏠 Начало', '⬅️ Назад')
                    bot.send_message(c.message.chat.id,
                                     f'Укажите вариант доставки \n На данный момент: {p.delivery}',
                                     reply_markup=back)

            # В начало
            elif c.data == 'vnachalo':
                bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                              reply_markup=menu())
            else:
                bot.answer_callback_query(c.id, text="")

        def processing_delivery(message):
            p = Users.objects.get(name=message.chat.id)
            with open('sum.json', 'r') as f:
                max_sum = json.load(f)
            if max_sum["max_sum"] > p.basket_sum:
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало', '🍴 Меню')
                bot.send_message(chat_id=message.chat.id, text=f'Минимальная сумма заказа {max_sum["max_sum"]} ₽. '
                                 f'Закажите ещё что-нибудь /menu  ', reply_markup=back)
            elif message.text == '✅ Верно':
                new_name = bot.send_message(chat_id=message.chat.id,
                                            text=f'Укажите ваше имя:\nСейчас:{p.nickname}',
                                            reply_markup=submenu())
                bot.register_next_step_handler(new_name, name_processing)

            elif message.text == '⬅️ Назад':
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('🏃 Заберу сам', '🚗 Привезти')
                back.row('🏠 Начало', '⬅️ Назад')
                type_delivery = bot.send_message(message.chat.id,
                                                 f'Укажите вариант доставки\nНа данный момент: {p.delivery}',
                                                 reply_markup=back)
                bot.register_next_step_handler(type_delivery, choice_of_delivery)

            elif message.text == '🏠 Начало':
                bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
                startpg(message)
            elif message.text == 'Как можно скорее':
                p.time_delivery = 'Как можно скорее'
                p.save(update_fields=["time_delivery"])
                new_name = bot.send_message(chat_id=message.chat.id,
                                           text=f'Укажите ваше имя:\nСейчас:{p.nickname}',
                                           reply_markup=submenu())
                bot.register_next_step_handler(new_name, name_processing)
            else:
                new_time = re.match(r'(2[0-3]|[0-1]\d):[0-5]\d', message.text)
                if new_time is None:
                    time_delivery = bot.send_message(chat_id=message.chat.id,
                                                     text=f'Введите корректно время в формате(14:30)\n'
                                                          f'Сейчас:{p.delivery}')
                    bot.register_next_step_handler(time_delivery, processing_delivery)
                else:
                    p.time_delivery = new_time.group(0)
                    p.save(update_fields=["time_delivery"])
                    new_name = bot.send_message(chat_id=message.chat.id,
                                                text=f'Укажите ваше имя:\nСейчас:{p.nickname}',
                                                reply_markup=submenu())
                    bot.register_next_step_handler(new_name, name_processing)

        def name_processing(message):
            p = Users.objects.get(name=message.chat.id)
            with open('sum.json', 'r') as f:
                max_sum = json.load(f)
            if max_sum["max_sum"] > p.basket_sum:
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало', '🍴 Меню')
                bot.send_message(chat_id=message.chat.id, text=f'Минимальная сумма заказа {max_sum["max_sum"]} ₽. '
                                                               f'Закажите ещё что-нибудь /menu  ', reply_markup=back)
            elif message.text == '✅ Верно':
                if p.mobile is None:
                    back = types.ReplyKeyboardMarkup(True, False)
                    button_phone = types.KeyboardButton(text="Отправить мой номер телефона", request_contact=True)
                    back.add(button_phone)
                    back.row('🏠 Начало', '⬅️ Назад')
                    new_number = bot.send_message(chat_id=message.chat.id,
                                                  text=f'Укажите ваш мобильный телефон:\n Сейчас:не указан',
                                                  reply_markup=back)
                    bot.register_next_step_handler(new_number, phone_number)
                else:
                    new_number = bot.send_message(chat_id=message.chat.id,
                                                  text=f'Укажите ваш мобильный телефон:\n Сейчас:{p.mobile}',
                                                  reply_markup=keyboard_number())
                    bot.register_next_step_handler(new_number, phone_number)
            elif message.text == '⬅️ Назад':
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Верно')
                back.row('Как можно скорее')
                back.row('🏠 Начало', '⬅️ Назад')
                time_delivery = bot.send_message(chat_id=message.chat.id,
                                                 text=f'Укажите время доставки в формате(12:30)\n'
                                                      f'Сейчас: {p.time_delivery}',
                                                 reply_markup=back)
                bot.register_next_step_handler(time_delivery, processing_delivery)
            elif message.text == '🏠 Начало':
                bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
                startpg(message)
            elif message.text.isalpha() and len(message.text) < 30:
                p.nickname = message.text
                p.save(update_fields=["nickname"])
                if p.mobile is not None:
                    new_number = bot.send_message(chat_id=message.chat.id,
                                                  text=f'Укажите ваш мобильный телефон:\n Сейчас:{p.mobile}',
                                                  reply_markup=keyboard_number())
                    bot.register_next_step_handler(new_number, phone_number)
                else:
                    back = types.ReplyKeyboardMarkup(True, False)
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
            print(message.chat.id)
            p = Users.objects.get(name=message.chat.id)
            with open('sum.json', 'r') as f:
                max_sum = json.load(f)
            if max_sum["max_sum"] > p.basket_sum:
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало', '🍴 Меню')
                bot.send_message(chat_id=message.chat.id, text=f'Минимальная сумма заказа {max_sum["max_sum"]} ₽. '
                                                               f'Закажите ещё что-нибудь /menu  ', reply_markup=back)
            elif message.text == '✅ Верно':
                if p.delivery == '🚗 Привезти':  # сделать для заберу сам
                    if p.address == "" or p.address is None:
                        back = types.ReplyKeyboardMarkup(True, False)
                        back.row('🏠 Начало', '⬅️ Назад')
                        new_address = bot.send_message(chat_id=message.chat.id,
                                                       text=f'Укажите адрес доставки \n'
                                                            f'Улицу, дом, подъезд, квартиру и этаж:\n'
                                                            f'Сейчас:не указан',
                                                       reply_markup=back)
                    else:
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
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                               output_field=IntegerField()))
                    back = types.ReplyKeyboardMarkup(True, False)
                    back.row('✅ Подтвердить и отправить')
                    back.row('🏠 Начало', '⬅️ Назад')
                    ordering = bot.send_message(message.chat.id, f' *Данные заказа*: \n'
                                                                 f'Сумма заказа: {final_sum["sum"]} ₽\n'
                                                                 f'Покупатель: {p.nickname} \nТелефон: {p.mobile}\n'
                                                                 f'Доставка: {p.delivery}',
                                                reply_markup=back, parse_mode='markdown')
                    bot.register_next_step_handler(ordering, ordering_process)
            elif message.text == '⬅️ Назад':
                new_name = bot.send_message(chat_id=message.chat.id,
                                            text=f'Укажите ваше имя:\n Сейчас:{p.nickname}',
                                            reply_markup=submenu())
                bot.register_next_step_handler(new_name, name_processing)

            elif message.text == '🏠 Начало':
                bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
                startpg(message)
            elif message.contact is not None:
                p.mobile = message.contact.phone_number[1:]

                if p.delivery == '🚗 Привезти':
                    if p.address == '' or p.address is None:
                        back = types.ReplyKeyboardMarkup(True, False)
                        back.row('🏠 Начало', '⬅️ Назад')
                        new_address = bot.send_message(chat_id=message.chat.id,
                                                       text=f'Укажите адрес доставки \n'
                                                            f'Улицу, дом, подъезд, квартиру и этаж:\n'
                                                            f'Сейчас:не указан',
                                                       reply_markup=back)
                    else:
                        back = types.ReplyKeyboardMarkup(True, False)
                        back.row('✅ Верно')
                        back.row('🏠 Начало', '⬅️ Назад')
                        new_address = bot.send_message(chat_id=message.chat.id,
                                                       text=f'Укажите адрес доставки \n'
                                                            f' Улицу, дом, подъезд, квартиру и этаж:\n'
                                                            f' Сейчас:{p.address}',
                                                       reply_markup=submenu())

                    bot.register_next_step_handler(new_address, address_processing)
                else:
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                               output_field=IntegerField()))
                    back = types.ReplyKeyboardMarkup(True, False)
                    back.row('✅ Подтвердить и отправить')
                    back.row('🏠 Начало', '⬅️ Назад')
                    ordering = bot.send_message(message.chat.id, f'*Данные заказа:* \n'
                                                                 f'Сумма заказа: {final_sum["sum"]}₽\n'
                                                                 f'Покупатель: {p.nickname} \nТелефон: {p.mobile} \n'
                                                                 f'Доставка: {p.delivery}',
                                                reply_markup=back, parse_mode='markdown')
                    bot.register_next_step_handler(ordering, ordering_process)

            elif message.text.isdigit() and len(message.text) == 11 and message.text[0] == '7':
                p.mobile = message.text
                p.save(update_fields=["mobile"])
                if p.delivery == '🚗 Привезти':
                    if p.address == '' or p.address is None:
                        back = types.ReplyKeyboardMarkup(True, False)
                        back.row('🏠 Начало', '⬅️ Назад')
                        new_address = bot.send_message(chat_id=message.chat.id,
                                                       text=f'Укажите адрес доставки\n'
                                                            f'Улицу, дом, подъезд, квартиру и этаж:\n'
                                                            f'Сейчас:не указан',
                                                       reply_markup=back)
                    else:
                        new_address = bot.send_message(chat_id=message.chat.id,
                                                       text=f'Укажите адрес доставки\n'
                                                            f' Улицу, дом, подъезд, квартиру и этаж:\n'
                                                            f' Сейчас:{p.address}',
                                                       reply_markup=submenu())

                    bot.register_next_step_handler(new_address, address_processing)
                else:
                    final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                               output_field=IntegerField()))
                    back = types.ReplyKeyboardMarkup(True, False)
                    back.row('✅ Подтвердить и отправить')
                    back.row('🏠 Начало', '⬅️ Назад')
                    ordering = bot.send_message(message.chat.id, f'*Данные заказа:*\n'
                                                                 f'Сумма заказа: {final_sum["sum"]}₽\n'
                                                                 f'Покупатель: {p.nickname}\nТелефон: {p.mobile}\n'
                                                                 f'Доставка: {p.delivery}',
                                                reply_markup=back, parse_mode='markdown')
                    bot.register_next_step_handler(ordering, ordering_process)

            else:
                new_number = bot.send_message(message.chat.id, 'Введите корректно номер через 7')
                bot.register_next_step_handler(new_number, phone_number)

        def address_processing(message):
            p = Users.objects.get(name=message.chat.id)
            with open('sum.json', 'r') as f:
                max_sum = json.load(f)
            if max_sum["max_sum"] > p.basket_sum:
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('🏠 Начало', '🍴 Меню')
                bot.send_message(chat_id=message.chat.id, text=f'Минимальная сумма заказа {max_sum["max_sum"]} ₽. '
                                                               f'Закажите ещё что-нибудь /menu  ', reply_markup=back)
            elif message.text == '✅ Верно':
                final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                           output_field=IntegerField()))
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Подтвердить и отправить')
                back.row('🏠 Начало', '⬅️ Назад')
                ordering = bot.send_message(message.chat.id, f'*Данные заказа:*\nСумма заказа: {final_sum["sum"]}₽\n'
                                                             f'Покупатель: {p.nickname}\nТелефон: {p.mobile}\n'
                                                             f'Доставка: {p.delivery}\nАдрес: {p.address}\n',
                                            reply_markup=back, parse_mode='markdown')
                bot.register_next_step_handler(ordering, ordering_process)
            elif message.text == '⬅️ Назад':
                new_number = bot.send_message(chat_id=message.chat.id,
                                              text=f'Укажите ваш мобильный телефон:\nСейчас:{p.mobile}',
                                              reply_markup=keyboard_number())
                bot.register_next_step_handler(new_number, phone_number)

            elif message.text == '🏠 Начало':
                bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
                startpg(message)
            elif message.text[0] == "\'" or message.text.isdigit() or len(message.text) > 40:
                new_address = bot.send_message(chat_id=message.chat.id,
                                               text=f'Укажите корректно адрес доставки\n'
                                                    f'Улицу, дом, подъезд, квартиру и этаж:\n'
                                                    f'Сейчас:{p.address}',
                                               reply_markup=submenu())

                bot.register_next_step_handler(new_address, address_processing)
            else:
                final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                           output_field=IntegerField()))
                p.address = message.text
                p.save(update_fields=["address"])
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Подтвердить и отправить')
                back.row('🏠 Начало', '⬅️ Назад')
                ordering = bot.send_message(message.chat.id, f'*Данные заказа:*\nСумма заказа: {final_sum["sum"]}₽\n'
                                                             f'Покупатель: {p.nickname}\nТелефон: {p.mobile}\n'
                                                             f'Доставка: {p.delivery}\nАдрес: {p.address} \n',
                                            reply_markup=back, parse_mode='markdown')
                bot.register_next_step_handler(ordering, ordering_process)

        def ordering_process(message):
            p = Users.objects.get(name=message.chat.id)
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            if message.text == '✅ Подтвердить и отправить':
                p.basket_sum = 0
                p.save(update_fields=["basket_sum"])
                basket = p.basket_set.all()
                final_sum = p.basket_set.aggregate(sum=Sum(F('count') * F('price'),
                                                           output_field=IntegerField()))
                foods = ''
                for i in basket:
                    sum_food = i.count * i.price
                    foods += '{} - {}шт. = {} ₽\n'.format(i.name_product, i.count, sum_food)
                p.orders_set.create(amount_to_pay=final_sum['sum'], type_delivery=p.delivery,
                                    address_delivery=p.address, food=foods, time_delivery=p.time_delivery)
                bot.send_message(chat_id=Users.objects.get(id=1).name, text=f'❗️ *Вам пришел заказ*\n\n'
                                                                            f'👤 Данные покупателя:\n'
                                                                            f'{p.nickname}, {p.mobile}\n\n'
                                                                            f'📦 Доставка:\n{p.delivery}\n'
                                                                            f'Адрес: {p.address}\n'
                                                                            f'Время: {p.time_delivery}\n\n*---*\n'
                                                                            f'🛒  Товары:\n{foods}\n*---*\n'
                                                                            f'*💰 Сумма заказа {final_sum["sum"]} ₽*',
                                 parse_mode='markdown')
                p.basket_set.all().delete()
                bot.send_message(message.chat.id, 'Главное меню', reply_markup=startmenu())
            elif message.text == '⬅️ Назад':
                if p.delivery == '🚗 Привезти':
                    new_address = bot.send_message(chat_id=message.chat.id,
                                                   text=f'Укажите адрес доставки\n'
                                                        f'Улицу, дом, подъезд, квартиру и этаж:\n'
                                                        f'Сейчас:{p.address}',
                                                   reply_markup=submenu())
                    bot.register_next_step_handler(new_address, address_processing)
                else:
                    new_number = bot.send_message(chat_id=message.chat.id,
                                                  text=f'Укажите ваш мобильный телефон:\nСейчас:{p.mobile}',
                                                  reply_markup=keyboard_number())
                    bot.register_next_step_handler(new_number, phone_number)

            elif message.text == '🏠 Начало':
                bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
                startpg(message)

            else:
                back = types.ReplyKeyboardMarkup(True, False)
                back.row('✅ Подтвердить и отправить')
                back.row('🏠 Начало', '⬅️ Назад')
                error = bot.send_message(chat_id=message.chat.id,
                                         text='Выбирите одну из кнопок для дальнейшего действия',
                                         reply_markup=back)
                bot.register_next_step_handler(error, ordering_process)



        bot.polling(none_stop=True)
