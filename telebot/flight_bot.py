# !/usr/bin/env python3


import telebot  # чтобы работал telebot - удалить telebot, и установить Pytelegrambotapi, написанным оставить telebot
from telebot.types import InlineKeyboardMarkup
import baza
from telebot import types
from random import choice
from datetime import datetime, timedelta
import time
import pytz
import day_off_order
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
    btn6 = types.KeyboardButton('Заказ\nвыходных')  # 'Обратная связь')  #  'Заказ\nвыходных')
    general_menu.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return general_menu


def survey(user_id, name):
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

    city_btns = types.InlineKeyboardMarkup(row_width=1)
    moscow = types.InlineKeyboardButton(text="Москва", callback_data="moscow")
    SaintPetersburg = types.InlineKeyboardButton(text="Санкт-Петербург", callback_data="SaintPetersburg")
    ekaterinburg = types.InlineKeyboardButton(text="Екатеринбург", callback_data="ekaterinburg")
    city_btns.add(moscow, SaintPetersburg, ekaterinburg)

    position_btns = types.InlineKeyboardMarkup(row_width=3)
    purser = types.InlineKeyboardButton(text="СБ", callback_data="purser")
    bs = types.InlineKeyboardButton(text="BS", callback_data="bs")
    bp = types.InlineKeyboardButton(text="БП", callback_data="bp")
    position_btns.add(purser, bs, bp)

    osl_doc_btns = types.InlineKeyboardMarkup(row_width=1)
    yes_messaging = types.InlineKeyboardButton(text="Да, информировать", callback_data="yes_messaging")
    not_messaging = types.InlineKeyboardButton(text="Нет, не информирвоать", callback_data="not_messaging")
    osl_doc_btns.add(yes_messaging, not_messaging)

    bot.send_message(user_id,
                     f"`\t\t {name}, укажите часовые пояса, в которых Вам было бы удобно получать план работ: UTC или MSK",
                     reply_markup=hours_btns)

    bot.send_message(user_id,
                     f"`\t\t Подтверждать ли план работ в OpenSky автоматически при отправке уведомления Вам в Telegram?",
                     reply_markup=confirm_plan_btns)

    bot.send_message(user_id,
                     f"`\t\t Хотите ли Вы получать уведомления с планом работ в ночное время с 00:00 до 7:00?",
                     reply_markup=day_nights_btns)

    bot.send_message(user_id, f"`\t\t Укажите Ваш город локации", reply_markup=city_btns)
    bot.send_message(user_id, f"`\t\t Выберите Вашу должность в экипаже", reply_markup=position_btns)
    bot.send_message(user_id, f"`\t\t Хотите ли Вы получать уведомления о новых документах в OpenSky?",
                     reply_markup=osl_doc_btns)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """Всего лишь Обработчик опроса, который сообщает разработчику результаты индивидуальных ответов пользоателя."""
    tab_number = handler_db.get_tab_number(call.message.chat.id)
    name_surname = handler_db.get_name_surname(call.message.chat.id)
    name = name_surname.split()[0]
    surname = name_surname.split()[1]

    if call.message:
        if call.data == "one":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="План работ Вам будет высылаться в указанных часовых поясах: вылет по UTC, прилёт по МСК.")
            try:
                mess = 'utc_start msk'
                time_depart = handler_db.insert_utc_msk(mess, call.message.chat.id)
                if time_depart:
                    bot.send_message(157758328, f"{call.message.chat.id} часовые пояса установлены успешно: UTC МСК")
                    return
            except Exception as exc:
                bot.send_message(157758328, f"!!! проблема с установкой часовых поясов у пользователя "
                                            f"{call.message.chat.id}: часовые пояса установлены успешно: UTC МСК")

        if call.data == "two":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="План работ Вам будет высылаться в указанных часовых поясах: вылет и прилёт по МСК.")
            try:
                mess = 'msk_start msk'
                time_depart = handler_db.insert_utc_msk(mess, call.message.chat.id)
                if time_depart:
                    bot.send_message(157758328, f"{call.message.chat.id} часовые пояса установлены успешно: МСК МСК")
            except Exception as exc:
                bot.send_message(157758328,
                                 f"!!! проблема с установкой часовых поясов у пользователя {call.message.chat.id}: UTC МСК")

        if call.data == "confirm":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Ваш план работ будет подтверждаться автоматически при отправке его Вам в Telegram.")
            try:
                confirm = True
                confirm = handler_db.insert_confirm(confirm, call.message.chat.id)
                if confirm is not None or confirm != '':
                    bot.send_message(157758328, f"{call.message.chat.id} confirm true установлено успешно")
            except Exception as exc:
                bot.send_message(157758328, f"!!! проблема с установкой confirm true {call.message.chat.id}\n\n{exc}")

        if call.data == "not_confirm":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Ваш план работ не будет подтверждаться автоматически при отправке его Вам в Telegram.")
            try:
                confirm = False
                confirm = handler_db.insert_confirm(confirm, call.message.chat.id)
                if confirm is not None or confirm != '':
                    bot.send_message(157758328, f"{call.message.chat.id} confirm False установлено успешно")
            except Exception as exc:
                bot.send_message(157758328, f"!!! проблема с установкой confirm False {call.message.chat.id}\n\n{exc}")

        if call.data == "yes":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Отправка уведомлений по ночам разрешена.")
            try:
                night_notify = True
                night_notify = handler_db.update_night_notify(night_notify, call.message.chat.id)
                if night_notify is not None or night_notify != '':
                    bot.send_message(157758328, f"{call.message.chat.id} параметр night_notify True установлен успешно")
            except Exception as exc:
                bot.send_message(157758328,
                                 f"!!! проблема с установкой night_notify True {call.message.chat.id}\n\n{exc}")

        if call.data == "no":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Отправка уведомлений по ночам запрещена.")
            try:
                night_notify = False
                night_notify = handler_db.update_night_notify(night_notify, call.message.chat.id)
                if night_notify is not None or night_notify != '':
                    bot.send_message(157758328,
                                     f"{call.message.chat.id} параметр night_notify False установлен успешно")
            except Exception as exc:
                bot.send_message(157758328,
                                 f"!!! проблема с установкой night_notify False {call.message.chat.id}\n\n{exc}")

        if call.data == "purser":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Должность СБ внесена успешно.")
            try:
                position_status = handler_db.update_position(call.message.chat.id, 'СБ')
                if position_status is not None or position_status != '':
                    bot.send_message(157758328,
                                     f"{call.message.chat.id} должность СБ сохранена успешно")
            except Exception as exc:
                bot.send_message(157758328,
                                 f"!!! проблема с установкой position СБ {call.message.chat.id}\n\n{exc}")

        if call.data == "bs":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Должность BS внесена успешно.")
            try:
                position_status = handler_db.update_position(call.message.chat.id, 'BS')
                if position_status is not None or position_status != '':
                    bot.send_message(157758328,
                                     f"{call.message.chat.id} должность BS сохранена успешно")
            except Exception as exc:
                bot.send_message(157758328,
                                 f"!!! проблема с установкой position BS {call.message.chat.id}\n\n{exc}")

        if call.data == "bp":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Должность БП внесена успешно.")
            try:
                position_status = handler_db.update_position(call.message.chat.id, 'БП')
                if position_status is not None or position_status != '':
                    bot.send_message(157758328,
                                     f"{call.message.chat.id} должность БП сохранена успешно")
            except Exception as exc:
                bot.send_message(157758328,
                                 f"!!! проблема с установкой position БП {call.message.chat.id}\n\n{exc}")

        if call.data == "moscow":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="город Москва записан успешно.")
            try:
                city_status = handler_db.update_city("Москва", call.message.chat.id)
                if city_status is not None or city_status != '':
                    bot.send_message(157758328,
                                     f"{call.message.chat.id} город Москва сохранен успешно")
            except Exception as exc:
                bot.send_message(157758328,
                                 f"!!! проблема с установкой city Москва {call.message.chat.id}\n\n{exc}")

        if call.data == "SaintPetersburg":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="город Санкт-Петербург записан успешно.")
            try:
                city_status = handler_db.update_city("Санкт-Петербург", call.message.chat.id)
                if city_status is not None or city_status != '':
                    bot.send_message(157758328,
                                     f"{call.message.chat.id} город Санкт-Петербург сохранен успешно")
            except Exception as exc:
                bot.send_message(157758328,
                                 f"!!! проблема с установкой city Санкт-Петербург {call.message.chat.id}\n\n{exc}")

        if call.data == "ekaterinburg":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="город Екатеринбург записан успешно.")
            try:
                city_status = handler_db.update_city("Екатеринбург", call.message.chat.id)
                if city_status is not None or city_status != '':
                    bot.send_message(157758328,
                                     f"{call.message.chat.id} город Екатеринбург сохранен успешно")
            except Exception as exc:
                bot.send_message(157758328,
                                 f"!!! проблема с установкой city Екатеринбург {call.message.chat.id}\n\n{exc}")

        if call.data == "yes_messaging":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Информирование о важной информации подключено.")
            try:
                messaging_status = handler_db.update_messaging(True, call.message.chat.id)
                if messaging_status is not None or messaging_status != '':
                    bot.send_message(157758328,
                                     f"{call.message.chat.id} Информирование о важной информации подключено успешно")
            except Exception as exc:
                bot.send_message(157758328,
                                 f"!!! проблема с установкой yes_messaging  {call.message.chat.id}\n\n{exc}")

        if call.data == "not_messaging":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Информирование о важной информации отключено.")
            try:
                messaging_status = handler_db.update_messaging(False, call.message.chat.id)
                if messaging_status is not None or messaging_status != '':
                    bot.send_message(157758328,
                                     f"{call.message.chat.id} Информирование о важной информации отключено")
            except Exception as exc:
                bot.send_message(157758328,
                                 f"!!! проблема с установкой not_messaging  {call.message.chat.id}\n\n{exc}")


