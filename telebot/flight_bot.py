# -*- coding: utf8 -*-
# !/usr/bin/env python3

import telebot  # чтобы работал telebot - удалить telebot, и установить Pytelegrambotapi, написанным оставить telebot
from telebot.types import InlineKeyboardMarkup
import baza
from telebot import types
from random import choice
import settings
import dict_users
import getplan
import getnalet
import notificator
import threading
import time
import get_permissions
import traceback
import flight_counter
import check_news

bot = telebot.TeleBot(settings.TOKEN)


def survey(user_id):
    """Сообщение с кнопками для проведения опроса под индивидуальные пожелания. Вызов функции прикрепляется в качестве параметра к reply_markup в bot.send_message"""
    survey_btns = types.InlineKeyboardMarkup(row_width=1)
    one = types.InlineKeyboardButton(text="1 - Вылет UTC, Прилёт МСК", callback_data="one")
    two = types.InlineKeyboardButton(text="2 - Вылет МСК, Прилёт МСК", callback_data="two")
    three = types.InlineKeyboardButton(text="3 - Вылет МСК, Прилёт UTC", callback_data="three")
    four = types.InlineKeyboardButton(text="4 - Вылет UTC, Прилёт UTC", callback_data="four")
    survey_btns.add(one, two, three, four)
    bot.send_message(user_id, f"`\t\t {dict_users.users[user_id]['name']}, Ваш логин пароль успешно отправлен. \n"
                              f"`\t\t Для завершения персональной настройки, "
                              f"укажите часовые пояса, в которых Вам было бы удобно получать план работ: UTC или MSK",
                     reply_markup=survey_btns)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """Всего лишь Обработчик опроса, который сообщает разработчику результаты индивидуальных ответов пользоателя."""
    if call.message:
        if call.data == "one":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Хорошо, спасибо за ответ.")
            bot.send_message(157758328, f"{call.message.chat.id} {dict_users.users[call.message.chat.id]['surname']} "
                                        f"Ответил, номер один: UTC МСК")
        if call.data == "two":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Хорошо, спасибо за ответ. Скоро исправлю")
            bot.send_message(157758328, f"{call.message.chat.id} {dict_users.users[call.message.chat.id]['surname']} "
                                        f"Попросил номер два: МСК МСК")
        if call.data == "three":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Хорошо, спасибо за ответ. Скоро исправлю")
            bot.send_message(157758328, f"{call.message.chat.id} {dict_users.users[call.message.chat.id]['surname']} "
                                        f"Попросил номер три: МСК UTC")
        if call.data == "three":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Хорошо, спасибо за ответ. Скоро исправлю")
            bot.send_message(157758328, f"{call.message.chat.id} {dict_users.users[call.message.chat.id]['surname']} "
                                        f"Попросил номер четыре: UTC UTC")


def cycle_plan_notify():
    while True:
        counter_errors = 0
        counter_users = 0
        users_off_list = []
        sent_plan_counter = 0
        sent_plan_list = []
        for user_id in dict_users.users.keys():
            counter_users += 1
            name = dict_users.users[user_id]['name']
            surname = dict_users.users[user_id]['surname']
            fio = f'{user_id} {surname} {name} '
            try:
                notification = notificator.notify(
                    user_id)  # TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС  ЗАПИСИ ФАЙЛА в НОТИФИКАТОРЕ!!!!!!!
                if notification != None:  # не равно none - получили план. будет ошибка, если ему не удалось отправить ему его план - по
                    plan_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
                    btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                                     url='https://edu.rossiya-airlines.com/workplan/')
                    plan_btn.add(btn)
                    bot.send_message(user_id, notification, reply_markup=plan_btn,
                                     parse_mode='html')  # отправляем пользователю его план
                    sent_plan_counter += 1
                    sent_plan_list.append(fio)
                if notification == None:  # равно None - не записан пароль пользователя, парсить не стали
                    continue  # bot.send_message(157758328, 'Нет пароля у пользователя') # в самом парсере тоже написано return если отсутсвует пароль в словаре
            except Exception:  # если случилась ошибка при отправке сообщений пользователю
                users_off_list.append(fio)
                counter_errors += 1
                error = f'{traceback.format_exc()}'  # TODO в этом месте надо предусмотреть, чтио ошибок может быть несколько от разных пользователей: добавлять в список ошибки? только нужны сами ошибки а не весь путь
                continue

            # bot.send_message(user_id, "Чуть попозже будет так, как Вы решили. Если вы уже отвечали на опрос, повторно отвечать не нужно.", reply_markup=survey(user_id))

        if sent_plan_counter > 0:
            bot.send_message(157758328, f'план выслан {sent_plan_counter} пользователям: {", ".join(sent_plan_list)}')
            if len(users_off_list) != 0:
                bot.send_message(157758328, f'не удалось отправить план: {", ".join(users_off_list)}: {error}')

        time.sleep(300)


plan_thread = threading.Thread(target=cycle_plan_notify)
plan_thread.start()


