# !/usr/bin/env python3


import telebot  # чтобы работал telebot - удалить telebot, и установить Pytelegrambotapi, написанным оставить telebot
from telebot.types import InlineKeyboardMarkup
import baza
from telebot import types
from random import choice
import exception_logger
import handler_db
import settings
import dict_users
import getplan
import getnalet
import check_plan
import threading
import time
import get_permissions
import traceback
import flight_counter
import check_news

bot = telebot.TeleBot(settings.TOKEN)
bot.send_message(157758328, f"бот перезапущен")

list_id = handler_db.list_user_id()


## -*- coding: utf8 -*-

def general_menu():
    """Основаня клавиатура внизу экрана"""
    general_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton('План работ')
    btn2 = types.KeyboardButton('Мой налет')
    btn3 = types.KeyboardButton('Расчётный лист')
    btn4 = types.KeyboardButton('Новости')
    btn5 = types.KeyboardButton('Добавить  информацию')
    btn6 = types.KeyboardButton('Обратная связь')  # InlineKeyBoard (callback_data='Внести информацию')
    general_menu.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return general_menu


def survey(user_id):
    """Вопрос про часовые пояса. Все три вопроса грузятся сразу. Вызов функции прикрепляется в качестве параметра к reply_markup в bot.send_message"""
    hours_btns = types.InlineKeyboardMarkup(row_width=1)
    one = types.InlineKeyboardButton(text="1 - Вылет UTC, Прилёт МСК", callback_data="one")
    two = types.InlineKeyboardButton(text="2 - Вылет МСК, Прилёт МСК", callback_data="two")
    hours_btns.add(one, two)

    confirm_plan_btns = types.InlineKeyboardMarkup(row_width=1)
    confirm = types.InlineKeyboardButton(text="Подтверждать план автоматически", callback_data="confirm")
    not_confirm = types.InlineKeyboardButton(text="Не подтверждать план автоматически", callback_data="not_confirm")
    confirm_plan_btns.add(confirm, not_confirm)

    day_nights_btns = types.InlineKeyboardMarkup(row_width=1)
    yes = types.InlineKeyboardButton(text="Да, ночью разрешить", callback_data="yes")
    no = types.InlineKeyboardButton(text="Нет, только днём", callback_data="no")
    day_nights_btns.add(yes, no)

    bot.send_message(user_id,
                     f"`\t\t {dict_users.users[user_id]['name']}, укажите часовые пояса, в которых Вам было бы удобно получать план работ: UTC или MSK",
                     reply_markup=hours_btns)

    bot.send_message(user_id,
                     f"`\t\t {dict_users.users[user_id]['name']} подтверждать ли план работ в OpenSky автоматически при отправке уведомления Вам в Telegram?",
                     reply_markup=confirm_plan_btns)

    bot.send_message(user_id,
                     f"`\t\t Хотите ли Вы получать уведомления с планом работ в ночное время с 00:00 до 7:00?",
                     reply_markup=day_nights_btns)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """Всего лишь Обработчик опроса, который сообщает разработчику результаты индивидуальных ответов пользоателя."""
    if call.message:
        if call.data == "one":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="План работ Вам будет высылаться в указанных часовых поясах: вылет по UTC, прилёт по МСК.")
            bot.send_message(157758328, f"{call.message.chat.id} {dict_users.users[call.message.chat.id]['surname']} "
                                        f"Ответил, номер один: UTC МСК")
        if call.data == "two":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="План работ Вам будет высылаться в указанных часовых поясах: вылет и прилёт по МСК.")
            bot.send_message(157758328, f"{call.message.chat.id} {dict_users.users[call.message.chat.id]['surname']} "
                                        f"Попросил номер два: МСК МСК")
        if call.data == "confirm":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Ваш план работ будет подтверждаться автоматически при отправке его Вам в Telegram.")
            bot.send_message(157758328, f"{call.message.chat.id} {dict_users.users[call.message.chat.id]['surname']} "
                                        f"Попросил подтверждать план работ")
        if call.data == "not_confirm":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Ваш план работ не будет подтверждаться автоматически при отправке его Вам в Telegram.")
            bot.send_message(157758328, f"{call.message.chat.id} {dict_users.users[call.message.chat.id]['surname']} "
                                        f"Попросил не подтверждать план работ")
        if call.data == "yes":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Отправка уведомлений по ночам разрешена.")
            bot.send_message(157758328, f"{call.message.chat.id} {dict_users.users[call.message.chat.id]['surname']} "
                                        f"ночью присылать уведомления можно")
        if call.data == "no":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Отправка уведомлений по ночам запрещена.")
            bot.send_message(157758328, f"{call.message.chat.id} {dict_users.users[call.message.chat.id]['surname']} "
                                        f"пользователь не хочет ночью получать уведомления ночью")


check_plan = threading.Thread(target=check_plan.cycle_plan_notify)  # TODO закомментирвоать
check_plan.start()
if not check_plan.is_alive():
    bot.send_message(157758328, f'поток проверки планов умер')
    check_plan.start()
    exc_event = exception_logger.writer(exc="поток проверки планов умер", request=None, user_id=None, fio=None,
                                        answer=None)
    bot.send_message(157758328, exc_event)


def check_permissions_for_everyone():
    """Проверяет допуски у всех бортпроводников"""
    document_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
    btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                     url='https://edu.rossiya-airlines.com/ready/userReady-1/')
    document_btn.add(btn)
    bot.send_message(157758328, f'Бот начал проверку допусков всех проводников.')
    counter = 0

    for user_id in list_id:
        user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, autoconfirm = handler_db.fetch_user_for_plan(
            user_id)
        fio = f'{user_id} {surname} {name} '
        if password == '' or not password or password == '0':  # TODO сделать в базе всем одинаково
            continue
        else:
            try:
                documents_info = get_permissions.parser(user_id, tab_number, password, name)
                bot.send_message(user_id, documents_info, reply_markup=document_btn)
                bot.send_message(157758328, f'Пользователю {fio} отправлен сообщение об истекающих допусках.')
                # bot.send_message(157758328, documents_info, reply_markup=document_btn)  # TODO закомментировать
                counter += 1
                time.sleep(3)
            except Exception:
                bot.send_message(157758328, f'{fio} не удалось уведомление о допусках: {traceback.format_exc()}')
                continue
    bot.send_message(157758328, f"бот закончил проверку допусков всех проводников. Отправлено {counter} уведомлений.")


def check_nalet_for_everyone():
    """Проверяет налет у всех бортпроводников"""
    nalet_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
    btn = types.InlineKeyboardButton(text="Просмотреть налёт в OpenSky",
                                     url='https://edu.rossiya-airlines.com/nalet/')
    nalet_btn.add(btn)
    bot.send_message(157758328, f'Бот начал проверку налёта всех проводников.')
    counter = 0

    for user_id in list_id:
        user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, autoconfirm = handler_db.fetch_user_for_plan(
            user_id)
        fio = f'{user_id} {surname} {name} '
        if password == '' or not password or password == '0':  # TODO сделать в базе всем одинаково
            continue
        else:
            try:
                nalet_info = getnalet.parser(user_id, tab_number, password)
                bot.send_message(user_id, f'{name}, у Вас в этом месяце\n{nalet_info}', reply_markup=nalet_btn)
                bot.send_message(157758328, f'Пользователю {fio} отправлен налёт.')
                counter += 1
                time.sleep(3)
            except Exception:
                bot.send_message(157758328, f'{fio} не удалось отправить налёт: {traceback.format_exc()}')
                continue
    bot.send_message(157758328, f"бот закончил проверку налёта всех проводников. Отправлено {counter} уведомлений.")