check_plan = threading.Thread(target=check_plan.cycle_plan_notify)  # TODO закомментирвоать
check_plan.start()
if not check_plan.is_alive():
    bot.send_message(157758328, f'поток проверки планов умер')
    check_plan.start()
    exc_event = exception_logger.writer(exc="поток проверки планов умер", request=None, fio=None,
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
        user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, \
        autoconfirm, time_depart = handler_db.fetch_user_for_plan(user_id)
        fio = f'{user_id} {surname} {name} '
        if password and messaging and password != '0':  # TODO сделать в базе всем одинаково
            try:
                documents_info = get_permissions.parser(user_id, tab_number, password, name)
                bot.send_message(user_id, documents_info, reply_markup=document_btn)
                bot.send_message(157758328, f'Пользователю {fio} отправлен сообщение об истекающих допусках.')
                bot.send_message(157758328, documents_info, reply_markup=document_btn)  # TODO закомментировать
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
        user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, \
        autoconfirm, time_depart = handler_db.fetch_user_for_plan(user_id)
        fio = f'{user_id} {surname} {name} '
        if password and password != '0':  # TODO сделать в базе всем одинаково
            try:
                nalet_info = getnalet.parser(user_id, tab_number, password)
                if "Не удалось" in nalet_info:
                    continue
                else:
                    bot.send_message(user_id, f'{name}, у Вас в этом месяце\n{nalet_info}', reply_markup=nalet_btn)
                    bot.send_message(157758328, f'Пользователю {fio} отправлен налёт.')
                    counter += 1
                    time.sleep(3)
            except Exception as exc:
                bot.send_message(157758328, f'{fio} не удалось отправить налёт: {exc}')
                continue
    bot.send_message(157758328, f"бот закончил проверку налёта всех проводников. Отправлено {counter} уведомлений.")


def check_new_documents(user_id):
    """Проверяет выложены ли новые документы в OpenSky для конкретного пользователя"""
    document_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
    btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky", url='https://edu.rossiya-airlines.com/')
    document_btn.add(btn)

    user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, \
    autoconfirm, time_depart = handler_db.fetch_user_for_plan(user_id)
    fio = f'{user_id} {surname} {name} '

    if password and password != '0':  # TODO сделать в базе всем одинаково
        try:
            new_document = check_news.parser(tab_number, password)
            if new_document is not None:
                bot.send_message(user_id, new_document, reply_markup=document_btn)  # TODO закомментировать
        except Exception:
            bot.send_message(user_id, f'{name}, у вас слишком много неподтвержденных документов в Opensky.',
                             reply_markup=document_btn)
            bot.send_message(157758328,
                             f'{fio} не удалось отправить сообщение о новых документах, произошла ошибка: '
                             f'{traceback.format_exc()}')


def messaging_process(message):
    """При принудительном вызове функции рассылает всем сообщения со скоростью 1 человек в 3 секунды"""
    mess = message.text.split()
    counter_users = 0
    for user_id in list_id:
        user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, \
        autoconfirm, time_depart = handler_db.fetch_user_for_plan(user_id)
        fio = f'{user_id} {name} {surname}'
        if messaging:
            try:
                # with open('static/book.png', 'rb') as f:
                #     text = "подпись к фотографии"
                #     bot.send_photo(user_id, f, caption=text)
                bot.send_message(user_id, f'{name}, {" ".join(mess[2:])}', reply_markup=general_menu())
                counter_users += 1
                bot.send_message(157758328, f"Сообщение успешно отравлено {fio}")  # TODO временно
                time.sleep(3)
            except Exception as exc:  # если случилась ошибка при отправке сообщений пользователю
                exc_event = exception_logger.writer(exc=exc, request='рассылка сообщений пользователям',
                                                    fio=fio, answer='сообщение не удалось отправить ')
                bot.send_message(157758328, exc_event)
                bot.send_message(157758328,
                                 f"сообщение не удалось отправить {fio} ошибка {exc}.")  # TODO временно
    bot.send_message(157758328,
                     f"всего разослано {counter_users} чел. из {len(dict_users.users)} чел.")  # TODO временно
    return


def write_new_dict_user(message):  # TODO ВЫНЕСТИ В ОТДЕЛЬНЫЙ ФАЙЛ
    """Предоставление доступа пользователю: внесение новго пользователя в базу данных general.db, таблицу users
    непосредственно сразу через чат телеграм-бота. поступающую строку типа: 157758328 Азаров Дмитрий... делит на список,
    вносит в базу, затем делает запрос в базу, на основании которого выдает ответ, успешно внесен человек в базу или нет"""
    try:
        mess = message.text.split('\n')
        user_id = int(mess[1])  # 0 - предоставить доступ, 1 - user_id, 2 - surname
        surname = mess[2]
        name = mess[3]
        city = mess[4]
        link = mess[5]
        exp_date = mess[6]
        tab_number = mess[7]
        password = mess[8]
        access = mess[9]
        messaging = mess[10]
        check_permissions = mess[11]
        night_notify = mess[12]
        plan_notify = mess[13]
        autoconfirm = mess[14]
        time_depart = mess[15]
        time_arrive = mess[16]
    except Exception as exc:
        bot.send_message(157758328,
                         f"Проблема с извлечением слов из полученной строки на вход: {mess} в general.db:\n\n {exc}\n\n "
                         f"Новый пользователь не был добавлен в БД.")
        return
    try:
        handler_db.add_new_user_to_db_users(user_id, surname, name, city, link, exp_date, tab_number, password, access,
                                            messaging, check_permissions, night_notify, plan_notify, autoconfirm,
                                            time_depart, time_arrive)
    except Exception as exc:
        bot.send_message(157758328, f"Проблема с добавлением пользователя {surname} в general.db:\n {exc}")
        bot.send_message(157758328, f"последние внесенные пользвоатели в базе данных:")
        last_three_users_in_db = handler_db.get_three_last()
        for i in last_three_users_in_db:
            bot.send_message(157758328, i[2])
        exc_event = exception_logger.writer(exc=exc,
                                            request='Добавление нового пользователя в словарь удаленно',
                                            fio=f'{user_id} {surname}',
                                            answer='произошла ошибка при предоставлении доступа.')
        bot.send_message(157758328, exc_event)
        bot.send_message(157758328, f"произошла ошибка при предоставлении доступа {exc}.")
        return
    try:
        user_id_from_db = handler_db.check_user_id_in_db(user_id)
    except Exception as exc:
        bot.send_message(157758328,
                         f"не удалось проверить успешность добавления пользователю в базу. Возникла ошибка:\n\n {exc}.")
        return
    if user_id == user_id_from_db:
        bot.send_message(user_id,
                         f'\t    {name}, Вам успешно предоставлен доступ к телеграм-боту. \n'
                         f'    Спрашивайте, буду рад помочь! \n'
                         f'    Если хотите получать уведомления о новых рейсах, смотреть налет и следить за допусками,'
                         f' то пришлите в ответном одном сообщении через пробел логин и пароль от '
                         f'OpenSky (4 слова через пробел) по следующему шаблону: логин ....... пароль ......',
                         reply_markup=general_menu())
        bot.send_message(157758328, "Сообщение о предоставлении доступа пользователю отправлено успешно.")
        return
    else:
        bot.send_message(157758328, f"Пользователь {user_id} {surname} {name} отсутсвует в базе general.db")
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
                         'Вам необходимо пройти верификацию пользователя, для этого отправьте сюда фото своего штабного '
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
                     '\t Это служебный Telegram-бот для бортпроводников АК "Россия".'
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

    user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, \
    autoconfirm, time_depart = handler_db.fetch_user_for_plan(message.chat.id)
    fio = f'{user_id} {name} {surname}'

    if message.text.lower() in "обратная связь /feedback пригласить человека Написать разработчику автору азарову программисту справка как " \
                               "сообщить о проблеме ошибке неточности устаревшей информации работает неправильно /write":
        def feedback(message):
            if "отмена" in message.text.lower():
                bot.send_message(message.chat.id,
                                 f"Если надумаете в следующий раз что-то мне сообщить - буду рад узнать.")
                bot.send_message(157758328, f"{fio} передумал оставлять обратную связь.")
            else:
                bot.send_message(157758328, f"{fio} оставил обратную связь: \n {message.text}")

        text = f" Если у Вас есть какие-то замечания, предложения или вопрос - отправьте мне обратную связь в " \
               f"ответном сообщении. Телеграм-бот ждет вашего сообщения. Если Вы передумали оставлять обратную связь, " \
               f"отправьте слово отмена."
        msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(msg, feedback)
        return

    def get_photo():
        """Отправляет пользовтелю информацию с фото"""
        try:  # TODO временный try except посмотреть почему падает в этом месте
            pic = baza.dictionary[id].get('photo')
            text = baza.dictionary[id].get('answer')
            with open(pic, 'rb') as f:
                bot.send_photo(user_id, f, caption=text, parse_mode='Markdown')
        except Exception as exc:
            bot.send_message(157758328,
                             f"Ошибка при отправке изображения из функции get_photo() при запросе {message.text}: {exc}")
        bot.send_message(157758328, "Выдали фото по запросу: " + message.text)

    def get_photo_3_1(photo, answer):
        """Функция для поиска 3.1. в случайном порядке. Отправляет пользовтелю информацию с фото"""
        try:  # TODO временный try except посмотреть почему падает в этом месте
            pic = photo
            if pic is None:
                pic = photo
            with open(pic, 'rb') as f:
                bot.send_photo(user_id, f, caption=answer, parse_mode='Markdown')
        except Exception as exc:
            bot.send_message(157758328,
                             f"Ошибка при отправке изображения из функции get_photo() при запросе {message.text}: {exc}")
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
        """2.1 - Ищет не в строгом соответсвии."""
        if 4 <= len(message.text) <= 5:
            bot.send_message(user_id, "Пожалуйста, уточните свой вопрос", reply_markup=general_menu())
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
                        get_photo()
                    else:  # так надо 2 раза
                        bot.send_message(user_id, baza.dictionary[id]['answer'], reply_markup=general_menu(),
                                         parse_mode='Markdown')
                        bot.send_message(157758328, f"2.1 - Пользователю {fio} выдан ответ не в строгом соответсвии "
                                                    f"по запросу:\n{message.text}")
                    found_result = True
                    return found_result

    def find_non_strict_accordance_2(message):
        """2.2 - Ищет не в строгом соответсвии."""
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            if changed(message.text) in changed(question):
                if 'скачать' in baza.dictionary[id]['question'].lower():  # так надо 2 раза
                    download()
                elif 'просмотреть' in question:  # так надо 2 раза
                    open_link()
                elif 'изображение' in question:  # так надо 2 раза
                    get_photo()
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
                    get_photo_3_1(photo, each_answer)
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
            bot.send_message(message.chat.id,
                             f"{name}, вероятно, на Ваш вопрос нет однозначного ответа. Пожалуйста, уточните свой вопрос.")
            bot.send_message(157758328, f"4 - Пользователю {fio} выдан ответ, что найдено слишком много ответов при "
                                        f"запросе:\n{message.text}")
            return

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
                             "........  Менять старый пароль каждый раз не нужно, достаточно ввести старый пароль в "
                             "графу нового пароля по ссылке pwd.rossiya-airlines.com'.", reply_markup=document_btn)
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

    def check_true_date(message):
        """Проверяет насколько корректно ввдена дата. Возвращает False Либо дату"""
        days = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31, }

        current_datetime = time.strftime('%d.%m.%Y %H:%M')
        dt_utc = datetime.strptime(current_datetime, '%d.%m.%Y %H:%M').replace(tzinfo=pytz.utc)
        dt = dt_utc.astimezone(pytz.utc) + timedelta(days=60)
        future_month = int(dt.month)
        future_year = str(dt.year)[2:]
        day = message.text

        if '.' in message.text:
            day = message.text.split('.')[0]
            requested_month = message.text.split('.')[1]
            if requested_month == '' or int(requested_month) != future_month:
                return False
        if '/' in message.text:
            day = message.text.split('/')[0]
        if ',' in message.text:
            day = message.text.split(',')[0]
        if ' ' in message.text:
            day = message.text.split(' ')[0]
        if len(day) < 2:
            day = '0' + day
        if not day.isdigit():
            return False
        if len(day) > 2 or 0 <= int(day) > 31:
            return False
        if int(day) > days[future_month]:
            return False
        else:
            if len(str(future_month)) < 2:
                future_month = '0' + str(future_month)
            return f'{day}.{future_month}.{future_year}'

    found_result = False

    # global user_id
    # service_notification(message)

    if "выйти" in message.text.lower():
        bot.send_message(message.chat.id, "Хорошего дня! Если что - обращайтесь.", reply_markup=general_menu())
        return

    if "написать по id" in message.text.lower():
        mess = message.text.split()
        try:
            bot.send_message(int(mess[3]), ' '.join(mess[4:]).capitalize(), reply_markup=general_menu())
            bot.send_message(157758328, "Сообщение пользователю отправлено успешно.")
        except Exception:
            bot.send_message(157758328, f"Пользователь не подключен к телеграм-боту.\n {traceback.format_exc()}")
        return

    if message.text.lower() in ['сколько рейсов', '/flight_counter', 'счетчик рейсов', "счётчик рейсов",
                                "сколько рейсов на сухом", "посчитать рейсы"]:
        if password == '' or not password or password == '0':
            bot.send_message(user_id,
                             "К сожалению, я не могу посчитать сколько рейсов вы отлетали, т.к. в моей базе нет "
                             "Вашего логина и пароля. Если Вы хотите чтобы я за вас легко и просто посчитал "
                             "количество рейсов, пришлите мне в ответном одном сообщении 4 слова через пробел по "
                             "шаблону: логин ...... пароль ........  Менять старый пароль каждый раз не нужно, достаточно "
                             "ввести старый пароль в графу нового пароля по ссылке pwd.rossiya-airlines.com")
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

    if message.text.lower() in "план на завтра мой план работ /getplan мой наряд":
        if password == '' or not password or password == '0':
            plan_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
            btn = types.InlineKeyboardButton(text="Открыть план работ в OpenSky",
                                             url='https://edu.rossiya-airlines.com/workplan/')
            plan_btn.add(btn)
            bot.send_message(user_id,
                             f'{name}, Ваш логин и пароль от OpenSky отсутсвует в моей базе данных, поэтому я '
                             'не могу запросить ваш план работ и выдать его напрямую сюда. Если Вы '
                             'хотите быстро узнавать свой план работ, получать '
                             'уведомления о новых рейсах - сообщите свой логин и пароль '
                             'через пробел в следующем формате: \n логин ...... пароль ...... \n '
                             '(4 слова через пробел, вместо многоточия ваш логин и пароль). \n Менять старый пароль каждый раз не '
                             'нужно, достаточно ввести старый пароль в графу нового пароля по ссылке pwd.rossiya-airlines.com)',
                             reply_markup=plan_btn)
            return
        else:
            bot.send_message(user_id, f"{name}, запрос отправлен. Ожидайте несколько секунд...")
            plan = getplan.parser(user_id, tab_number, password, autoconfirm, time_depart)
            plan_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
            btn = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky",
                                             url='https://edu.rossiya-airlines.com/workplan/')
            plan_btn.add(btn)
            bot.send_message(user_id, plan, reply_markup=plan_btn, parse_mode='html')
            with open("/usr/local/bin/bot/plans/plans" + str(user_id) + ".txt", 'w', encoding='utf-8') as modified:
                modified.write(plan)
            # bot.send_message(157758328, plan, parse_mode='html')
            # bot.send_message(157758328, f"{fio} получил план работ по индивидуальному запросу, изменения должны были быть записаны проверь")
            return

    if '/plan' in message.text.lower():  # TODO сделать потом чтобы автоматически менял статус в словаре
        if not password:
            bot.send_message(user_id, 'Вам не приходят автоматические уведомление о предстоящем плане работ, '
                                      'так как Вы ранее не сообщили свой логин и пароль от OpenSky. Чтобы получать '
                                      'уведомления о предстоящем плане работ, Вам неообходимо сообщить свой логин и '
                                      'пароль в сообщении по следующему шаблону: логин ...... пароль ........ '
                                      '(4 слова через пробел в одну строку). Менять старый пароль каждый раз не нужно, '
                                      'достаточно ввести старый пароль в графу нового пароля по ссылке pwd.rossiya-airlines.com')
        if len(password) >= 1 and plan_notify:
            if plan_notify:
                bot.send_message(user_id, "Хорошо, мы обязательно отключим уведомления о плане работ.")
                bot.send_message(157758328, f'{user_id} {name} {surname} попросил отключить уведомления о плане работ')
                prohibited = False
                result = handler_db.update_plan_notify(prohibited, user_id)
                if result is not None:
                    bot.send_message(user_id, "Рассылка уведомлений о плане работ отключена.")
                    bot.send_message(157758328, f'{fio} рассылка сообщений отключена автоматически.')
                    return
    if not plan_notify:
        bot.send_message(user_id, "Хорошо, мы обязательно включим уведомления о плане работ.")
        bot.send_message(157758328, f'{user_id} {name} {surname} попросил включить уведомления о плане работ')
        allowed = True
        result = handler_db.update_plan_notify(allowed, user_id)
        if result is not None:
            bot.send_message(user_id, "Рассылка уведомлений о плане работ включена.")
            bot.send_message(157758328, f'{fio} рассылка уведомлений о плане работ включена автоматически.')
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
                             ' Менять старый пароль каждый раз не нужно, достаточно ввести старый пароль в графу нового '
                             'пароля по ссылке pwd.rossiya-airlines.com', reply_markup=nalet_btn)
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

    if "изменить город пользователя" in message.text.lower():
        user = message.text.split()[-2]
        city = message.text.split()[-1]
        handler_db.update_city(city, user)
        result = handler_db.select_all_data_of_person(user)
        bot.send_message(157758328, result)
        return

    if "удалить выходной" in message.text.lower():
        user_id = message.chat.id
        message.text = message.text.split()[2]
        date = check_true_date(message)
        tab_number = handler_db.get_tab_number(user_id)
        handler_db.delete_date(tab_number, date)  # TODO доделать удаление выходного
        bot.send_message(user_id, f"Выходной день {date} отменен.", reply_markup=general_menu())
        return

    if "добавить должность" in message.text.lower():
        user = message.text.split()[-2]
        position = message.text.split()[-1]
        handler_db.update_position(user_id, position)
        result = handler_db.select_all_data_of_person(user)
        bot.send_message(157758328, result)
        return

    if "просмотреть данные пользователя" in message.text.lower():  # ! РАБОТАЕТ!
        user = message.text.split()
        result = handler_db.select_all_data_of_person(user[-1])
        bot.send_message(157758328, result)
        return

    if "удалить пользователя" in message.text.lower():
        user = message.text.split()
        handler_db.delete_user_from_db(user[-1])
        result = handler_db.select_all_data_of_person(user[-1])
        bot.send_message(157758328, result)
        return

    if "сколько бортпроводников" in message.text.lower():
        bot.send_message(user_id, f"К Telegram-боту подключено сейчас {handler_db.count_users()} бортпроводников.")
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
                         'и требует времени и дополнительных расходов. Есть еще много идей, которые хочется '
                         'реализовать. \n\n'
                         '*Содержание и обслуживание телеграм бота:*\n'
                         '1. *Доменное имя* = 1000 руб./год;\n'
                         '2. *Хостинг* - аренда сервера = 3600 руб./год;\n'
                         '3. *SSL-секртификат* безопасности для защищенной передачи данных = 2900 руб./год;\n'
                         '*Вознаграждения:*\n'
                         '4. *За найденные ошибки, новую информацию, приведенного друга* по 100 руб пользователю за каждый факт = 400 руб./мес'
                         '5. *Аутсорсинг* - переодическое привлечение более опытных программистов 1-2 раза в месяц, час работы их стоит = 1000 руб./час.\n'
                         'Да, я и так практически всё свободное время занят программированием, исправлением ошибок, '
                         'занесением информации, но бывает, что не все сам могу разрешить и приходится '
                         'привлекать других программистов.\n\n'
                         '*Итого обслуживание телеграм-бота обходится примерно в 2500 руб/мес.*\n\n'
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
            bot.send_message(157758328, "предоставить доступ\n"
                                        "user_id\n"
                                        "surname\n"
                                        "name\n"
                                        "Санкт-Петербург\n"
                                        "@username\n"
                                        "exp_date\n"
                                        "tab_number\n"
                                        "password_стереть\n"
                                        "1\n"
                                        "1\n"
                                        "1\n"
                                        "1\n"
                                        "1\n"
                                        "0\n"
                                        "msk_start\n"
                                        "msk")
            return
        else:
            bot.send_message(157758328, "вызвали write_new_dict_user внести бользователя в general_db")
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

    if "поменять пользователю" in message.text.lower():
        if len(message.text.split()) == 2:
            bot.send_message(157758328,
                             'поменять пользователю\n'
                             'user_id\n'
                             'пароль\n'
                             '_______\n'
                             '#######')
            return
        else:
            mess = message.text.split('\n')
            user_id = mess[1]
            password = mess[3]
            handler_db.update_password_for_user(password, user_id)
            result = handler_db.select_all_data_of_person(user_id)
            bot.send_message(157758328, result)
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

    if len(message.text.split()) >= 2:
        mess_list = message.text.split()
        tab_number = mess_list[0]
        password = mess_list[1]
    if 4 <= len(tab_number) <= 6 and tab_number.isdigit() and len(message.text.split()) == 2:
        request = (tab_number, password)
        result = handler_db.insert_login_password(request, user_id)
        if result:
            bot.send_message(user_id, "\r \t Логин и пароль отправлен успешно, ожидайте.\n",
                             reply_markup=survey(user_id, name))
            bot.send_message(157758328,
                             f"{fio} Самостоятельно успешно добавил логин {tab_number} и пароль {password} в базу.")
            return
        else:
            bot.send_message(157758328, f"{fio} прислал логин и пароль: \n {message.text}")
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
                                 reply_markup=survey(user_id, name))
                bot.send_message(157758328,
                                 f"{fio} Самостоятельно успешно добавил логин {tab_number} и пароль {password} в базу.")
                return
        else:
            bot.send_message(157758328, f"{fio} прислал логин и пароль: \n {message.text}")
            return

    # TODO ВЫХОДНЫЕ №№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№

    if message.text.lower() in "/day_order заказ\nвыходных заказ выходных заказать выходной":
        bot.send_message(user_id, f'Функция разрабатывается для бортпроводников из Санкт-Петербурга, работает в '
                                  f'тестовом режиме, фактически заказы пока не принимаются.')

        def select_action():
            """Основаня клавиатура внизу экрана: выбор первичного дейсвтия заказать выходной, просмотреть свободные дни, отменить"""
            select_action = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            btn1 = types.KeyboardButton('Заказать\nвыходной')
            btn2 = types.KeyboardButton('Свободные\nдаты')
            btn3 = types.KeyboardButton('Отменить\nвыходной')
            btn4 = types.KeyboardButton('Заказанные даты')
            btn5 = types.KeyboardButton('Выйти')
            select_action.add(btn1, btn2, btn3, btn4, btn5)
            return select_action

        def select_action_in_cancel():
            """При выдаче заказанных дней спрашивает что сдлеать с заказанными днями"""
            select_action_in_cancel_btns = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            btn1 = types.KeyboardButton('Заказать\nвыходной')
            btn3 = types.KeyboardButton('Отменить\nвыходной')
            btn5 = types.KeyboardButton('Выйти')
            select_action_in_cancel_btns.add(btn1, btn3, btn5)
            return select_action_in_cancel_btns

        def position():
            position_btn = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            sb = types.KeyboardButton('СБ')
            bs = types.KeyboardButton('BS')
            simple = types.KeyboardButton('БП')
            position_btn.add(sb, bs, simple)
            return position_btn

        def otdelenie():
            otdelenie_btn = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            oke1 = types.KeyboardButton('OKЭ 1')
            oke2 = types.KeyboardButton('ОКЭ 2')
            otdelenie_btn.add(oke1, oke2)
            return otdelenie_btn

        ask_order_or_cancel = "Вы хотите заказать выходной или отменить ранее заказанный выходной?"
        ask_position = 'Укажите Вашу должность'
        ask_date = 'На какую дату Вы бы хотели заказать выходной?'
        ask_comment = 'Оставьте комментарий, для чего Вам нужен выходной?'
        ask_oke = "Укажите Ваше отделение"

        # функция check_true_date вынесена в общий код строка 831

        def check_true_position(message):
            """Проверяет правильность введеной позиции"""
            if message.text.lower() in "бортпроводник бп рядовой провод проводник":
                return "БП"
            if message.text.lower() in "бизнес класс бизнес-класс bs":
                return "BS"
            if message.text.lower() in "сб старший бортпроводник":
                return "СБ"

        def start_20(message):
            """удаляет заказанные ранее выходные"""
            pass

        def start_04(message):
            """Проверяет дату на корректность, заносит дату в словарь, спрашивает комментарий ...."""
            date = check_true_date(message)
            oke = order_dict[message.chat.id][ask_oke]
            tab_number = handler_db.get_tab_number(message.chat.id)
            handler_db.update_oke(tab_number, oke)

            two_days_status = handler_db.check_two_days_in_row(date=date, tab_number=tab_number)

            position = order_dict[message.chat.id][ask_position]
            if date:
                order_dict[message.chat.id][ask_date] = date
                available = handler_db.check_free_place(date, position)  # TODO не могу включить телефон!!((

                free_days_defore = int(available)
                if free_days_defore > 0:
                    bot.send_message(message.chat.id,
                                     f'Вы выбранный Вами день еще доступно {available} места для {position}')
                    handler_db.update_date(date, tab_number, surname, name, position, oke)
                    available_after_oder = handler_db.check_free_place(date, position)
                    counter_days = handler_db.get_counter_days(tab_number)
                    ordered_days = handler_db.what_dates_order(tab_number)
                    print(len(ordered_days))
                    bot.send_message(message.chat.id,
                                     f'Теперь в эту дату доступно {available_after_oder} места для {position}')
                    bot.send_message(message.chat.id,
                                     f'Итого у вас заказано на этот месяц {counter_days} дн.:\n{ordered_days}')
                else:
                    bot.send_message(message.chat.id, f'В эту дату не осталось свободных мест\n')
                    return
                # if available:
                #     pass
                # msg5 = bot.send_message(message.chat.id, ask_comment)
                # bot.register_next_step_handler(msg5, start_05)
            else:
                bot.send_message(message.chat.id, f'Введенная дата некорректна. Начните процедуру заново.')
                return

        def start_003(message):
            """Проверяет должность на корректность, заносит должность в две базы данных
            спрашивает желаемую дату"""
            message.text = check_true_position(message)
            order_dict[message.chat.id][ask_oke] = message.text
            msg4 = bot.send_message(message.chat.id, ask_date, parse_mode='Markdown')
            bot.register_next_step_handler(msg4, start_04)

        def start_03(message):
            """Проверяет должность на корректность, заносит должность в две базы данных
            спрашивает желаемую дату"""
            message.text = check_true_position(message)
            order_dict[message.chat.id][ask_position] = message.text
            handler_db.update_position(message.chat.id, message.text)
            msg5 = bot.send_message(message.chat.id, ask_oke, reply_markup=otdelenie(), parse_mode='Markdown')
            bot.register_next_step_handler(msg5, start_003)

        def start_02(message):
            '''Выполняет соответсвующее от выбранного действия: либо спрашивает должность, либо выдает заранее заказанные выходные'''
            order_dict[message.chat.id]['surname'] = surname
            order_dict[message.chat.id]['name'] = name
            order_dict[message.chat.id]['tab_number'] = handler_db.get_tab_number(message.chat.id)
            order_dict[message.chat.id][ask_order_or_cancel] = message.text

            if message.text.lower() in "заказать выходной заказать\nвыходной":
                bot.send_message(message.chat.id,
                                 "Обращаем Ваше внимание, что выходные на данные момент можно заказывать "
                                 "на февраль месяц. \nCуществует ограничение на количество заказанных "
                                 "выходных в день на каждое отделение:\n - 2 СБ;\n - 2 BS;\n - 4 БП.\n "
                                 "Каждый бортпроводник может заказать не более двух дней подряд.")
                msg2 = bot.send_message(message.chat.id, ask_position, reply_markup=position(),
                                        parse_mode='Markdown')
                bot.register_next_step_handler(msg2, start_03)
            if message.text.lower() in "отменить\nвыходной отменить выходной":
                order_dict[message.chat.id][ask_order_or_cancel] = message.text
                tab_number = handler_db.get_tab_number(message.chat.id)
                ordered_days = handler_db.what_dates_order(tab_number)

                bot.send_message(message.chat.id,
                                 f'Вот Ваши уже заказанные выходные:\n {ordered_days}\n\n'
                                 f'Для того чтобы удалить выходной в определенную дату напишите слово удалить выходной и число, напрмер:\n\n'
                                 f'удалить выходной 25')  # if "удалить выходной " будет написано в общем коде
            if message.text.lower() in "заказанные даты":
                tab_number = handler_db.get_tab_number(message.chat.id)
                counter_days = handler_db.get_counter_days(tab_number)
                ordered_days = handler_db.what_dates_order(tab_number)
                msg500 = bot.send_message(message.chat.id,
                                          f'Итого у вас заказано на этот месяц {counter_days} дн.:\n{ordered_days}',
                                          reply_markup=select_action_in_cancel())
                bot.register_next_step_handler(msg500, start_02)
            if message.text.lower() in "свободные\nдаты":
                handler_db.check_free_dates(position)
            if message.text.lower() in "выйти":
                return

        order_dict = {message.chat.id: {}}
        msg1 = bot.send_message(message.chat.id, ask_order_or_cancel, reply_markup=select_action())
        bot.register_next_step_handler(msg1, start_02)

        # TODO ВЫХОДНЫЕ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

        if not autoconfirm and not password:
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

    if 'отказ от рассылки' in message.text or 'отказаться от рассылки' in message.text or '/newsnote' in message.text:
        if messaging:
            bot.send_message(user_id, "Хорошо, мы обязательно отключим рассылку сообщений.")
            bot.send_message(157758328, f'{user_id} {name} {surname} попросил отказаться от рассылки')
            prohibited = False
            result = handler_db.update_messaging(prohibited, user_id)
            if result is not None:
                bot.send_message(user_id, "Рассылка сообщений отключена.")
                bot.send_message(157758328, f'{fio} рассылка сообщений отключена автоматически.')
        if not messaging:
            bot.send_message(user_id, "Хорошо, мы обязательно включим рассылку сообщений.")
            bot.send_message(157758328, f'{user_id} {name} {surname} попросил включить рассылки')
            allowed = True
            result = handler_db.update_messaging(allowed, user_id)
            if result is not None:
                bot.send_message(user_id, "Рассылка сообщений включена.")
                bot.send_message(157758328, f'{fio} рассылка сообщений включена автоматически.')
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

    if message.text in "/addinfo добавить  информацию":
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

    if 'инструктор' == message.text or 'инструктора' == message.text:
        bot.send_message(user_id, 'Какой именно инструктор Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить какой инструктор интересует")
        return

    if 'телефон' == message.text or 'номер телефона' == message.text or "добавочный номер" == message.text or 'телефоны' in message.text or 'номера' in message.text:  # TODO наверное не очень семантично здесь размещать обработку этого запроса
        bot.send_message(user_id, 'Чей именно телефон Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить чей телефон нужен")
        return

    if 'почта' == message.text:
        bot.send_message(user_id, 'Чья именно почта Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить какая именно почта интересует")
        return

    if 'особенности' == message.text:
        bot.send_message(user_id, 'Какие именно особенности Вас инетересуют?', reply_markup=general_menu())
        bot.send_message(157758328, "Попросили уточнить какие именно особенности интересуют")
        return

    if 'особенности рейса' == message.text:
        bot.send_message(user_id, 'Какой город Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "При запросе особенности рейса, попросили уточнить какой город интересует")
        return

    if 'питание' == message.text:
        bot.send_message(user_id, 'Какое питание Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "При запросе питание, попросили уточнить какое питание интересует")
        return

    if 'самолет' == message.text:
        bot.send_message(user_id, 'Какой самолет Вас инетересует?', reply_markup=general_menu())
        bot.send_message(157758328, "При запросе самолет, попросили уточнить какой самолет интересует")
        return

    if 'супервайзер' == message.text:
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
                         "предоставить доступ\nuser_id\nsurname\nname\ncity\nlink\nexp_date\ntab_number\npassword\naccess\nmessaging\ncheck_permissions\nnight_notify\nplan_notify\nautoconfirm\ntime_depart\ntime_arrive\n\n"
                         "7.  разослать сообщение <сразу текст...> - рассылает сообщение всем пользователям из базы\n\n"
                         "8.  проверить налет у всех бортпроводников - вызывает функцию check_nalet_for_everyone()\n\n"
                         "9.  проверить допуски у всех бортпроводников - вызывает функцию check_permissions_for_everyone()\n\n"
                         "10. сколько бортпроводников - возвращает длину базы данных\n\n"
                         "11. удалить пользователя <user_id>- вызывает функцию delete_user_from_db и возвращает результат\n\n"
                         "12. просмотреть данные пользователя <user_id> - вызывает select() возвращает сырой кортеж из базы\n\n"
                         "13. изменить город пользователя user_id city")
        return

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
                    get_photo()
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
        except Exception as exc:
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