def check_permissions_for_everyone():
    document_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
    btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                     url='https://edu.rossiya-airlines.com/ready/userReady-1/')
    document_btn.add(btn)
    bot.send_message(157758328, f'Бот начал проверку допусков проводников.')
    for user_id in dict_users.users.keys():
        if dict_users.users[user_id]['password'] == '':
            continue
        else:
            name = dict_users.users[user_id]['name']
            surname = dict_users.users[user_id]['surname']
            fio = f'{user_id} {surname} {name}'
            try:
                documents_info = get_permissions.parser(user_id, name, surname)
                bot.send_message(user_id, documents_info, reply_markup=document_btn)
                bot.send_message(157758328, f'Пользователю {fio} отправлен сообщение об истекающих допусках.')
                bot.send_message(157758328, documents_info, reply_markup=document_btn)  # TODO закомментировать
            except Exception:
                bot.send_message(157758328,
                                 f'Пользователю {fio} не удалось отправить сообщение об истекающих допусках, произошла ошибка: {traceback.format_exc()}')
                continue
    time.sleep(3000)


# permissions_thread = threading.Thread(target=check_permissions_for_everyone) #TODO закомментирвоать
# permissions_thread.start()


def check_new_documents():
    document_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
    btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                     url='https://edu.rossiya-airlines.com/')
    document_btn.add(btn)

    try:
        new_document = check_news.parser(157758328)
        if new_document is not None:
            bot.send_message(157758328, new_document, reply_markup=document_btn)  # TODO закомментировать
    except Exception:
        bot.send_message(157758328,
                         f'не удалось отправить сообщение о новых документах, произошла ошибка: {traceback.format_exc()}')

    time.sleep(2000)


check_new_documents_thread = threading.Thread(target=check_new_documents)  # TODO закомментирвоать
check_new_documents_thread.start()


def messaging(message):
    mess = message.text.split()
    counter_users = 0
    counter_errors = 0
    sent_list = []
    users_off_list = []
    for user_id in dict_users.users.keys():
        if dict_users.users[user_id]['messaging']:
            name = dict_users.users[user_id]['name']
            surname = dict_users.users[user_id]['surname']
            fio = f'{user_id} {name} {surname}'
            try:
                if len(name) == 0:
                    bot.send_message(user_id, 'Уважаемый бортпроводник, {}'.format(' '.join(mess[2:]),
                                                                                   reply_markup=general_menu()))
                else:
                    bot.send_message(user_id, f'{name}, {mess[2:]}', reply_markup=general_menu())
                # bot.send_message(user_id,
                #                  "Если Вы не хотите получать рассылку, отправьте: отказ от рассылки")
                # sent_list.append(fio)
                counter_users += 1
                bot.send_message(157758328, f"Сообщение успешно отравлено {fio}")  # TODO временно
                time.sleep(3)
            except Exception:  # если случилась ошибка при отправке сообщений пользователю
                users_off_list.append(fio)
                counter_errors += 1
                bot.send_message(157758328,
                                 f"сообщение не удалось отправить {fio} ошибка {traceback.format_exc()}.")  # TODO временно
        else:
            continue
    bot.send_message(157758328,
                     f"всего разослано {counter_users} чел. из {len(dict_users.users)} чел.")  # TODO временно

    return


def general_menu():
    general_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton('План работ')
    btn2 = types.KeyboardButton('Мой налет')
    btn3 = types.KeyboardButton('Расчётный лист')
    btn4 = types.KeyboardButton('Новости')
    btn5 = types.KeyboardButton('Исправить ответ')
    btn6 = types.KeyboardButton('Добавить  информацию')  # InlineKeyBoard (callback_data='Внести информацию')
    general_menu.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return general_menu


def write_new_dict_user(message):  # TODO почему стирает весь файл?
    """Предоставление доступа пользователю: внесение новго пользователя в словарь непосредлственно сразу через чат телеграм-бота."""
    bot.send_message(157758328, "зашли в словарь юзеров.")
    try:
        mess = message.text.split()
        with open('dict_users.py', 'r', encoding='utf-8') as original:
            data = original.read()
        with open('dict_users.py', 'w', encoding='utf-8') as modified:
            modified.write(
                data[:-1] + mess[2] + ': {"surname": "' + mess[3] + '",\n "name": "' + mess[4] + '",\n "city": "' +
                mess[5] + '",\n "link": "' + mess[6] + '",\n "exp_date": "' + mess[7] + '",\n "tab_number": "' + mess[
                    8] + '",\n "password": "' + mess[9] + '",\n "access": ' + mess[10] + ',\n "plan_notify": ' + mess[
                    11] + ',\n "autoconfirm": ' + mess[12] + ',\n "messaging": ' + mess[13] + '},\n }')
        bot.send_message(int(mess[2]),
                         f'{dict_users.users[int(mess[2])]["name"]}, Вам успешно предоставлен доступ к телеграм-боту. Спрашивайте, буду рад помочь! Если хотите получать уведомления на телефон об изменениях в плане работ, то просим Вас выслать в ответном одном сообщении через пробел логин и пароль от OpenSky (4 слова) по следующему шаблону: логин ....... пароль ......',
                         reply_markup=general_menu())
        bot.send_message(157758328, "внесли запись в файл")
        bot.send_message(157758328,
                         "Сообщение о предоставлении доступа пользователю отправлено успешно. \n\n ОБНОВИ СЕРВЕР!")
    except Exception as exc:
        bot.send_message(157758328,
                         f"произошла ошибка при предоставлении доступа {exc}. Словарь пользователей стерся полностью. \n Используй шаблон заполнения словаря: предоставить доступ id фамилия имя город ссылка срок табельный пароль access plan_notify autoconfirm messaging")


