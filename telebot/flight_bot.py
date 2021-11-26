# -*- coding: utf8 -*-
# !/usr/bin/env python3

import telebot  # чтобы работал telebot - удалить telebot, и установить Pytelegrambotapi, написанным оставить telebot
from telebot.types import InlineKeyboardMarkup
import baza
from telebot import types
from random import choice
import exception_logger
import get_weather
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
bot.send_message(157758328, f"бот перезапущен")


def general_menu():
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

    yes_no_btns = types.InlineKeyboardMarkup(row_width=1)
    yes = types.InlineKeyboardButton(text="да", callback_data="yes")
    no = types.InlineKeyboardButton(text="нет", callback_data="no")
    yes_no_btns.add(yes, no)

    bot.send_message(user_id,
                     f"`\t\t {dict_users.users[user_id]['name']}, укажите часовые пояса, в которых Вам было бы удобно получать план работ: UTC или MSK",
                     reply_markup=hours_btns)

    bot.send_message(user_id,
                     f"`\t\t {dict_users.users[user_id]['name']} подтверждать ли план работ в OpenSky автоматически при отправке его Вам в Telegram?",
                     reply_markup=confirm_plan_btns)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """Всего лишь Обработчик опроса, который сообщает разработчику результаты индивидуальных ответов пользоателя."""
    if call.message:
        if call.data == "one":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Хорошо, план работ Вам будет высылаться в указанных часовых поясах: вылет по UTC, прилёт по МСК.")
            bot.send_message(157758328, f"{call.message.chat.id} {dict_users.users[call.message.chat.id]['surname']} "
                                        f"Ответил, номер один: UTC МСК")
        if call.data == "two":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Хорошо, план работ Вам будет высылаться в указанных часовых поясах: вылет и прилёт по МСК.")
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
                                  text="Хорошо, я понял.")
            bot.send_message(157758328, f"{call.message.chat.id} {dict_users.users[call.message.chat.id]['surname']} "
                                        f"пользователь ответил да")
        if call.data == "no":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Хорошо, я понял.")
            bot.send_message(157758328, f"{call.message.chat.id} {dict_users.users[call.message.chat.id]['surname']} "
                                        f"пользователь ответил нет")


def cycle_plan_notify():
    while True:
        counter_users = 0
        users_off_list = []
        sent_plan_counter = 0
        sent_plan_list = []
        # bot.send_message(157758328, "бот начал проверку планов пользователей в атоматическом режиме")
        if time.strftime('%H:%M') == '00:00':
            time.sleep(60)
        try:
            for user_id in dict_users.users.keys():
                counter_users += 1
                try:
                    name = dict_users.users[user_id]['name']
                    surname = dict_users.users[user_id]['surname']
                    fio = f'{user_id} {surname} {name} '
                    notification = notificator.notify(user_id)  # TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС ФАЙЛА в НОТИФИКАТОРЕ!!!
                    if notification != None:  # не равно none - получили план. будет ошибка, если ему не удалось отправить ему его план - по
                        plan_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
                        btn = types.InlineKeyboardButton(text="Открыть план работ в OpenSky",
                                                         url='https://edu.rossiya-airlines.com/workplan/')
                        plan_btn.add(btn)
                        bot.send_message(user_id, notification, reply_markup=plan_btn, parse_mode='html')
                        # bot.send_message(157758328, f'отправили план {fio}')
                        # bot.send_message(157758328, notification, reply_markup=plan_btn,
                        #                  parse_mode='html')
                        sent_plan_counter += 1
                        sent_plan_list.append(fio)
                    if notification == None:  # равно None - не записан пароль пользователя, парсить не стали
                        continue  # в самом парсере тоже написано return если отсутсвует пароль в словаре
                except Exception as exc:  # если случилась ошибка при отправке сообщений пользователю
                    users_off_list.append(fio)
                    exc_event = exception_logger.writer(exc=exc,
                                                        request="отправка плана пользователю в атоматическом режиме",
                                                        user_id=user_id, fio=fio, answer='не удалось отправить план')
                    bot.send_message(157758328, exc_event)
                    bot.send_message(157758328,
                                     f'не удалось отправить план: {users_off_list}: {traceback.format_exc()}')
                    continue

            if sent_plan_counter > 0:
                bot.send_message(157758328,
                                 f'общий отчет: план выслан {sent_plan_counter} чел. {", ".join(sent_plan_list)}')
        except Exception as e:
            exception_logger.writer(exc=e, request="извлечение ключа словаря user_id при автоматической отправке плана",
                                    user_id=user_id, fio=fio, answer='поймали ошибку во внешнем try except')
            bot.send_message(157758328, f'поймали ошибку во внешнем try except: {fio}: {traceback.format_exc()}')
        # bot.send_message(157758328, "бот закончил проверку планов проводников в атоматическом режиме, уснул на 5 мин.")
        time.sleep(300)