def check_new_documents(user_id):
    """Проверяет выложены ли новые документы в OpenSky"""
    document_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
    btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                     url='https://edu.rossiya-airlines.com/')
    document_btn.add(btn)

    for user_id in list_id:
        user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, autoconfirm = handler_db.fetch_user_for_plan(
            user_id)
        fio = f'{user_id} {surname} {name} '

        if password == '' or not password or password == '0':  # TODO сделать в базе всем одинаково
            continue
        try:
            new_document = check_news.parser(tab_number, password)
            if new_document is not None:
                bot.send_message(user_id, new_document, reply_markup=document_btn)  # TODO закомментировать
        except Exception:
            bot.send_message(157758328,
                             f'{fio} не удалось отправить сообщение о новых документах, произошла ошибка: {traceback.format_exc()}')


def messaging_process(message):
    """При принудительном вызове функции рассылает всем сообщения со скоростью 1 человек в 3 секунды"""
    mess = message.text.split()
    counter_users = 0
    for user_id in list_id:
        user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, autoconfirm = handler_db.fetch_user_for_plan(
            user_id)
        fio = f'{user_id} {name} {surname}'
        if messaging:
            try:
                bot.send_message(user_id, f'{name}, {" ".join(mess[2:])}', reply_markup=general_menu())
                counter_users += 1
                bot.send_message(157758328, f"Сообщение успешно отравлено {fio}")  # TODO временно
                time.sleep(3)
            except Exception as exc:  # если случилась ошибка при отправке сообщений пользователю
                exc_event = exception_logger.writer(exc=exc, request='рассылка сообщений пользователям',
                                                    user_id=user_id, fio=fio,
                                                    answer='сообщение не удалось отправить ')
                bot.send_message(157758328, exc_event)
                bot.send_message(157758328,
                                 f"сообщение не удалось отправить {fio} ошибка {exc}.")  # TODO временно
    bot.send_message(157758328,
                     f"всего разослано {counter_users} чел. из {len(dict_users.users)} чел.")  # TODO временно
    return


def write_new_dict_user(message):  # TODO почему стирает весь файл?
    """Предоставление доступа пользователю: внесение новго пользователя в словарь непосредлственно сразу через чат телеграм-бота.
    пример текста поступающей команды: предоставить доступ 157758328 Азаров Дмитрий 119221"""
    try:
        mess = message.text.split('\n')
        user_id = mess[1]  # 0 - предоставить доступ, 1 - user_id, 2 - surname
        surname = mess[2]
        name = mess[3]
        city = mess[4]
        link = mess[5]
        exp_date = mess[6]
        tab_number = mess[7]
        password = mess[8]
        messaging = mess[9]
        check_permissions = mess[10]
        autoconfirm = mess[11]
        handler_db.add_new_user_to_db_users(user_id, surname, name, city, link, exp_date, tab_number, password,
                                            messaging, check_permissions, autoconfirm)
        result = handler_db.select(user_id)
        user_id_from_db = result.split()[0]
        name_from_db = result.split()[2]
        if user_id == user_id_from_db and name == name_from_db:
            bot.send_message(user_id,
                             f'{name_from_db}, Вам успешно предоставлен доступ к телеграм-боту. '
                             f'Спрашивайте, буду рад помочь! Если хотите получать уведомления на телефон об изменениях в '
                             f'плане работ, то пришлите в ответном одном сообщении через пробел логин и пароль от '
                             f'OpenSky (4 слова через пробел) по следующему шаблону: логин ....... пароль ......',
                             reply_markup=general_menu())
            bot.send_message(157758328, "Сообщение о предоставлении доступа пользователю отправлено успешно.")
            return
        else:
            bot.send_message(157758328, "Проблема с добавлением пользователя в general.db")
            bot.send_message(157758328, f"последние внесенные пользвоатели в базе данных:")
            last_three_users_in_db = handler_db.get_three_last()
            for i in last_three_users_in_db:
                bot.send_message(157758328, i[2])

    except Exception as exc:
        exc_event = exception_logger.writer(exc=exc,
                                            request='Внесение нового пользователя в словарь удаленно через диалог',
                                            user_id=user_id,
                                            answer='произошла ошибка при предоставлении доступа. Словарь пользователей стерся полностью.')
        bot.send_message(157758328, exc_event)
        bot.send_message(157758328, f"произошла ошибка при предоставлении доступа {exc}.")
        return


def service_notification(message):
    """Уведомление на случай проведения технических работ на сервере."""
    bot.send_message(message.chat.id, 'На сервере проводятся технические работы. Возможна некорретная работа '
                                      'телеграм-бота. Это продлится недолго. Приносим свои извинения за доставленные '
                                      'неудобства.')
    bot.send_message(157758328, f"Отправлено уведомление о некорректной работе телеграм-бота.")


def verification(message):
    """Верифицирует пользователя каждый раз: проверяет есть ли у него одобренный доступ к телеграм-боту."""
    if message.chat.id in dict_users.blocked.keys():
        bot.send_message(message.chat.id, 'Вам отказано в доступе.')
        bot.send_message(157758328,
                         f"Отказали в доступе {message.from_user.id} @{message.from_user.username} {message.from_user.first_name} "
                         f"{message.from_user.last_name} Пользователь спрашивал {message.text}")
        return False
    if handler_db.check_access(message.chat.id):
        return True
    else:
        bot.send_message(message.chat.id,
                         'Прошу Вас пройти верификацию, для этого Вам необходимо отправить сюда фото своего штабного '
                         'пропуска. Нам необходимо убедиться, что Вы летающий '
                         'бортпроводник АК "Россия". На время ожидания доступ временно ограничен.')
        bot.send_message(157758328,
                         f"Запросили фото айдишки для верификации от пользователя id {message.from_user.id} @{message.from_user.username} {message.from_user.first_name} "
                         f"{message.from_user.last_name} Пользователь спрашивал {message.text}")
        return False


@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    """пересылает разработчику картинку отправленную пользователем. Сделано для верификации по айдишке"""
    bot.send_photo(157758328, message.photo[0].file_id)
    new_photo_notification = "Пользователь {0.first_name} {0.last_name} @{0.username} id {0.id} прислал " \
                             "фото.".format(message.from_user, message.from_user, message.from_user,
                                            message.from_user)
    bot.send_message(157758328, new_photo_notification)
    bot.send_message(message.chat.id,
                     "Фото отправлено успешно. Пожалуйста, ожидайте, о результате мы Вам сообщим. Ожидание может составить до суток.")