def service_notification(message):
    """Уведомление на случай проведения технических работ на сервере."""
    bot.send_message(message.chat.id,
                     'На сервере проводятся технические работы. Возможна некорретная работа телеграм-бота. Это продлится недолго. Приносим свои извинения за доставленные неудобства.')
    bot.send_message(157758328,
                     "Отправлено уведомление о некорректной работе телеграм-бота пользователю id {0.id} @{0.username} {0.first_name} {0.last_name}".format(
                         message.from_user, message.from_user, message.from_user))


def verification(message):
    """Верифицирует пользователя каждый раз: проверяет есть ли у него одобренный доступ к телеграм-боту."""
    if message.chat.id in dict_users.users.keys():
        return True
    else:
        bot.send_message(message.chat.id,
                         'Прошу Вас пройти верификацию, для этого Вам необходимо отправить сюда фото своего штабного '
                         'пропуска либо связаться с разработчиком лично '
                         '@DeveloperAzarov. Нам необходимо убедиться, что вы летающий '
                         'бортпроводник АК "Россия". \n')
        bot.send_message(message.chat.id, 'Уважаемый бортпроводник! К сожалению, на время ожидания вашего лётного '
                                          'удостоверения, доступ временно ограничен, но нам не терпится как можно '
                                          'быстрее предоставить Вам доступ.')
        bot.send_message(157758328,
                         "Запросили фото айдишки для верификации от пользователя id {0.id} @{0.username} {0.first_name} "
                         "{0.last_name}".format(message.from_user, message.from_user, message.from_user))
        return False


@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    """пересылает разработчику картинку отправленную пользователем. Сделано для верификации по айдишке"""
    bot.send_photo(157758328, message.photo[0].file_id)
    new_photo_notification = "Пользователь {0.first_name} {0.last_name} @{0.username} id {0.id} прислал " \
                             "фото.".format(message.from_user, message.from_user, message.from_user,
                                            message.from_user)
    bot.send_message(157758328, new_photo_notification)
    bot.send_message(message.chat.id, "Фото отправлено успешно.")