check_plan = threading.Thread(target=cycle_plan_notify)  # TODO закомментирвоать
check_plan.start()
if not check_plan.is_alive():
    bot.send_message(157758328, f'поток проверки планов умер')
    exc_event = exception_logger.writer(exc="поток проверки планов умер", request=None, user_id=None, fio=None,
                                        answer=None)
    bot.send_message(157758328, exc_event)
    check_plan.start()


def check_permissions_for_everyone():
    document_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
    btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                     url='https://edu.rossiya-airlines.com/ready/userReady-1/')
    document_btn.add(btn)
    bot.send_message(157758328, f'Бот начал проверку допусков всех проводников.')
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
                time.sleep(3)
            except Exception:
                bot.send_message(157758328, f'{fio} не удалось уведомление о допусках: {traceback.format_exc()}')
                continue
    bot.send_message(157758328, f"бот закончил проверку допусков всех проводников")


def check_new_documents(user_id):
    document_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
    btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                     url='https://edu.rossiya-airlines.com/')
    document_btn.add(btn)
    try:
        new_document = check_news.parser(user_id)
        if new_document is not None:
            bot.send_message(user_id, new_document, reply_markup=document_btn)  # TODO закомментировать
    except Exception:
        bot.send_message(157758328,
                         f'не удалось отправить сообщение о новых документах, произошла ошибка: {traceback.format_exc()}')


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
                bot.send_message(user_id, f'{name}, {" ".join(mess[2:])}', reply_markup=general_menu())
                counter_users += 1
                bot.send_message(157758328, f"Сообщение успешно отравлено {fio}")  # TODO временно
                time.sleep(3)
            except Exception as exc:  # если случилась ошибка при отправке сообщений пользователю
                exc_event = exception_logger.writer(exc=exc, request='рассылка сообщений пользователям',
                                                    user_id=user_id, fio=fio,
                                                    answer='сообщение не удалось отправить ')
                bot.send_message(157758328, exc_event)
                users_off_list.append(fio)
                counter_errors += 1
                bot.send_message(157758328,
                                 f"сообщение не удалось отправить {fio} ошибка {traceback.format_exc()}.")  # TODO временно
    bot.send_message(157758328,
                     f"всего разослано {counter_users} чел. из {len(dict_users.users)} чел.")  # TODO временно
    return