@bot.message_handler(commands=['start'])
def welcome(message):
    """При первом подключении пользователя к боту - выводит приветсвенный стикер, приветсвенную речь. Также в этой
    функции обозначены кнопки, которые будут всегда отображаться под полем ввода запроса."""
    # service_notification(message)

    with open('static/AnimatedSticker.tgs', 'rb') as sti:
        bot.send_sticker(message.chat.id, sti)

    bot.send_message(message.chat.id,
                     '\t Привет!\n'
                     '\t Я робот, призванный отвечать на вопросы бортпроводников: '
                     'вопросы к МКК и КПК, справки, часы работы, телефоны, представители разных служб и в разных городах, '
                     'настройки почты, названия самолетов по бортовым номерам, особенности рейсов, какой сейчас рацион, '
                     'расшифровки аббревиатур и сокращений, ответы на тесты, как закрыть больничный, инструктажи, команды, '
                     'высылаю уведомления о предстоящем плане работ и т.д. И разработчик '
                     'ждёт ваших предложений и идей, участвуйте в развитии приложения №1 для бортпроводников АК "Россия"!\n'
                     '\t Вопросы задавать лучше коротко.'
                     .format(message.from_user, bot.get_me()), reply_markup=general_menu())
    new_user_notification = "Пользователь {0.first_name} {0.last_name} @{0.username} id {0.id} подключился к телеграм-боту." \
        .format(message.from_user, message.from_user, message.from_user,
                message.from_user)
    bot.send_message(157758328, new_user_notification)

    if not verification(message):
        return


def find(question, user_request):
    """Выявляет степень максимального соответсвия искомых слов запросу в каждом результате: считает количество совпавших
    слов и возвращает счетчик."""
    count = 0
    for word in user_request:
        if word in question:
            count += 1
    return count