@bot.message_handler(commands=['start'])
def welcome(message):
    """При первом подключении пользователя к боту - выводит приветсвенный стикер, приветсвенную речь. Также в этой
    функции обозначены кнопки, которые будут всегда отображаться под полем ввода запроса."""
    # service_notification(message)

    sti = open('static/AnimatedSticker.tgs', 'rb')
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

    name = dict_users.users[message.chat.id]['name']
    surname = dict_users.users[message.chat.id]['surname']
    password = dict_users.users[message.chat.id]['password']
    fio = f'{name} {surname}'

    def photo():
        """Отправляет пользовтелю информацию с фото"""
        pic = baza.dictionary[id].get('photo')
        bot.send_message(message.chat.id, baza.dictionary[id].get('answer'),
                         parse_mode='Markdown', )  # reply_markup=photo_btn
        bot.send_photo(message.chat.id, pic)
        bot.send_message(157758328, "Выдали фото по запросу: " + message.text)

    def open():
        """Предлагает открыть сайт"""
        download_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
        btn = types.InlineKeyboardButton(text="ОТКРЫТЬ", url=baza.dictionary[id]['link'])
        download_btn.add(btn)
        bot.send_message(message.chat.id, baza.dictionary[id].get('answer'), parse_mode='Markdown',
                         reply_markup=download_btn)
        bot.send_message(157758328, "Предложили ОТКРЫТЬ: " + message.text)
        new_file_notification = "Пользователь {0.first_name} {0.last_name} @{0.username} id {0.id}." \
            .format(message.from_user, message.from_user, message.from_user,
                    message.from_user)
        bot.send_message(157758328, new_file_notification)

    def download():
        """Предлагает скачать файл"""
        download_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="СКАЧАТЬ", url=baza.dictionary[id][
            'link'])  # TODO возникает ошибка в кнопку нельзя передавать содержание ключа 'link' ссылку методом .get('link') [id]['link'] возникает ошибка
        download_btn.add(btn)
        bot.send_message(message.chat.id, baza.dictionary[id].get('answer'), parse_mode='Markdown',
                         reply_markup=download_btn)
        bot.send_message(157758328, "Предложили скачать: " + message.text)
        new_file_notification = "Пользователь {0.first_name} {0.last_name} @{0.username} id {0.id}." \
            .format(message.from_user, message.from_user, message.from_user,
                    message.from_user)
        bot.send_message(157758328, new_file_notification)

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

    def find_abbreviation(message):
        """все запросы от пользователя сначала прогоняет через словарь исключений, если функция находит его там, то
        заменяет его на такое же развернутое значение, которое следует использовать при дальнейшем поиске. ищет слова
        для преобразования чтобы обойти минимально допустимое разрешение на длину слова"""
        for word in message.split(' '):
            for id in baza.exceptions:
                if word == baza.exceptions[id]['word']:
                    return baza.exceptions[id]['changed_word']
        answer = f"Как расшифровывается {word.upper()} мне пока неизвестно."
        return answer

    def find_garbage(message):
        """Ищет лишние слова-сорняки, которые вешают программу (как, кто, где) и меняет их на пустую строку"""
        for word in baza.garbage:  # для каждого слова в кортеже
            if word.lower() in message.lower():  # если это каждое слово есть в запросе
                message = message.replace(word, '')

        return message

    def find_non_strict_accordance(message):
        """2 - Ищет не в строгом соответсвии."""
        if 4 <= len(message.text) <= 5:
            bot.send_message(message.chat.id, "Пожалуйста, уточните свой вопрос", reply_markup=general_menu(),
                             parse_mode='Markdown')
            bot.send_message(message.chat.id, f'2.1 Пользователя {fio} попросили уточнить вопрос {message.text}')
            found_result = True
            return found_result
        else:
            for id in baza.dictionary:
                question = baza.dictionary[id]['question'].lower()
                # нужно сделать так чтобы для каждого слова из # bcgjkmpjdfnm функцию find для вопроса и ответа либо создать функцию которая будет записывать чсило совпадению в клю словаря, а сам ответ в ответ словаря.. и по наибольшему ключу - искать нужный
                if changed(message.text) in changed(question):
                    if 'скачать' in baza.dictionary[id]['question'].lower():  # так надо 2 раза
                        download()
                    elif 'просмотреть' in question:  # так надо 2 раза
                        open()
                    elif 'изображение' in question:  # так надо 2 раза
                        photo()
                    else:  # так надо 2 раза
                        bot.send_message(message.chat.id, baza.dictionary[id]['answer'], reply_markup=general_menu(),
                                         parse_mode='Markdown')
                        bot.send_message(157758328,
                                         "2.1 - ответ выдан не в строгом соответсвии по запросу: " + message.text)
                        non_strict_notification = "Пользователь {0.first_name} {0.last_name} @{0.username} id {0.id}." \
                            .format(message.from_user, message.from_user, message.from_user,
                                    message.from_user)
                        bot.send_message(157758328, non_strict_notification)
                    found_result = True
                    return found_result

    def find_non_strict_accordance_2(message):
        """2 - Ищет не в строгом соответсвии."""
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            # нужно сделать так чтобы для каждого слова из # bcgjkmpjdfnm функцию find для вопроса и ответа либо создать функцию которая будет записывать чсило совпадению в клю словаря, а сам ответ в ответ словаря.. и по наибольшему ключу - искать нужный
            if changed(message.text) in changed(question):
                if 'скачать' in baza.dictionary[id]['question'].lower():  # так надо 2 раза
                    download()
                elif 'просмотреть' in question:  # так надо 2 раза
                    open()
                elif 'изображение' in question:  # так надо 2 раза
                    photo()
                else:  # так надо 2 раза
                    bot.send_message(message.chat.id, baza.dictionary[id]['answer'], reply_markup=general_menu(),
                                     parse_mode='Markdown')
                    bot.send_message(157758328,
                                     "2.2 - ответ выдан не в строгом соответсвии по запросу: " + message.text)
                    non_strict_notification = "Пользователь {0.first_name} {0.last_name} @{0.username} id {0.id}." \
                        .format(message.from_user, message.from_user, message.from_user,
                                message.from_user)
                    bot.send_message(157758328, non_strict_notification)
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
                    link = baza.dictionary[id].get(
                        'link')  # TODO кнопки скачать и просмотреть не передаются через try except
                elif 'изображение' in question:  # так надо 2 раза
                    photo = baza.dictionary[id].get('photo')

        if len(results) < 8:  # выдает ответы при оптимальном количстве результатов
            for each_answer in results:  # TODO не прикрепляет кнопки к ответу, если выдается ответ в случайном порядке
                if link:
                    open_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
                    btn = types.InlineKeyboardButton(text="ОТКРЫТЬ", url=link)
                    open_btn.add(btn)
                    bot.send_message(message.chat.id, each_answer, parse_mode='Markdown',
                                     reply_markup=open_btn)
                    found_result = True
                if photo:
                    photo()
                    found_result = True
                if link is None:
                    bot.send_message(message.chat.id, each_answer, reply_markup=general_menu(), parse_mode='Markdown')
                    found_result = True
                report = "3.1 - Пользователю {0.first_name} {0.last_name} @{0.username} id {0.id} выдан ответ в случайном порядке по запросу:\n" \
                             .format(message.from_user, message.from_user, message.from_user,
                                     message.from_user) + message.text
                bot.send_message(157758328, report)
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

                bot.send_message(message.chat.id, each_answer, reply_markup=general_menu(), parse_mode='Markdown')
                if link:
                    bot.send_message(message.chat.id, link, reply_markup=general_menu(), parse_mode='Markdown')
                found_result = True
                report = "3.2 - Пользователю {0.first_name} {0.last_name} @{0.username} id {0.id} выдан ответ в случайном порядке по запросу:\n" \
                             .format(message.from_user, message.from_user, message.from_user,
                                     message.from_user) + message.text
                bot.send_message(157758328, report)
                return found_result

    def confirm_question(message):
        """Сообщение с кнопками для отмены подтверждения плана работ, либо оставить всё как есть."""
        confirm_btns = types.InlineKeyboardMarkup()
        yes_off = types.InlineKeyboardButton(text="Да, отключить", callback_data="yes_off")
        no_on = types.InlineKeyboardButton(text="Нет, подтверждать", callback_data="no_on")
        confirm_btns.add(yes_off, no_on)
        bot.send_message(message.chat.id, f"`\t\t {dict_users.users[message.chat.id]['name']}, cейчас у Вас план работ "
                                          f"подтверждается автоматически. Вы хотите отключить подтверждение ознакомления "
                                          "с планом работ? Уведомления сюда будут приходить, но план не будет подтвержден в "
                                          "OpenSky автоматически. \n \t\t При проверке Telegram видит все "
                                          "рейсы, в том числе те, которые у Вас уже сняли, но которые еще висят в плане, "
                                          "потому что Вы еще не подтвердили ознакомление с планом. Поэтому эти рейсмы будут "
                                          "добавляться в уведомление. Чтобы информация в уведомлении была актуальной,  было "
                                          "решено активировать сразу ознакомление с планом, чтобы удалить снятые рейсы. Если "
                                          "это отключить автоподтверждение, то на телефон будут приходить уведомления  "
                                          "вместе с теми рейсами, которые у Вас уже убрали из плана. Такая информация не "
                                          "будет достоверной. \n\t\t Всё равно отключить автоподтверждение плана работ?",
                         reply_markup=confirm_btns)

    def check_permissions(user_id):
        document_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
        btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
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
            fio = f'{user_id} {surname} {name}'
            try:
                documents_info = get_permissions.parser(user_id, name, surname)
                bot.send_message(user_id, documents_info, reply_markup=document_btn)
                bot.send_message(user_id, f'Пользователю {fio} отправлено сообщение об истекающих допусках.',
                                 reply_markup=document_btn)
            except Exception:
                bot.send_message(user_id,
                                 f'Пользователю {fio} не удалось отправить сообщение об истекающих допусках, произошла ошибка: {traceback.format_exc()}',
                                 reply_markup=document_btn)
        return

    found_result = False  # TODO сделать чтобы запрос превр в список слов, и обрабат-е вопрос в словаре тоже в список и проверялось количество совпадений, но как-то тогда надо отделать хорошие соотсевтвия от плохих и опредлять сколько выдавать значений в результат. Третья ступень поиска так и ищет по списку, может так и оставить как есть, но тогда первые способы находят не все что нужно - так ли это - проверить
    global user_id

    # service_notification(message)

    if "написать пользователю по id" in message.text.lower():
        mess = message.text.split()
        bot.send_message(int(mess[4]), ' '.join(mess[5:]).capitalize(), reply_markup=general_menu())
        bot.send_message(157758328, "Сообщение пользователю отправлено успешно.")
        return

    # if "пройти опрос" in message.text.lower():
    #     bot.send_message(message.chat.id, "Чуть попозже будет так, как Вы решили.",
    #                      reply_markup=survey(message.chat.id))
    #     return

    if '/news' in message.text.lower():
        bot.send_message(message.chat.id,
                         'Автоматическое информирование о важных изменениях и новостях включено у всех по умолчанию. Как только будет важная информация - Вам будет прислано уведомление.',
                         reply_markup=general_menu())
        bot.send_message(157758328,
                         "Сообщение об автоматически подключенном информировании о важных новстях отправлено пользователю.")
        return

    if '/donate' in message.text.lower():
        donate_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
        btn = types.InlineKeyboardButton(text="Пожертвовать на развитие",
                                         url='https://money.alfabank.ru/p2p/web/transfer/dazarov5659')
        donate_btn.add(btn)
        bot.send_message(message.chat.id,
                         'Телеграм-бот для бортпроводников - это очень крутое, нужное многофункциональное '
                         'приложение, интегрированное в Telegram. Телеграм-бот развивается каждый день '
                         'и требует времени и ресурсов. Есть еще много идей, которые хочется реализовать. '
                         'Предлагайте свои идеи и свою информацию. Поддержите развитие телеграм-бота, '
                         'осуществив перевод на любую сумму без комиссии.',
                         parse_mode='Markdown', reply_markup=donate_btn)
        return

    if '/document' in message.text.lower() or 'проверить допуски' in message.text.lower() or "сроки" in message.text.lower():
        bot.send_message(message.chat.id, f"{name}, запрос отправлен, ожидайте несколько секунд...")
        check_permissions(message.chat.id)
        return

    if 'разослать сообщение' in message.text.lower():  # TODO протестирвоать потом на одном пользователе
        messaging_thread = threading.Thread(target=messaging(message))
        messaging_thread.start()
        return

    if "предоставить доступ" in message.text.lower():
        write_new_dict_user(message)
        return

    if message.text.lower() in ['сколько рейсов', '/flight_counter', 'счетчик рейсов', "счётчик рейсов",
                                "сколько рейсов на сухом", "посчитать рейсы"]:
        if password == '':
            bot.send_message(message.chat.id,
                             "К сожалению, я не могу посчитать сколько рейсов вы отлетали, т.к. в моей базе нет Вашего логина и пароля. Если Вы хотите чтобы я за вас легко и просто посчитал количество рейсов, пришлите мне в ответном одном сообщении 4 слова через пробел по шаблону: логин ...... пароль ........")
        else:
            bot.send_message(message.chat.id, "Уже считаю Ваши рейсы. Пожалуйста, подождите...")
            result = flight_counter.parser(message.chat.id)
            bot.send_message(message.chat.id, result, reply_markup=general_menu())
            bot.send_message(157758328, f"Пользователю {surname} {name} отправлен счетчик рейсов",
                             reply_markup=general_menu())
            found_result = True
        return found_result

    if "логин" in message.text.lower() and "пароль" in message.text.lower():
        bot.send_message(157758328,
                         "Пользователь {0.first_name} @{0.username} id {0.id} прислал логин и пароль: ".format(
                             message.from_user, message.from_user) + message.text)
        bot.send_message(message.chat.id,
                         "\r \t Ожидайте, через некоторое время логин и пароль будет добавлен..\n \t"
                         "В дальнейшем, можно установить тот же самый пароль, и не придумывать каждый раз новый, "
                         "если делать это по ссылке pwd.rossiya-airlines.com (на странице авторизации OpenSky под формой "
                         "ввода логина и пароля).\n"
                         , reply_markup=survey(message.chat.id))
        return

    message.text = find_garbage(message.text)
    message.text = find_exception(message.text.lower())  # расшифровывает аббревиатуры

    if message.chat.type == 'private':  # TODO по-моему, эту строку вообще можно удалить
        if message.text.lower() in baza.greetings:
            bot.send_message(message.chat.id, 'Привет! Буду рад тебе помочь, задавай свой вопрос.',
                             reply_markup=general_menu())
            return

        if "спасибо" in message.text.lower() or message.text.lower() in baza.good_bye:
            bot.send_message(message.chat.id, choice(baza.best_wishes))
            bot.send_message(157758328,
                             f"Пользователь {name} {surname} id {message.from_user.id} поблагодарил или попрощался.",
                             reply_markup=general_menu())
            return

    if 'не подтверждать план работ' in message.text.lower() or "/confirm" in message.text.lower():
        if dict_users.users[message.chat.id]['autoconfirm'] and password == '':
            bot.send_message(message.chat.id,
                             "Если вы хотите получать план работ и подтверждать его автоматически вам нужно сообщить "
                             "ответном сообщении: логин ..... пароль .... (4 слова через пробел).",
                             reply_markup=general_menu())
            bot.send_message(157758328,
                             f'{message.chat.id} попытался включить автоматическое подтверждение плана работ, но у нас нет пароля')
        if dict_users.users[message.chat.id]['autoconfirm'] and len(dict_users.users[message.chat.id]['password']) > 0:
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

            bot.send_message(message.chat.id, "Будет так, как Вы решили.", reply_markup=confirm_question(
                message))  # TODO без этой строки никак, к ней привязываются кнопки, но выводятся сверху - пока это проблема

        if not dict_users.users[message.chat.id]['autoconfirm'] and password == '':
            bot.send_message(message.chat.id,
                             "Вам не приходят уведомления и не подтверждается план работ, так как Вы ранее не сообщали "
                             "свой логин и пароль. Если Вы хотите подтверждать план работ автоматически и получать план работ в качестве "
                             "уведомлений в телеграм, Вам нужно прислать в ответном сообщении через пробел: "
                             "логин ...... пароль ......", reply_markup=general_menu())
            bot.send_message(157758328,
                             '{} попытался включить автоматическое подтверждение плана автоматического подтверждения '
                             'плана работ но у нас нет его пароля'.format(message.chat.id))

        return

    if "не верно" in message.text.lower() or 'данные устарели' in message.text.lower() or 'неправильн' in message.text.lower() or 'неверн' in message.text.lower():
        bot.send_message(message.chat.id,
                         'Буду искренне благодарен, если предоставите актуальные данные и корректную информацию. @DeveloperAzarov')
        return

    if 'отказ от рассылки' in message.text.lower() or 'отказаться от рассылки' in message.text.lower():
        if dict_users.users[message.chat.id]['messaging']:
            bot.send_message(message.chat.id, "Хорошо, мы обязательно отключим рассылку сообщений.")
            bot.send_message(157758328, f'{message.chat.id} {name} {surname} попросил отказаться от рассылки')
        if not dict_users.users[message.chat.id]['messaging']:
            bot.send_message(message.chat.id, "Рассылка сообщений у Вас уже отключена.")
        return

    if "план работ" in message.text.lower() or "план на завтра" in message.text.lower():
        if password == '':
            plan_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
            btn = types.InlineKeyboardButton(text="Открыть план работ в OpenSky",
                                             url='https://edu.rossiya-airlines.com/workplan/')
            plan_btn.add(btn)
            bot.send_message(message.chat.id, 'Ваш логин и пароль от OpenSky отсутсвует в моей базе данных, поэтому я '
                                              'не могу запросить ваш план работ и выдать его напрямую сюда. Если Вы '
                                              'хотите легко и быстро узнавать свой план работ, а в будущем получать '
                                              'уведомления на телефон о новых рейсах - сообщите мне свой логин и пароль '
                                              'через пробел в следующем формате: \n логин ...... пароль ...... \n '
                                              '(4 слова через пробел вместо многоточия ваш логин и пароль). В тоже время, '
                                              'есть возможность нажать на кнопку, перейти и '
                                              'самостоятельно просмотреть план работ: ввести логин и пароль туда вручную.',
                             reply_markup=plan_btn)
            return
        else:
            bot.send_message(message.chat.id, "Запрос отправлен. Ожидайте несколько секунд...")
            plan = getplan.parser(message.chat.id)
            plan_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
            btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                             url='https://edu.rossiya-airlines.com/workplan/')
            plan_btn.add(btn)
            bot.send_message(message.chat.id, plan, reply_markup=plan_btn, parse_mode='html')
            bot.send_message(157758328, f"{name} {surname} получил план работ")
            return

    if '/plan' in message.text.lower():  # TODO сделать потом чтобы автоматически менял статус в словаре
        if password == '':
            bot.send_message(message.chat.id, 'Вам не приходят автоматические уведомление о предстоящем плане работ, '
                                              'так как Вы ранее не сообщили свой логин и пароль от OpenSky. Чтобы получать '
                                              'уведомления о предстоящем плане работ, Вам неообходимо сообщить свой логин и '
                                              'пароль в сообщении по следующему шаблону: логин ...... пароль ........')
        if len(password) > 0 and dict_users.users[message.chat.id]['plan_notify']:
            bot.send_message(message.chat.id,
                             'Хорошо, будет сделано. Чуть позже уведомления о предстоящем плане работ у '
                             'вас будут отключены.')
        if len(password) > 0 and not dict_users.users[message.chat.id]['plan_notify']:
            bot.send_message(message.chat.id, 'Хорошо, будет сделано. Чуть позже мы включим уведомления о предстоящем '
                                              'плане работ.')
        return

    if "мой налет" in message.text.lower():
        if password == '':
            nalet_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
            btn = types.InlineKeyboardButton(text="Просмотреть налёт в OpenSky",
                                             url='https://edu.rossiya-airlines.com/nalet/')
            nalet_btn.add(btn)
            bot.send_message(message.chat.id,
                             'Ваш логин и пароль от OpenSky отсутсвует в моей базе данных, поэтому я не могу запросить '
                             'ваш налёт и выдать его напрямую сюда в чат. Если вы хотите легко и быстро узнавать свой '
                             'налёт - в ответном сообщении отправьте свой логин и пароль через пробел в следующем '
                             'формате: \n логин ...... пароль ...... \n (вместо многоточия ваш логин и пароль). \n '
                             'Поэтому пока предлагаю нажать на кнопку, перейти и самостоятельно просмотреть Ваш налёт, '
                             'ввести логин и пароль туда вручную.', reply_markup=nalet_btn)
            return
        else:
            nalet = getnalet.parser(message.chat.id)
            nalet_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
            btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                             url='https://edu.rossiya-airlines.com/nalet/')
            nalet_btn.add(btn)
            bot.send_message(message.chat.id, nalet, reply_markup=nalet_btn, parse_mode='Markdown')
            bot.send_message(157758328, f"Пользователю {message.chat.id} {surname} {name} выдан налёт")
            return

    if "исправить ответ" in message.text.lower():
        bot.send_message(message.chat.id,
                         'В следующем сообщении еще раз коротко напишите свой вопрос и свой вариант ответа в произвольной '
                         'форме, но начинаться Ваше сообщение должно со слова "исправить", например:\n\n '
                         'Исправить: добавочный номер бухгалтерии 1017.\n\n '
                         'Пожалуйста, не забывайте пояснять к какому вопросу правка (не просто 1017).')
        return

    if 'исправить' in message.text.lower():
        correct = "Пользователь {0.first_name} @{0.username} id{0.id} предлоджил правку:\n" \
                      .format(message.from_user, message.from_user, message.from_user) + message.text[10:]
        bot.send_message(message.chat.id, 'Ваша информация успешно отправлена. После ее рассмотрения будут внесены '
                                          'соответсвующие изменения. \n Большое спасибо за Ваше участие в улучшении '
                                          'Телеграм-Бота!', reply_markup=general_menu())
        bot.send_message(157758328, correct)
        return

    if "добавить  информацию" in message.text.lower():  # TODO идея использовать метод словаря .setdefault() который будет добавлять ключ со значением в словарь при его отсутствии
        bot.send_message(message.chat.id,
                         # TODO либо создавать новый словарь и методом в питон 3.9  а|b сливать его с существующим
                         'Для добавления своей информации в телеграм-бот, начните свое сообщение со слова "добавить:". '
                         'Например:\n\nДобавить: номер телефона представителя в Москве 8(495)123-45-67',
                         reply_markup=general_menu())
        return

    if 'добавить' in message.text.lower():  # предложить заменили на добавить так как пересекается с предложить вино на английском языке
        correct = "Пользователь {0.first_name} @{0.username} id{0.id} предлоджил информацию:\n" \
                      .format(message.from_user, message.from_user, message.from_user) + message.text[8:]
        bot.send_message(message.chat.id, 'Ваша информация успешно отправлена. После ее рассмотрения будут внесены '
                                          'соответсвующие изменения. \n Большое спасибо за Ваше участие в улучшении '
                                          'Телеграм-Бота!', reply_markup=general_menu())
        bot.send_message(157758328, correct)
        return

    if "ответ пользователю" in message.text.lower():
        try:
            bot.send_message(user_id, message.text[18:], reply_markup=general_menu())
            bot.send_message(157758328, "Ответ пользователю отправлен успешно")
            return
        except:
            bot.send_message(157758328, "User_id не определен: кому отправлять сообщение - мне неизвестно.")
            return

    if 'телефон' == message.text.lower() or 'номер телефона' == message.text.lower():  # TODO наверное не очень семантично здесь размещать обработку этого запроса
        bot.send_message(message.chat.id, 'Чей именно телефон Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить чей телефон нужен")
        return  # TODO быть может га обработку подобных запросов, при выдаче ответов в строгом соответвии №1 добвлять ответы сначала в список, а потом считать, и если ответов много, то задавать уточняющий вопрос

    if 'почта' == message.text.lower():  # TODO наверное не очень семантично здесь размещать обработку этого запроса
        bot.send_message(message.chat.id, 'Чья именно почта Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить какая именно почта интересует")
        return

    if 'особенности' == message.text.lower():  # TODO наверное не очень семантично здесь размещать обработку этого запроса
        bot.send_message(message.chat.id, 'Какие именно особенности Вас инетересуют?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить какие именно особенности интересуют")
        return

    if 'виза' == message.text.lower():  # TODO наверное не очень семантично здесь размещать обработку этого запроса
        bot.send_message(message.chat.id,
                         'Какая виза? Никакой информации про визу у меня нет. Обратитесь в посольство.',
                         reply_markup=general_menu())
        bot.send_message(157758328, "Зачем-то спросили про визу.")
        return

    if (
            "аббревиатура" in message.text.lower() or "абривиатура" in message.text.lower() or "расшифровывается" in message.text.lower() or "означает" in message.text.lower() or "значит" in message.text.lower()) and (
            'команда' not in message.text.lower()):
        decrypt = find_abbreviation(message.text.lower())
        bot.send_message(message.chat.id, decrypt, reply_markup=general_menu())
        bot.send_message(157758328, f"Отправили расшифровку аббревиатуры по запросу: {message.text.lower()}")
        return

    if len(message.text) <= 2:  # было changed(message.text) - есть ли смысл вернуть чтобы не сыпал на короткие запросы
        bot.send_message(message.chat.id, 'Слишком короткий запрос. Пожалуйста, чуть подробнее, или измените запрос.',
                         reply_markup=general_menu())
        return

    # if any(baza.punctuation):

    # TODO сделать так чтобы вычленял из слов запятые и вопросительные знаки и удалял их
    """1 - ищет в строгом соответсвии"""
    if not found_result:  # СТРОГОЕ СООТВЕТСТВИЕ
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            if message.text.lower() in question:
                if 'скачать' in question:  # так надо 2 раза
                    download()  # TODO кнопки скачать и просмотреть не передаются через try except
                    found_result = True
                elif 'просмотреть' in question:  # так надо 2 раза
                    open()
                    found_result = True
                elif 'изображение' in question:  # так надо 2 раза
                    photo()
                    found_result = True
                else:  # так надо 2 раза
                    try:
                        bot.send_message(message.chat.id, baza.dictionary[id].get('answer'),
                                         reply_markup=general_menu(),
                                         parse_mode='Markdown')
                        bot.send_message(157758328,
                                         f"1 - пользователю {message.from_user.first_name} {message.from_user.last_name} " \
                                         f"@{message.from_user.username} id {message.from_user.id} выдана информация в строгом соответвии по запросу {message.text}.")
                    except Exception as exc:
                        bot.send_message(157758328, f"при запросе '{message.text}' при поиске в строгом соответствии "
                                                    f"возникала ошибка {type(exc).__name__} {exc} ")
                    found_result = True

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
            bot.send_message(message.chat.id,
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
            found_result = find_in_random_order(
                message)  # TODO при запросе: "тех учеба бизнес" и "напитков в ассортимент бизнесе" выдает ответ, но потом сообщение об ошибке ниже из exception
        except Exception as exc:
            bot.send_message(message.chat.id,
                             'Если Вам не удалось найти то, что Вы искали - попробуйте упростить свой запрос.',
                             reply_markup=general_menu(),
                             parse_mode='Markdown')
            bot.send_message(157758328,
                             f"при поиске '{message.text}' в случайном порядке с отсечением кончаний возникала ошибка "
                             f"{type(exc).__name__} {exc} ")
            found_result = True

    if not found_result:  # если ничего не найдено
        user_id = message.from_user.id
        if len(message.text) > 6:  # для отправки развернутой аббревиатуры, в случае если расшифровка была найдена, но
            bot.send_message(message.chat.id, message.text)  # подробного ответа на нее не было выдано. Расшифровывает.
        bot.send_message(message.chat.id,
                         f'\t {name}, я не знаю, что на это ответить. Попробуйте изменить или упростить свой запрос.\n'
                         '\t Если Вам что-то станет известно на этот счет, пожалуйста, поделитесь информацией и сообщите '
                         'мне, нажав кнопку "Добавить информацию" или @DeveloperAzarov\n'
                         '\n \tЕсли Вы заметите ошибки, устаревшую информцию или обнаружите факты некорректной работы '
                         'бота - просьба написать об этом также разработчику @DeveloperAzarov.\n',
                         reply_markup=general_menu())
        found_result = f"Пользователь {name} {surname} id {message.from_user.id} не смог найти запрос: {message.text}"
        bot.send_message(157758328, found_result)


bot.polling(none_stop=True)  # запускает бота