def write_new_dict_user(message):  # TODO почему стирает весь файл?
    """Предоставление доступа пользователю: внесение новго пользователя в словарь непосредлственно сразу через чат телеграм-бота."""
    bot.send_message(157758328, "зашли в словарь юзеров.")
    try:
        mess = message.text.split()
        user_id = mess[2]
        with open('dict_users.py', 'r',
                  encoding='utf-8') as original:  # вероятно это тогда не надо если использовать методы update и функцию dict
            data = original.read()
        with open('dict_users.py', 'w', encoding='utf-8') as modified:
            modified.write(
                dict_users.users.update(user_id,
                                        dict(surname=mess[3], name=mess[4], city=str(mess[5]), link=str(mess[6]),
                                             exp_date=str(mess[7]),
                                             tab_number=str(mess[8]), password=str(mess[9]), access=mess[10],
                                             plan_notify=mess[11],
                                             autoconfirm=mess[12], messaging=mess[13], check_permissions=mess[14],
                                             time_depart=str(mess[15]), time_arrive=str(mess[16]))))

        bot.send_message(int(mess[2]),
                         f'{dict_users.users[int(mess[2])]["name"]}, Вам успешно предоставлен доступ к телеграм-боту. '
                         f'Спрашивайте, буду рад помочь! Если хотите получать уведомления на телефон об изменениях в '
                         f'плане работ, то просим Вас выслать в ответном одном сообщении через пробел логин и пароль от '
                         f'OpenSky (4 слова) по следующему шаблону: логин ....... пароль ......',
                         reply_markup=general_menu())
        bot.send_message(157758328, "внесли запись в файл")
        bot.send_message(157758328,
                         "Сообщение о предоставлении доступа пользователю отправлено успешно. \n\n ОБНОВИ СЕРВЕР!")
    except Exception as exc:
        exc_event = exception_logger.writer(exc=exc,
                                            request='Внесение нового пользователя в словарь удаленно через диалог',
                                            user_id=dict_users.users[user_id],
                                            answer='произошла ошибка при предоставлении доступа. Словарь пользователей стерся полностью.')
        bot.send_message(157758328, exc_event)
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
    if message.chat.id in dict_users.blocked.keys():
        bot.send_message(message.chat.id, 'Вам отказано в доступе.')
        bot.send_message(157758328,
                         f"Отказали в доступе {message.from_user.id} @{message.from_user.username} {message.from_user.first_name} "
                         f"{message.from_user.last_name} Пользователь спрашивал {message.text}")
        return False
    if message.chat.id in dict_users.users.keys():
        return True
    else:
        bot.send_message(message.chat.id,
                         'Прошу Вас пройти верификацию, для этого Вам необходимо отправить сюда фото своего штабного '
                         'пропуска. Нам необходимо убедиться, что вы летающий '
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

    name = dict_users.users[message.chat.id]['name']
    surname = dict_users.users[message.chat.id]['surname']
    password = dict_users.users[message.chat.id]['password']
    user_id = message.chat.id
    fio = f'{user_id} {name} {surname}'

    def photo():
        """Отправляет пользовтелю информацию с фото"""
        try:  # TODO временный try except посмотреть почему падает в этом месте
            pic = baza.dictionary[id].get('photo')
            bot.send_message(message.chat.id, baza.dictionary[id].get('answer'),
                             parse_mode='Markdown', )  # reply_markup=photo_btn
            with open(pic, 'rb') as f:
                bot.send_photo(message.chat.id, f)
        except Exception:
            bot.send_message(157758328,
                             f"Поймали ошибку на стадии выдачи изображения из функции photo() при запросе {message.text}: {traceback.format_exc()}")
        bot.send_message(157758328, "Выдали фото по запросу: " + message.text)

    def open_link():
        """Предлагает открыть сайт"""
        download_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
        btn = types.InlineKeyboardButton(text="ОТКРЫТЬ", url=baza.dictionary[id]['link'])  # .get() здесь не позволяет
        download_btn.add(btn)
        bot.send_message(message.chat.id, baza.dictionary[id].get('answer'), parse_mode='Markdown',
                         reply_markup=download_btn)
        bot.send_message(157758328, f"Пользователю {fio} предложили ОТКРЫТЬ: {message.text}")

    def download():
        """Предлагает скачать файл"""
        download_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="СКАЧАТЬ", url=baza.dictionary[id][
            'link'])  # TODO возникает ошибка в кнопку нельзя передавать содержание ключа 'link' ссылку методом .get('link') [id]['link'] возникает ошибка
        download_btn.add(btn)
        bot.send_message(message.chat.id, baza.dictionary[id].get('answer'), parse_mode='Markdown',
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
                        open_link()
                    elif 'изображение' in question:  # так надо 2 раза
                        photo()
                    else:  # так надо 2 раза
                        bot.send_message(message.chat.id, baza.dictionary[id]['answer'], reply_markup=general_menu(),
                                         parse_mode='Markdown')
                        bot.send_message(157758328,
                                         f"2.1 - Пользователю {fio} выдан ответ не в строгом соответсвии по запросу:\n{message.text}")
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
                    open_link()
                elif 'изображение' in question:  # так надо 2 раза
                    photo()
                else:  # так надо 2 раза
                    bot.send_message(message.chat.id, baza.dictionary[id]['answer'], reply_markup=general_menu(),
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
                    bot.send_message(message.chat.id, each_answer, parse_mode='Markdown',
                                     reply_markup=open_btn)
                    found_result = True
                    photo = None
                if photo:
                    photo()
                    found_result = True
                if link is None:
                    bot.send_message(message.chat.id, each_answer, reply_markup=general_menu(), parse_mode='Markdown')
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

                bot.send_message(message.chat.id, each_answer, reply_markup=general_menu(), parse_mode='Markdown')
                if link:
                    bot.send_message(message.chat.id, link, reply_markup=general_menu(), parse_mode='Markdown')
                found_result = True
                bot.send_message(157758328,
                                 f"3.2 - Пользователю {fio} выдан ответ в случайном порядке c отсчением окончаний по запросу:\n{message.text}")
                return found_result

    def confirm_question(message):
        """Сообщение с кнопками для отмены подтверждения плана работ, либо оставить всё как есть."""
        confirm_btns = types.InlineKeyboardMarkup()
        yes_off = types.InlineKeyboardButton(text="Да, отключить", callback_data="not_confirm")
        no_on = types.InlineKeyboardButton(text="Нет, подтверждать", callback_data="confirm")
        confirm_btns.add(yes_off, no_on)

        if dict_users.users[message.chat.id]['autoconfirm']:
            bot.send_message(message.chat.id,
                             f"`\t\t {dict_users.users[message.chat.id]['name']}, cейчас у Вас план работ "
                             f"подтверждается автоматически. Вы хотите отключить подтверждение ознакомления "
                             f"с планом работ?", reply_markup=confirm_btns)

    def check_permissions(user_id):
        """Проверяет сроки дейсвтвия допусков у одного конкретного проводника по индивидуальному запросу."""
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

    # global user_id
    # service_notification(message)

    if "написать пользователю по id" in message.text.lower():
        mess = message.text.split()
        try:
            bot.send_message(int(mess[4]), ' '.join(mess[5:]).capitalize(), reply_markup=general_menu())
            bot.send_message(157758328, "Сообщение пользователю отправлено успешно.")
        except Exception:
            bot.send_message(157758328, f"Пользователь не подключен к телеграм-боту.\n {traceback.format_exc()}")
        return

    if message.text.lower() in 'это не нормально это ужасно это очень плохо очень жаль кошмар':
        bot.send_message(message.chat.id, f"Я тебя прекрасно понимаю, сочувствую.")
        bot.send_message(157758328, f"{fio} отправили сочувствие в ответ на {message.text}.")
        return

    if "обратная связь" in message.text.lower():
        def feedback(message):
            if "отмена" in message.text.lower():
                bot.send_message(message.chat.id,
                                 f"Если надумаете в следующий раз что-то мне сообщить - буду рад узнать.")
                bot.send_message(157758328, f"{fio} передумал оставлять обратную связь.")
            else:
                bot.send_message(157758328, f"{fio} оставил обратную связь: \n {message.text}")

        text = f"{name}, если у Вас есть какие-то замечания, предложения, выявили факты некорректной работы бота, либо у " \
               f"Вас есть какой-то вопрос или просто что-то сообщить - пожалуйста, отправьте мне обратную связь в " \
               f"ответном сообщении. Телеграм-бот ждет вашего сообщения. Если Вы передумали оставлять обратную связь, " \
               f"отправьте слово отмена."
        msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(msg, feedback)
        return

    if "логин" in message.text.lower() and "пароль" in message.text.lower():
        bot.send_message(157758328, f"{fio} прислал логин и пароль (если в конце пароля точка, то она входит в состав "
                                    f"пароля): \n{message.text}")
        bot.send_message(message.chat.id,
                         "\r \t Логин и пароль отправлен успешно, ожидайте.\n \t"
                         "В дальнейшем, можно установить тот же самый пароль, и не придумывать каждый раз новый, "
                         "если делать это по ссылке pwd.rossiya-airlines.com (на странице авторизации OpenSky под формой "
                         "ввода логина и пароля).\n")
        bot.send_message(message.chat.id,
                         "\r \t Настройки будут активированы позже, ожидание может составить до суток.\n",
                         reply_markup=survey(message.chat.id))
        return

    for i in message.text.split():
        if 4 <= len(i) <= 6 and i.isdigit() and len(message.text.split()) == 2:
            bot.send_message(157758328,
                             f"Пользователь {message.from_user.first_name} @{message.from_user.username} id {message.from_user.id} прислал логин и пароль: {message.text}")
            bot.send_message(message.chat.id,
                             "\r \t Логин и пароль отправлен успешно, ожидайте.\n \t"
                             "В дальнейшем, можно установить тот же самый пароль, и не придумывать каждый раз новый, "
                             "если делать это по ссылке pwd.rossiya-airlines.com (на странице авторизации OpenSky под формой "
                             "ввода логина и пароля).\n", reply_markup=survey(message.chat.id))
            return

    if "сколько бортпроводников" in message.text.lower():
        bot.send_message(message.chat.id, f"К Telegram-боту подключено сейчас {len(dict_users.users)} бортпроводников.")
        return

    if '/news' in message.text.lower():
        if dict_users.users[message.chat.id]['messaging']:
            bot.send_message(message.chat.id,
                             'Автоматическое информирование о важных изменениях и новостях у вас включено по умолчанию. Как только будет важная информация - Вам будет прислано уведомление.',
                             reply_markup=general_menu())
            bot.send_message(157758328,
                             f"{fio} Сообщение об автоматически подключенном информировании о важных новстях отправлено пользователю.")
        else:
            bot.send_message(message.chat.id,
                             'Автоматическое информирование о важных изменениях у вас ранее было отключено. Чуть позже мы его включим Вам обратно, и будем прысылать сообщения при наличии важной информации.',
                             reply_markup=general_menu())
            bot.send_message(157758328,
                             f"{fio} Информирование о важной информации было отключено, попросили включить..")

        return

    if message.text.lower() in ['/donate', 'пожертвовать', 'пожертвовать на развитие', 'поддержать',
                                'перечислить деньги', 'перевести',
                                'задонатить']:
        donate_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
        btn = types.InlineKeyboardButton(text="Пожертвовать на развитие",
                                         url='https://www.tinkoff.ru/cf/2baJRGWKnrf')
        donate_btn.add(btn)
        bot.send_message(message.chat.id,
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

    if message.text.lower() in ['/document', 'проверить допуски', "сроки", "мои допуски", "проверить мои допуски"]:
        bot.send_message(message.chat.id, f"{name}, запрос отправлен, ожидайте несколько секунд...")
        check_permissions(message.chat.id)
        return

    if 'проверить допуски у всех проводников' in message.text.lower():  # TODO еще не тестировал это
        check_permissions_for_everyone()
        return

    if 'разослать сообщение' in message.text.lower():
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
            bot.send_message(157758328, f"Пользователю {fio} отправлен счетчик рейсов",
                             reply_markup=general_menu())
            found_result = True
        return found_result

    if "хорошо" in message.text.lower():

        with open('static/AnimatedSticker.tgs', 'rb') as sti:
            bot.send_sticker(message.chat.id, sti)
        return

    if "не верно" in message.text.lower() or 'данные устарели' in message.text.lower() or 'неправильн' in message.text.lower() or 'неверн' in message.text.lower():
        bot.send_message(message.chat.id,
                         'Буду искренне благодарен, если предоставите актуальные данные и корректную информацию. @DeveloperAzarov')
        return



        return

    # TODO не могу доделать "спросить пользователя"
    # if "спросить пользователя" in message.text.lower():
    #     to_whom = int(message.text.split()[2])
    #     question = message.text.split()
    #
    #     def send_question(message, to_whom):
    #         bot.send_message(157758328, f'{fio} ответил на вопрос: \n {message.text}')
    #         if message.text.lower() == 'отмена':
    #             bot.send_message(message.chat.id, 'Надумаете - пишите! Успехов!)')
    #         else:
    #             bot.send_message(message.chat.id, 'Вы успешно ответили. Спасибо.')
    #
    #     mesg = bot.send_message(to_whom, question)
    #     bot.register_next_step_handler(mesg, send_question)
    #     return

    message.text = find_punctuation(message.text)
    message.text = find_garbage(message.text)
    message.text = find_exception(message.text.lower())  # расшифровывает аббревиатуры

    if len(message.text.lower()) < 3:
        bot.send_message(message.chat.id, f'{name}, пожалуйста, уточните свой запрос.')
        return

    if message.text.lower() in baza.greetings:
        bot.send_message(message.chat.id, 'Привет! Буду рад тебе помочь, задавай свой вопрос.',
                         reply_markup=general_menu())
        return

    if "спасибо" in message.text.lower() or message.text.lower() in baza.good_bye:
        bot.send_message(message.chat.id, choice(baza.best_wishes))
        bot.send_message(157758328,
                         f"{fio} поблагодарил.", reply_markup=general_menu())
        return

    # TODO стал выдавать ошибку Unknown location; please try ~46.37093535,6.23116849372243
    # if message.text in get_weather.cities or 'погода' in message.text.lower():
    #     weather = get_weather.what_weather(message.text.lower())
    #     bot.send_message(message.chat.id, weather, reply_markup=general_menu())
    #     bot.send_message(157758328, f'{message.chat.id} отправили погоду {message.text}')

    if 'не подтверждать план работ' in message.text.lower() or "/confirm" in message.text.lower():
        if password == '':
            bot.send_message(message.chat.id,
                             "У нас нет Вашего пароля от OpenSky, "
                             "поэтому мы не сможем ни получать ваш план, ни подтверждить его автоматически. Если вы хотите получать "
                             "план работ и подтверждать его автоматически вам нужно сообщить "
                             "ответном сообщении: логин ..... пароль .... (4 слова через пробел).",
                             reply_markup=general_menu())
            bot.send_message(157758328,
                             f'{fio} попытался включить автоматическое подтверждение плана работ, но у нас нет пароля')
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
                             "уведомлений в телеграм, Вам нужно прислать в ответном сообщении 4 слова через пробел в однеу строку: "
                             "логин ...... пароль ......", reply_markup=general_menu())
            bot.send_message(157758328,
                             '{} попытался включить автоматическое подтверждение плана автоматического подтверждения '
                             'плана работ но у нас нет его пароля'.format(message.chat.id))

        return

    if 'проверить допуски всех бортпроводников' in message.text.lower():
        check_permissions_for_everyone()
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
            bot.send_message(message.chat.id,
                             f'{name}, Ваш логин и пароль от OpenSky отсутсвует в моей базе данных, поэтому я '
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
            bot.send_message(message.chat.id, f"{name}, запрос отправлен. Ожидайте несколько секунд...")
            plan = getplan.parser(message.chat.id)
            plan_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
            btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                             url='https://edu.rossiya-airlines.com/workplan/')
            plan_btn.add(btn)
            bot.send_message(message.chat.id, plan, reply_markup=plan_btn, parse_mode='html')
            bot.send_message(157758328, plan, reply_markup=plan_btn, parse_mode='html')
            bot.send_message(157758328, f"{fio} получил план работ по индивидуальному запросу")
            return

    if '/plan' in message.text.lower():  # TODO сделать потом чтобы автоматически менял статус в словаре
        if password == '':
            bot.send_message(message.chat.id, 'Вам не приходят автоматические уведомление о предстоящем плане работ, '
                                              'так как Вы ранее не сообщили свой логин и пароль от OpenSky. Чтобы получать '
                                              'уведомления о предстоящем плане работ, Вам неообходимо сообщить свой логин и '
                                              'пароль в сообщении по следующему шаблону: логин ...... пароль ........ (4 слова через пробел в одну строку)')
        if len(password) > 0 and dict_users.users[message.chat.id]['plan_notify']:
            bot.send_message(message.chat.id,
                             'Хорошо, будет сделано. Чуть позже уведомления о предстоящем плане работ у '
                             'вас будут отключены.')
        if len(password) > 0 and not dict_users.users[message.chat.id]['plan_notify']:
            bot.send_message(message.chat.id, 'Хорошо, будет сделано. Чуть позже мы включим уведомления о предстоящем '
                                              'плане работ.')
        return

    if "мой налет" in message.text.lower() or "сейчас налёт" in message.text.lower():
        if password == '':
            nalet_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
            btn = types.InlineKeyboardButton(text="Просмотреть налёт в OpenSky",
                                             url='https://edu.rossiya-airlines.com/nalet/')
            nalet_btn.add(btn)
            bot.send_message(message.chat.id,
                             'Ваш логин и пароль от OpenSky отсутсвует в моей базе данных, поэтому я не могу запросить '
                             'ваш налёт и выдать его напрямую сюда в чат. Если вы хотите легко и быстро узнавать свой '
                             'налёт - в ответном сообщении отправьте свой логин и пароль через пробел в следующем '
                             'формате: \n логин ...... пароль ...... \n (вместо многоточия ваш логин и пароль - 4 слова через пробел). \n '
                             'Поэтому пока предлагаю нажать на кнопку, перейти и самостоятельно просмотреть Ваш налёт, '
                             'ввести логин и пароль туда вручную.', reply_markup=nalet_btn)
            return
        else:
            bot.send_message(message.chat.id, f"{name}, уже считаю Ваш налёт. Пожалуйста, подождите...")
            nalet = getnalet.parser(message.chat.id)
            nalet_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
            btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                             url='https://edu.rossiya-airlines.com/nalet/')
            nalet_btn.add(btn)
            bot.send_message(message.chat.id, nalet, reply_markup=nalet_btn, parse_mode='Markdown')
            bot.send_message(157758328, f"Пользователю {fio} выдан налёт")
            return

    if 'время на сервере' in message.text.lower():
        bot.send_message(157758328, time.strftime('%d.%m.%Y %H:%M'))
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

    if 'инструктор' == message.text.lower() or 'инструктора' == message.text.lower():  # TODO наверное не очень семантично здесь размещать обработку этого запроса
        bot.send_message(message.chat.id, 'Какой именно инструктор Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить какой инструктор интересует")
        return

    if 'телефон' == message.text.lower() or 'номер телефона' == message.text.lower() or 'телефоны' in message.text.lower() or 'номера' in message.text.lower():  # TODO наверное не очень семантично здесь размещать обработку этого запроса
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

    if 'супервайзер' == message.text.lower():  # TODO наверное не очень семантично здесь размещать обработку этого запроса
        bot.send_message(message.chat.id, 'Какой именно супервайзер Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить какой именно супервайзер интересуют")
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
                    open_link()
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
        if len(message.text) > 6:  # для отправки развернутой аббревиатуры, в случае если расшифровка была найдена, но
            bot.send_message(message.chat.id, message.text)  # подробного ответа на нее не было выдано. Расшифровывает.
        bot.send_message(message.chat.id,
                         f'\t {name}, я не знаю, что на это ответить. Попробуйте изменить или упростить свой запрос.\n'
                         '\t Если Вам что-то станет известно на этот счет, пожалуйста, поделитесь информацией и сообщите '
                         'мне, нажав кнопку "Добавить информацию" или @DeveloperAzarov\n'
                         '\n \tЕсли Вы заметите ошибки, устаревшую информцию или обнаружите факты некорректной работы '
                         'бота - просьба написать об этом также разработчику @DeveloperAzarov.\n',
                         reply_markup=general_menu())
        found_result = f"Пользователь {fio} не смог найти запрос: {message.text}"
        bot.send_message(157758328, found_result)


bot.polling(none_stop=True)  # запускает бота