@bot.message_handler(content_types=["text"])  #
def conversation(message):
    """Модуль для общения и взаимодействия с пользователем. Декоратор будет вызываться когда боту напишут текст."""
    if not verification(message):
        return

    try:
        user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, autoconfirm = \
            handler_db.fetch_user_for_plan(message.chat.id)
        fio = f'{user_id} {name} {surname}'
    except Exception as exc:
        bot.send_message(157758328, f"Поймали ошибку при извлечении данных пользователя из базы: {message.chat.id} \n"
                                    f"при запросе: {message.text}: {exc}")

    def photo():
        """Отправляет пользовтелю информацию с фото"""
        try:  # TODO временный try except посмотреть почему падает в этом месте
            pic = baza.dictionary[id].get('photo')
            bot.send_message(user_id, baza.dictionary[id].get('answer'), parse_mode='Markdown')
            with open(pic, 'rb') as f:
                bot.send_photo(user_id, f)
        except Exception as exc:
            bot.send_message(157758328,
                             f"Ошибка при отправке изображения из функции photo() при запросе {message.text}: {exc}")
        bot.send_message(157758328, "Выдали фото по запросу: " + message.text)

    def open_link():
        """Предлагает открыть сайт"""
        download_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
        btn = types.InlineKeyboardButton(text="ОТКРЫТЬ", url=baza.dictionary[id]['link'])  # .get() здесь не позволяет
        download_btn.add(btn)
        bot.send_message(user_id, baza.dictionary[id].get('answer'), parse_mode='Markdown',
                         reply_markup=download_btn)
        bot.send_message(157758328, f"Пользователю {fio} предложили ОТКРЫТЬ: {message.text}")

    def download():
        """Предлагает скачать файл"""
        download_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="СКАЧАТЬ", url=baza.dictionary[id][
            'link'])  # TODO возникает ошибка в кнопку нельзя передавать содержание ключа 'link' ссылку методом .get('link') [id]['link'] возникает ошибка
        download_btn.add(btn)
        bot.send_message(user_id, baza.dictionary[id].get('answer'), parse_mode='Markdown',
                         reply_markup=download_btn)
        bot.send_message(157758328, f"Пользователю {fio} предложили СКАЧАТЬ: {message.text}")

    def changed(text):
        """Видоизменяет текст поступающего запроса от пользователя и искомого текста в базе для успешного поиска:
        переводит регистр всех букв в нижний, у каждого слова убирает окончание."""
        lower_text_without_ends = [word[:-2].lower() for word in text.split()]
        return ' '.join(lower_text_without_ends)

    def find_exception(message):
        """все запросы от пользователя сначала прогоняет через словарь исключений, если функция находит его там, то
        заменяет его на такое же развернутое значение, которое следует использовать при дальнейшем поиске. ищет слова
        для преобразования чтобы обойти минимально допустимое разрешение на длину слова"""
        for word in message.split(' '):
            for id in baza.exceptions:
                if word == baza.exceptions[id]['word']:
                    changed_word = baza.exceptions[id]['changed_word']
                    message = message.replace(word, changed_word)
                    return message
        return message

    def find_punctuation(message):
        """Ищет знаки пунктуации"""
        for m in baza.punctuation:  # message.lower().split():  # для каждого слова в кортеже
            if m in message:  # если это каждое слово есть в запросе
                message = message.replace(m, '')
        return message

    def find_garbage(message):
        """Ищет лишние слова-сорняки, которые вешают программу (как, кто, где) и меняет их на пустую строку"""
        for word in message.lower().split():  # для каждого слова в кортеже
            if word.lower() in baza.garbage:  # если это каждое слово есть в запросе
                message = message.replace(word, '')
        return message

    def find_non_strict_accordance(message):
        """2 - Ищет не в строгом соответсвии."""
        if 4 <= len(message.text) <= 5:
            bot.send_message(user_id, "Пожалуйста, уточните свой вопрос", reply_markup=general_menu(),
                             parse_mode='Markdown')
            bot.send_message(user_id, f'2.1 Пользователя {fio} попросили уточнить вопрос {message.text}')
            found_result = True
            return found_result
        else:
            for id in baza.dictionary:
                question = baza.dictionary[id]['question'].lower()
                if changed(message.text) in changed(question):
                    if 'скачать' in baza.dictionary[id]['question'].lower():  # так надо 2 раза
                        download()
                    elif 'просмотреть' in question:  # так надо 2 раза
                        open_link()
                    elif 'изображение' in question:  # так надо 2 раза
                        photo()
                    else:  # так надо 2 раза
                        bot.send_message(user_id, baza.dictionary[id]['answer'], reply_markup=general_menu(),
                                         parse_mode='Markdown')
                        bot.send_message(157758328, f"2.1 - Пользователю {fio} выдан ответ не в строгом соответсвии "
                                                    f"по запросу:\n{message.text}")
                    found_result = True
                    return found_result

    def find_non_strict_accordance_2(message):
        """2 - Ищет не в строгом соответсвии."""
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            if changed(message.text) in changed(question):
                if 'скачать' in baza.dictionary[id]['question'].lower():  # так надо 2 раза
                    download()
                elif 'просмотреть' in question:  # так надо 2 раза
                    open_link()
                elif 'изображение' in question:  # так надо 2 раза
                    photo()
                else:  # так надо 2 раза
                    bot.send_message(user_id, baza.dictionary[id]['answer'], reply_markup=general_menu(),
                                     parse_mode='Markdown')
                    bot.send_message(157758328,
                                     f"2.2 - Пользователю {fio} выдан ответ не в строгом соответсвии по запросу:\n{message.text}")
                found_result = True  # в таком положении не ищет в следующем случайном порядке ставит что всё найдено уже но ищет много с отсеченными окончаниями коктейли
                return found_result

    def find_in_fullform_random_order(message):
        # TODO Добавить сюда скачать просмотреть изображение
        """3.1 - Ищет в случайном порядке без отсеченных окончаний."""
        global question
        user_request = message.text.split()
        max_of_found_words = 0  # в max <- записывается matches <- записывается find(вычисляется количество совпадений слов)
        results = []
        link = None
        photo = None
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            matches = find(question, user_request)
            # в matches сохраняется число соответсвий слов запроса вопросу в базе для каждого id мы проверяем кол-во соотв-х слов
            if matches == max_of_found_words and matches != 0:  # если количество соответсвий равно максимум
                results.append(baza.dictionary[id].get('answer'))
            if matches > max_of_found_words:  # если соответсвий нашли еще больше итогового счетчика максимума
                results.clear()  # очищаем список результатов
                max_of_found_words = matches  # в максимум записываем новую цифру соответсвия
                results.append(baza.dictionary[id].get('answer'))
                if 'скачать' in question or 'просмотреть' in question:  # так надо 2 раза
                    link = baza.dictionary[id].get('link')
                else:
                    link = None
                if 'изображение' in question:  # так надо 2 раза
                    photo = baza.dictionary[id].get('photo')
                else:
                    photo = None

        if len(results) < 8:  # выдает ответы при оптимальном количстве результатов
            for each_answer in results:  # TODO не прикрепляет кнопки к ответу, если выдается ответ в случайном порядке
                if link:
                    open_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
                    btn = types.InlineKeyboardButton(text="ОТКРЫТЬ", url=link)
                    open_btn.add(btn)
                    bot.send_message(user_id, each_answer, parse_mode='Markdown',
                                     reply_markup=open_btn)
                    found_result = True
                    photo = None
                if photo:
                    photo()
                    found_result = True
                if link is None:
                    bot.send_message(user_id, each_answer, reply_markup=general_menu(), parse_mode='Markdown')
                    found_result = True

                bot.send_message(157758328,
                                 f"3.1 - Пользователю {fio} выдан ответ в случайном порядке по запросу:\n{message.text}")
                return found_result

    def find_in_random_order(message):
        # TODO Добавить сюда скачать просмотреть изображение
        """Ищет в случайном полрядке с отсеченными окончаниями."""
        global question
        changed_user_request = changed(message.text).split()
        max_of_found_words = 0  # в max <- записывается matches <- записывается find(вычисляется количество совпадений слов)
        results = []
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            matches = find(question, changed_user_request)
            # в matches сохраняется число соответсвий слов запроса вопросу в базе для каждого id мы проверяем кол-во соотв-х слов
            if matches == max_of_found_words and matches != 0:  # если количество соответсвий равно максимум
                results.append(baza.dictionary[id].get('answer'))
            if matches > max_of_found_words:  # если соответсвий нашли еще больше итогового счетчика максимума
                results.clear()  # очищаем список результатов
                max_of_found_words = matches  # в максимум записываем новую цифру соответсвия
                results.append(baza.dictionary[id].get('answer'))
                link = baza.dictionary[id].get('link')  # в результаты добавляем answer

        if len(results) < 8:  # выдает ответы при оптимальном количстве результатов
            for each_answer in results:  # TODO не прикрепляет кнопки к ответу, если выдается ответ в случайном порядке

                bot.send_message(user_id, each_answer, reply_markup=general_menu(), parse_mode='Markdown')
                if link:
                    bot.send_message(user_id, link, reply_markup=general_menu(), parse_mode='Markdown')
                found_result = True
                bot.send_message(157758328, f"3.2 - Пользователю {fio} выдан ответ в случайном порядке c отсчением "
                                            f"окончаний по запросу:\n{message.text}")
                return found_result

    def find_in_answers(message):
        """Ищет в случайном порядке с отсеченными окончаниями."""
        global question
        changed_user_request = changed(message.text).split()
        max_of_found_words = 0  # в max <- записывается matches <- записывается find(вычисляется количество совпадений слов)
        results = []
        for id in baza.dictionary:
            answer = baza.dictionary[id]['answer'].lower()
            matches = find(answer, changed_user_request)
            # в matches сохраняется число соответсвий слов запроса вопросу в базе для каждого id мы проверяем кол-во соотв-х слов
            if matches == max_of_found_words and matches != 0:  # если количество соответсвий равно максимум
                results.append(baza.dictionary[id].get('answer'))
            if matches > max_of_found_words:  # если соответсвий нашли еще больше итогового счетчика максимума
                results.clear()  # очищаем список результатов
                max_of_found_words = matches  # в максимум записываем новую цифру соответсвия
                results.append(baza.dictionary[id].get('answer'))
                link = baza.dictionary[id].get('link')  # в результаты добавляем answer

        if len(results) < 8:  # выдает ответы при оптимальном количстве результатов
            for each_answer in results:  # TODO не прикрепляет кнопки к ответу, если выдается ответ в случайном порядке

                bot.send_message(user_id, each_answer, reply_markup=general_menu(), parse_mode='Markdown')
                if link:
                    bot.send_message(user_id, link, reply_markup=general_menu(), parse_mode='Markdown')
                found_result = True
                bot.send_message(157758328, f"4 -{fio} При поиске по ответам, пользователю выдан ответ в случайном "
                                            f"порядке c отсчением окончаний по запросу:\n{message.text}")
                return found_result
        if len(results) >= 8:
            bot.send_message(message.chat.id, f"{name}, Найдено слишком много ответов. Уточните свой вопрос.")
            bot.send_message(157758328, f"4 - Пользователю {fio} выдан ответ, что найдено слишком много ответов при "
                                        f"запросе:\n{message.text}")

    def confirm_question(message):
        """Сообщение с кнопками для отмены подтверждения плана работ, либо оставить всё как есть."""
        confirm_btns = types.InlineKeyboardMarkup()
        yes_off = types.InlineKeyboardButton(text="Да, отключить", callback_data="not_confirm")
        no_on = types.InlineKeyboardButton(text="Нет, подтверждать", callback_data="confirm")
        confirm_btns.add(yes_off, no_on)

        if autoconfirm:
            bot.send_message(user_id,
                             f"`\t\t {name}, cейчас у Вас план работ "
                             f"подтверждается автоматически. Вы хотите отключить подтверждение ознакомления "
                             f"с планом работ?", reply_markup=confirm_btns)

    def check_permissions(user_id):
        """Проверяет сроки дейсвтвия допусков у одного конкретного проводника по индивидуальному запросу."""
        document_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
        btn = types.InlineKeyboardButton(text="Открыть допуски в OpenSky",
                                         url='https://edu.rossiya-airlines.com/ready/userReady-1/')
        document_btn.add(btn)
        if password == '':
            bot.send_message(user_id,
                             "К сожалению, я не могу проверить сроки действия Ваших документов и допусков, т.к. "
                             "в моей базе нет Вашего логина и пароля от OpenSky. Если Вы не хотите пропустить "
                             "сроки дейтсивя документов и вовремя получить уведомление на телефон, пришлите в "
                             "ответном одном сообщении 4 слова через пробел по шаблону: логин ...... пароль "
                             "........ А пока рекомендую вам самостоятельно перейти в раздел документов и "
                             "проверить сроки там.", reply_markup=document_btn)
        else:
            try:
                documents_info = get_permissions.parser(user_id, tab_number, name, surname)
                bot.send_message(user_id, documents_info, reply_markup=document_btn)
                bot.send_message(user_id, f'Пользователю {fio} отправлено сообщение об истекающих допусках.',
                                 reply_markup=document_btn)
            except Exception:
                bot.send_message(user_id,
                                 f'Пользователю {fio} не удалось отправить сообщение об истекающих допусках, произошла ошибка: {traceback.format_exc()}',
                                 reply_markup=document_btn)
        return

    found_result = False

    # global user_id
    # service_notification(message)

    if "написать по id" in message.text.lower():
        mess = message.text.split()
        try:
            bot.send_message(int(mess[3]), ' '.join(mess[5:]).capitalize(), reply_markup=general_menu())
            bot.send_message(157758328, "Сообщение пользователю отправлено успешно.")
        except Exception:
            bot.send_message(157758328, f"Пользователь не подключен к телеграм-боту.\n {traceback.format_exc()}")
        return

    if message.text.lower() in ['сколько рейсов', '/flight_counter', 'счетчик рейсов', "счётчик рейсов",
                                "сколько рейсов на сухом", "посчитать рейсы"]:
        if password == '' or not password or password == '0':
            bot.send_message(user_id,
                             "К сожалению, я не могу посчитать сколько рейсов вы отлетали, т.к. в моей базе нет Вашего логина и пароля. Если Вы хотите чтобы я за вас легко и просто посчитал количество рейсов, пришлите мне в ответном одном сообщении 4 слова через пробел по шаблону: логин ...... пароль ........")
        else:
            bot.send_message(user_id, "Уже считаю Ваши рейсы. Пожалуйста, подождите...")
            result = flight_counter.parser(user_id, tab_number, password)
            bot.send_message(user_id, result, reply_markup=general_menu())
            bot.send_message(157758328, f"Пользователю {fio} отправлен счетчик рейсов",
                             reply_markup=general_menu())
            found_result = True
        return found_result

    if message.text.lower() in 'это не нормально это ужасно это очень плохо очень жаль кошмар охренеть':
        bot.send_message(user_id, f"Ну, что поделать, {name}... Я тебя прекрасно понимаю.")
        bot.send_message(157758328, f"{fio} отправили сочувствие в ответ на {message.text}.")
        return

    if message.text.lower() in "обратная связь /feedback":
        def feedback(message):
            if "отмена" in message.text.lower():
                bot.send_message(user_id,
                                 f"Если надумаете в следующий раз что-то мне сообщить - буду рад узнать.")
                bot.send_message(157758328, f"{fio} передумал оставлять обратную связь.")
            else:
                bot.send_message(157758328, f"{fio} оставил обратную связь: \n {message.text}")

        text = f"{name}, если у Вас есть какие-то замечания, предложения, выявили факты некорректной работы бота, либо у " \
               f"Вас есть какой-то вопрос или просто что-то сообщить - пожалуйста, отправьте мне обратную связь в " \
               f"ответном сообщении. Телеграм-бот ждет вашего сообщения. Если Вы передумали оставлять обратную связь, " \
               f"отправьте слово отмена."
        msg = bot.send_message(user_id, text)
        bot.register_next_step_handler(msg, feedback)
        return

    if message.text.lower() in "план на завтра план работ /getplan мой наряд":
        if password == '' or not password or password == '0':
            plan_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
            btn = types.InlineKeyboardButton(text="Открыть план работ в OpenSky",
                                             url='https://edu.rossiya-airlines.com/workplan/')
            plan_btn.add(btn)
            bot.send_message(user_id,
                             f'{name}, Ваш логин и пароль от OpenSky отсутсвует в моей базе данных, поэтому я '
                             'не могу запросить ваш план работ и выдать его напрямую сюда. Если Вы '
                             'хотите легко и быстро узнавать свой план работ, а в будущем получать '
                             'уведомления на телефон о новых рейсах - сообщите мне свой логин и пароль '
                             'через пробел в следующем формате: \n логин ...... пароль ...... \n '
                             '(4 слова через пробел, вместо многоточия ваш логин и пароль).',
                             reply_markup=plan_btn)
            return
        else:
            bot.send_message(user_id, f"{name}, запрос отправлен. Ожидайте несколько секунд...")
            plan = getplan.parser(user_id, tab_number, password, autoconfirm)
            plan_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
            btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                             url='https://edu.rossiya-airlines.com/workplan/')
            plan_btn.add(btn)
            bot.send_message(user_id, plan, reply_markup=plan_btn, parse_mode='html')
            bot.send_message(157758328, plan, parse_mode='html')
            bot.send_message(157758328, f"{fio} получил план работ по индивидуальному запросу")
            return

    if '/plan' in message.text.lower():  # TODO сделать потом чтобы автоматически менял статус в словаре
        if password == '':
            bot.send_message(user_id, 'Вам не приходят автоматические уведомление о предстоящем плане работ, '
                                      'так как Вы ранее не сообщили свой логин и пароль от OpenSky. Чтобы получать '
                                      'уведомления о предстоящем плане работ, Вам неообходимо сообщить свой логин и '
                                      'пароль в сообщении по следующему шаблону: логин ...... пароль ........ '
                                      '(4 слова через пробел в одну строку)')
        if len(password) > 0 and plan_notify:
            bot.send_message(message.chat.id,
                             'Хорошо, будет сделано. Чуть позже уведомления о предстоящем плане работ у '
                             'вас будут отключены.')
            bot.send_message(157758328, f'{fio} попросил отключить уведомления о плане работ')
        if len(password) > 0 and not dict_users.users[message.chat.id]['plan_notify']:
            bot.send_message(message.chat.id, 'Хорошо, будет сделано. Чуть позже мы включим уведомления о предстоящем '
                                              'плане работ.')
            bot.send_message(157758328, f'{fio} попросил включить уведомления о плане работ')
        return

    if message.text.lower() in "мой налет сейчас налёт /nalet":
        if password == '':
            nalet_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
            btn = types.InlineKeyboardButton(text="Просмотреть налёт в OpenSky",
                                             url='https://edu.rossiya-airlines.com/nalet/')
            nalet_btn.add(btn)
            bot.send_message(user_id,
                             'Ваш логин и пароль от OpenSky отсутсвует в моей базе данных, поэтому я не могу запросить '
                             'ваш налёт и выдать его напрямую сюда в чат. Если вы хотите легко и быстро узнавать свой '
                             'налёт - в ответном сообщении отправьте свой логин и пароль через пробел в следующем '
                             'формате: \n логин ...... пароль ...... \n (вместо многоточия ваш логин и пароль - 4 слова через пробел). \n '
                             'Поэтому пока предлагаю нажать на кнопку, перейти и самостоятельно просмотреть Ваш налёт, '
                             'ввести логин и пароль туда вручную.', reply_markup=nalet_btn)
            return
        else:
            bot.send_message(user_id, f"{name}, уже считаю Ваш налёт. Пожалуйста, подождите...")
            nalet = getnalet.parser(user_id, tab_number, password)
            nalet_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
            btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                             url='https://edu.rossiya-airlines.com/nalet/')
            nalet_btn.add(btn)
            bot.send_message(user_id, nalet, reply_markup=nalet_btn, parse_mode='Markdown')
            bot.send_message(157758328, f"Пользователю {fio} выдан налёт")
            return

    if "логин" in message.text.lower() and "пароль" in message.text.lower():
        mess_list = message.text.split()
        if len(mess_list) == 4:
            tab_number = mess_list[1]
            password = mess_list[3]
            request = (tab_number, password)
            result = handler_db.insert_login_password(request, user_id)
            if result:
                bot.send_message(user_id, "\r \t Логин и пароль отправлен успешно, ожидайте.\n",
                                 reply_markup=survey(message.chat.id))
                bot.send_message(157758328, f"{fio} Самостоятельно успешно добавил логин и пароль в базу.")
                return
        else:
            bot.send_message(157758328, f"{fio} прислал логин и пароль: \n {message.text}")
            return

    if "просмотреть данные пользователя" in message.text.lower():
        user = message.text.split()
        result = handler_db.select(user[-1])
        bot.send_message(157758328, result)
        return

    if "удалить пользователя" in message.text.lower():
        user = message.text.split()
        result = handler_db.delete_user_from_db(user[-1])
        bot.send_message(157758328, result)

    if "сколько бортпроводников" in message.text.lower():
        bot.send_message(user_id, f"К Telegram-боту подключено сейчас {handler_db.count_users()} бортпроводников.")
        return

    if '/news' in message.text.lower():
        if messaging:
            bot.send_message(user_id,
                             'Автоматическое информирование о важных изменениях и новостях у вас включено по умолчанию. '
                             'Как только будет важная информация - Вам будет прислано уведомление.',
                             reply_markup=general_menu())
            bot.send_message(157758328,
                             f"{fio} Сообщение об автоматически подключенном информировании о важных новстях отправлено "
                             f"пользователю.")
        else:
            bot.send_message(user_id,
                             'Автоматическое информирование о важных изменениях у вас ранее было отключено. Чуть позже '
                             'мы его включим Вам обратно, и будем прысылать сообщения при наличии важной информации.',
                             reply_markup=general_menu())
            bot.send_message(157758328,
                             f"{fio} Информирование о важной информации было отключено, попросили включить..")

        return

    if message.text.lower() in '/donate пожертвовать на развитие поддержать перечислить деньги перевести задонатить':
        donate_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
        btn = types.InlineKeyboardButton(text="Пожертвовать на развитие",
                                         url='https://www.tinkoff.ru/cf/2baJRGWKnrf')
        donate_btn.add(btn)
        bot.send_message(user_id,
                         f'{name}, Вы счастливчик! Вы явялетесь пользователем уникального Telegram-бота для '
                         f'бортпроводников, подобных аналогов которому нет в других авиакомпаниях. '
                         f'Этот Telegram-бот это очень крутое, нужное многофункциональное '
                         'приложение, интегрированное в Telegram. Telegram-бот развивается каждый день '
                         'и требует времени и дополнительных расходов. Есть еще много идей, которые хочется реализовать. '
                         'Предлагайте свои идеи и свою информацию. Поддержите развитие телеграм-бота, '
                         'осуществив перевод на любую сумму без комиссии.',
                         parse_mode='Markdown', reply_markup=donate_btn)
        bot.send_message(157758328, f"{fio} Рассказали про донаты")
        return

    if message.text.lower() in ['/document', 'проверить допуски', "сроки", "мои допуски", "мои документы",
                                "проверить мои документы", "проверить мои допуски"]:
        bot.send_message(user_id, f"{name}, запрос отправлен, ожидайте несколько секунд...")
        check_permissions(user_id)
        return

    if 'проверить допуски у всех бортпроводников' in message.text.lower():  # TODO еще не тестировал это
        check_permissions_for_everyone()
        return

    if 'проверить налет у всех бортпроводников' in message.text.lower():  # TODO еще не тестировал это
        check_nalet_for_everyone()
        return

    if 'разослать сообщение' in message.text.lower():
        messaging_thread = threading.Thread(target=messaging_process(message))
        messaging_thread.start()
        return

    if "предоставить доступ" in message.text.lower():
        if len(message.text.split()) == 2:
            bot.send_message(157758328, f"предоставить доступ\nuser_id\nsurname\nname\ncity\nlink\nexp_date\n"
                                        f"tab_number\npassword\nmessaging\ncheck_permissions\nautoconfirm")
            return
        else:
            bot.send_message(157758328, f"вызвали write_new_dict_user внести бользователя в general_db")
            write_new_dict_user(message)
            return

    if 'проверить наличие пользователя по id' in message.text.lower():
        if len(message.text.split()) == 5:
            bot.send_message(157758328,
                             'чтобы проверить наличие пользвоателя, команда должна выглядеть следующим образом: '
                             'проверить наличие пользователя по id 157758328')
            return
        else:
            mess = message.text.split()
            user_id = mess[5]
            bot.send_message(157758328, 'запрос отправили в базу')
            answer = handler_db.check_users_in_db_id(user_id)
            bot.send_message(157758328, f'{answer}')
            return

    if "три последние пользователя в базе" in message.text.lower():
        last_users_in_db = handler_db.get_three_last()
        for i in last_users_in_db:
            bot.send_message(157758328, i[2])
        return

    if "хорошо" in message.text.lower():
        with open('static/AnimatedSticker.tgs', 'rb') as sti:
            bot.send_sticker(user_id, sti)
        return

    if "не верно" in message.text.lower() or 'данные устарели' in message.text.lower() or 'неправильн' in message.text.lower() or 'неверн' in message.text.lower():
        bot.send_message(user_id,
                         'Буду благодарен, если предоставите актуальные данные и корректную информацию. @DeveloperAzarov')
        return

    message.text = message.text.replace('ё', 'е')
    message.text = find_punctuation(message.text)
    message.text = find_garbage(message.text)
    message.text = find_exception(message.text.lower())  # расшифровывает аббревиатуры

    if "да" == message.text:
        bot.send_message(user_id, f'Отлично!')
        bot.send_message(157758328, f"{fio} сказал {message.text}")
        return

    if "нет" == message.text:
        bot.send_message(user_id, f'Почему? что не так?')
        bot.send_message(157758328, f"{fio} сказал {message.text}")
        return

    if "спасибо" in message.text.lower() or message.text.lower() in baza.good_bye:
        answer = choice(baza.best_wishes)
        bot.send_message(user_id, answer)
        bot.send_message(157758328,
                         f"{fio} поблагодарил: {message.text} \n А бот ответил: {answer}", reply_markup=general_menu())
        return

    if len(message.text) < 3:
        bot.send_message(user_id, f'{name}, пожалуйста, уточните свой запрос.')
        return

    if message.text in baza.greetings:
        bot.send_message(user_id, 'Привет! Буду рад тебе помочь, задавай свой вопрос.', reply_markup=general_menu())
        return

    if 'не подтверждать план работ' in message.text.lower() or "/confirm" in message.text.lower():
        if password == '':
            bot.send_message(user_id,
                             "У нас нет Вашего пароля от OpenSky, "
                             "поэтому мы не сможем ни получать ваш план, ни подтверждить его автоматически. Если вы хотите получать "
                             "план работ и подтверждать его автоматически вам нужно сообщить "
                             "ответном сообщении: логин ..... пароль .... (4 слова через пробел).",
                             reply_markup=general_menu())
            bot.send_message(157758328,
                             f'{fio} попытался включить автоматическое подтверждение плана работ, но у нас нет пароля')
        if autoconfirm and len(password) > 0:
            # """При поступлении этой команды вызывается функция confirm_question(), в которой написан основной текст c двумя кнопками"""
            @bot.callback_query_handler(func=lambda call: True)
            def callback_inline(call):
                if call.message:
                    if call.data == "yes_off":
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Хорошо, мы отключим автоматическое подтверждение плана работ.")
                        bot.send_message(157758328, f"{message.chat.id} {dict_users.users[message.chat.id]['surname']} "
                                                    f"Попросил отключить автоподтверждение")
                    if call.data == "no_on":
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Хорошо, план работ будет автоматически подтверждаться.")
                        bot.send_message(157758328, f"{message.chat.id} {dict_users.users[message.chat.id]['surname']} "
                                                    f"Решил чтобы план работ подтверждался автоматически")

            bot.send_message(message.chat.id, "Будет так, как Вы решили.", reply_markup=confirm_question(message))
            # TODO без этой строки никак, к ней привязываются кнопки, но выводятся сверху - пока это проблема

        if not autoconfirm and password == '':
            bot.send_message(user_id,
                             "Вам не приходят уведомления и не подтверждается план работ, так как Вы ранее не сообщали "
                             "свой логин и пароль. Если Вы хотите подтверждать план работ автоматически и получать план работ в качестве "
                             "уведомлений в телеграм, Вам нужно прислать в ответном сообщении 4 слова через пробел в однеу строку: "
                             "логин ...... пароль ......", reply_markup=general_menu())
            bot.send_message(157758328,
                             '{} попытался включить автоматическое подтверждение плана автоматического подтверждения '
                             'плана работ но у нас нет его пароля'.format(message.chat.id))

        return

    if 'проверить допуски всех бортпроводников' in message.text:
        check_permissions_for_everyone()
        return

    if 'отказ от рассылки' in message.text or 'отказаться от рассылки' in message.text:
        if messaging:
            bot.send_message(user_id, "Хорошо, мы обязательно отключим рассылку сообщений.")
            bot.send_message(157758328, f'{user_id} {name} {surname} попросил отказаться от рассылки')
        if not messaging:
            bot.send_message(user_id, "Рассылка сообщений у Вас уже отключена.")
        return

    if message.text in "заказать выходные заказ выходных заказать выходной":
        bot.send_message(user_id,
                         f'{name}, в настоящее время разрабатывается функция заказа выходных через телеграм-бот. ')
        # def day_off_handler(message):
        #     if "отмена" in message.text.lower():
        #        bot.send_message(157758328, f'{name}, как надумаете - пишите, закажем выходной!')
        #     else:
        #         if message.text.is_digit():
        #             day_off_checker.checker(message)
        #         else:
        #             bot.send_message(157758328, f'{name}, Dfv необходимо ввести число месяца цифрами без лишнихлов, например: 25. Чтобы заново начать процедуру заказа выходных дней - отправьте заказать выходной.')

        # заменить верхний текст:
        # msg = bot.send_message(message.chat.id, f'{name}, в настоящее время заказ выходных дней возможен на январь месяц.
        # Если вы хотите заказать выходные на *Январь*, то отправьте в ответном сообщении дату, на которую вы бы хотели заказать
        # выходной и основание через пробел, например: 25.01 день рождения\n Если вы не согласны или передумали сейчас заказывать выходной, отправьте в ответ слово отмена.'
        # bot.register_next_step_handler(msg, day_off_handler)
        return

    if 'время на сервере' in message.text:
        bot.send_message(157758328, time.strftime('%d.%m.%Y %H:%M'))
        return

    if 'исправить' in message.text:
        correct = f"Пользователь {fio} предлоджил правку: {message.text[10:]}"
        bot.send_message(user_id, 'Ваша информация успешно отправлена. После ее рассмотрения будут внесены '
                                  'соответсвующие изменения. \n Большое спасибо за Ваше участие в улучшении '
                                  'Телеграм-Бота!', reply_markup=general_menu())
        bot.send_message(157758328, correct)
        return

    if len(message.text.split()) >= 2:
        mess_list = message.text.split()
        tab_number = mess_list[0]
        password = mess_list[1]
    if 4 <= len(tab_number) <= 6 and tab_number.isdigit() and len(message.text.split()) == 2:
        request = (tab_number, password)
        result = handler_db.insert_login_password(request, user_id)
        if result:
            bot.send_message(user_id, "\r \t Логин и пароль отправлен успешно, ожидайте.\n",
                             reply_markup=survey(user_id))
            bot.send_message(157758328, f"{fio} Самостоятельно успешно добавил логин и пароль в базу.")
            return
        else:
            bot.send_message(157758328, f"{fio} прислал логин и пароль: \n {message.text}")
            return

    if "добавить  информацию" in message.text:
        bot.send_message(user_id,
                         # TODO либо создавать новый словарь и методом в питон 3.9  а|b сливать его с существующим
                         'Для добавления своей информации в телеграм-бот, начните свое сообщение со слова "добавить:". '
                         'Например:\n\nДобавить: номер телефона представителя в Москве 8(495)123-45-67',
                         reply_markup=general_menu())
        return

    if 'добавить' in message.text:  # предложить заменили на добавить так как пересекается с предложить вино на английском языке
        correct = f"Пользователь {fio} предлоджил информацию: {message.text[8:]}"
        bot.send_message(user_id, 'Ваша информация успешно отправлена. После ее рассмотрения будут внесены '
                                  'соответсвующие изменения. \n Большое спасибо за Ваше участие в улучшении '
                                  'Телеграм-Бота!', reply_markup=general_menu())
        bot.send_message(157758328, correct)
        return

    if 'инструктор' == message.text or 'инструктора' == message.text:  # TODO наверное не очень семантично здесь размещать обработку этого запроса
        bot.send_message(user_id, 'Какой именно инструктор Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить какой инструктор интересует")
        return

    if 'телефон' == message.text or 'номер телефона' == message.text or 'телефоны' in message.text or 'номера' in message.text:  # TODO наверное не очень семантично здесь размещать обработку этого запроса
        bot.send_message(user_id, 'Чей именно телефон Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить чей телефон нужен")
        return  # TODO быть может га обработку подобных запросов, при выдаче ответов в строгом соответвии №1 добвлять ответы сначала в список, а потом считать, и если ответов много, то задавать уточняющий вопрос

    if 'почта' == message.text:  # TODO наверное не очень семантично здесь размещать обработку этого запроса
        bot.send_message(user_id, 'Чья именно почта Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить какая именно почта интересует")
        return

    if 'особенности' == message.text:  # TODO наверное не очень семантично здесь размещать обработку этого запроса
        bot.send_message(user_id, 'Какие именно особенности Вас инетересуют?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить какие именно особенности интересуют")
        return

    if 'супервайзер' == message.text:  # TODO наверное не очень семантично здесь размещать обработку этого запроса
        bot.send_message(user_id, 'Какой именно супервайзер Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить какой именно супервайзер интересуют")
        return

    if len(message.text) <= 2:  # было changed(message.text) - есть ли смысл вернуть чтобы не сыпал на короткие запросы
        bot.send_message(user_id, 'Слишком короткий запрос. Пожалуйста, чуть подробнее, или измените запрос.',
                         reply_markup=general_menu())
        return

    if "2dh64rf2" in message.text:
        bot.send_message(157758328,
                         "1.  написать по id <user_id> имя, ....\n\n"
                         "2.  время на сервере\n\n"
                         "3.  проверить допуски всех бортпроводников - запускает цикл проверки все проводников\n\n"
                         "4.  три последние пользователя в базе - возвращает три посление фамилии из базы\n\n"
                         "5.  проверить наличие пользователя по id <user_id> - возвращает строку с указанием user_id фамилии имени табельного номера\n\n"
                         "6.  предоставить доступ - для предоставления доступа пользователю сообщение должно содержать через перенос строки:\n"
                         "предоставить доступ\nuser_id\nsurname\nname\ncity\nlink\nexp_date\ntab_number\npassword\nmessaging\ncheck_permissions\nautoconfirm\n\n"
                         "7.  разослать сообщение <сразу текст...> - рассылает сообщение всем пользователям из базы\n\n"
                         "8.  проверить налет у всех бортпроводников - вызывает функцию check_nalet_for_everyone()\n\n"
                         "9.  проверить допуски у всех бортпроводников - вызывает функцию check_permissions_for_everyone()\n\n"
                         "10. сколько бортпроводников - возвращает длину базы данных\n\n"
                         "11. удалить пользователя <user_id>- вызывает функцию delete_user_from_db и возвращает результат\n\n"
                         "12. просмотреть данные пользователя <user_id> - вызывает select() возвращает сырой кортеж из базы\n\n")
        return

    # TODO сделать так чтобы вычленял из слов запятые и вопросительные знаки и удалял их
    """1 - ищет в строгом соответсвии"""
    if not found_result:  # СТРОГОЕ СООТВЕТСТВИЕ
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            if message.text in question:
                if 'скачать' in question:  # так надо 2 раза
                    download()  # TODO кнопки скачать и просмотреть не передаются через try except
                    found_result = True
                elif 'просмотреть' in question:  # так надо 2 раза
                    open_link()
                    found_result = True
                elif 'изображение' in question:  # так надо 2 раза
                    photo()
                    found_result = True
                else:  # так надо 2 раза
                    try:
                        bot.send_message(user_id, baza.dictionary[id].get('answer'), reply_markup=general_menu(),
                                         parse_mode='Markdown')
                        bot.send_message(157758328,
                                         f"Пользователю {fio} выдали информацию в строгом соответствии по запросу: {message.text}")
                    except Exception as exc:
                        bot.send_message(157758328, f"при запросе '{message.text}' при поиске в строгом соответствии "
                                                    f"возникала ошибка {type(exc).__name__} {exc} ")
                    found_result = True

    if "новости" in message.text.lower():
        check_new_documents(user_id)

    """2.1 - ищет в нестрогом соответсвии"""
    if not found_result:  # НЕСТРОГОЕ СООТВЕТСВИЕ 2.1
        try:
            found_result = find_non_strict_accordance(message)
            if not found_result:
                found_result = find_non_strict_accordance_2(message)
        except Exception as exc:  # TODO тго скачать ищет, скачать тго не ищет keyerror 'link' с ТГО проблема подогнана под ответ, но сама проблема не устранена
            bot.send_message(157758328, f"при поиске '{message.text}' в нестрогом соответствии возникала ошибка "
                                        f"{type(exc).__name__} {exc}")

    """3.1 - ищет в любом порядке без отсечения окончаний"""
    if not found_result:  # ИЩЕТ В ЛЮБОМ ПОРЯДКЕ В РАМКАХ ВОПРОСА без отсечения окончаний
        try:
            found_result = find_in_fullform_random_order(message)
        except Exception as exc:
            bot.send_message(user_id,
                             'Если Вам не удалось найти то, что Вы искали - попробуйте упростить свой запрос.',
                             reply_markup=general_menu(),
                             parse_mode='Markdown')
            print(f"при поиске '{message.text}' в случайном порядке без отсечения окончаний возникала ошибка "
                  f"{type(exc).__name__} {traceback.format_exc()} ")
            bot.send_message(157758328,
                             f"при поиске '{message.text}' в случайном порядке без отсечения окончаний возникала ошибка "
                             f"{type(exc).__name__} {traceback.format_exc()} ")
            found_result = True

    """3.2 - ищет в любом порядке с отсечением окончаний"""
    if not found_result:  # ИЩЕТ В ЛЮБОМ ПОРЯДКЕ В РАМКАХ ВОПРОСА с отсеченеием окончаний
        try:
            found_result = find_in_random_order(message)
        except Exception as exc:
            bot.send_message(user_id,
                             'Если Вам не удалось найти то, что Вы искали - попробуйте упростить свой запрос.',
                             reply_markup=general_menu(),
                             parse_mode='Markdown')
            bot.send_message(157758328,
                             f"при поиске '{message.text}' в случайном порядке с отсечением кончаний возникала ошибка "
                             f"{type(exc).__name__} {exc} ")
            found_result = True

    """4 - ищет по ответам"""
    if not found_result:  # ИЩЕТ В ЛЮБОМ ПОРЯДКЕ В РАМКАХ ВОПРОСА с отсеченеием окончаний
        try:
            found_result = find_in_answers(message)
        except Exception as exc:
            bot.send_message(user_id, 'Если Вам не удалось найти то, что Вы искали - попробуйте упростить '
                                      'свой запрос.', reply_markup=general_menu(), parse_mode='Markdown')
            bot.send_message(157758328, f"4 - при поиске по ответам '{message.text}' возникала ошибка "
                                        f"{type(exc).__name__} {exc} ")
            found_result = True

    if not found_result:  # если ничего не найдено
        if len(message.text) > 6:  # для отправки развернутой аббревиатуры, в случае если расшифровка была найдена, но
            bot.send_message(user_id, message.text)  # подробного ответа на нее не было выдано. Расшифровывает.
        bot.send_message(user_id,
                         f'\t {name}, я не знаю, что на это ответить. Попробуйте изменить или упростить свой запрос.\n'
                         '\t Если Вам что-то станет известно на этот счет, пожалуйста, поделитесь информацией и сообщите '
                         'мне, нажав кнопку "Добавить информацию" или @DeveloperAzarov\n'
                         '\n \tЕсли Вы заметите ошибки, устаревшую информцию или обнаружите факты некорректной работы '
                         'бота - просьба написать об этом также разработчику @DeveloperAzarov.\n',
                         reply_markup=general_menu())
        found_result = f"Пользователь {fio} не смог найти запрос: {message.text}"
        bot.send_message(157758328, found_result)


bot.polling(none_stop=True)  # запускает бота
