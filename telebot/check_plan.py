import traceback

import telebot
from telebot.types import InlineKeyboardMarkup
from telebot import types
import time
import os
import check_news
import settings
import handler_db
import notificator
import exception_logger

bot = telebot.TeleBot(settings.TOKEN)

document_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup(row_width=1)
btn_doc = types.InlineKeyboardButton(text="Открыть подробнее в OpenSky", url='https://edu.rossiya-airlines.com/')
not_messaging = types.InlineKeyboardButton(text="Отказаться от рассылки", callback_data="not_messaging")
document_btn.add(btn_doc, not_messaging)

plan_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()
btn = types.InlineKeyboardButton(text="Открыть план работ в OpenSky", url='https://edu.rossiya-airlines.com/workplan/')
plan_btn.add(btn)


def cycle_plan_notify():
    while True:
        # bot.send_message(157758328, f'Бот начал проверку планов пользователей')
        sent_plan_counter = 0
        sent_doc_counter = 0
        sent_plan_list = []
        sent_doc_list = []
        current_time = time.strftime('%H:%M')
        if current_time == '00:00':
            time.sleep(60)
        list_id = handler_db.list_user_id()
        try:
            # bot.send_message(157758328, f'бот начал проверку планов')
            for user_id in list_id:
                user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, autoconfirm, time_depart = handler_db.fetch_user_for_plan(
                    user_id)
                fio = f'{user_id} {surname} {name} '  # TODO почему-то бывает периодчески по некоторым значениям возвращает None
                if password == '' or not password or password == '0' or not plan_notify:
                    continue
                if '07:00' > current_time > '00:00' and not night_notify:  # обычно ['key'] выдает ошибку в некоторых местах нет ключа keyerror хотя ключ есть, а с методом get ключ видит
                    continue

                notification = notificator.notify(user_id, tab_number, password, autoconfirm, time_depart)
                # TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС ФАЙЛА в НОТИФИКАТОРЕ!!!
                if notification is None:
                    continue
                if notification.split()[0] == 'Проблема':
                    continue
                if notification != None:  # не равно none - получили план. будет ошибка, если ему не удалось отправить ему его план - по
                    bot.send_message(user_id, notification, reply_markup=plan_btn, parse_mode='html')
                    sent_plan_counter += 1
                    sent_plan_list.append(fio)

            # if sent_plan_counter > 0:
            #     bot.send_message(157758328,
            #                      f'общий отчет: план выслан {sent_plan_counter} чел. {", ".join(sent_plan_list)}')
            # bot.send_message(157758328, f'бот закончил проверку планов')
            # bot.send_message(157758328, f'бот начал проверку документов')
            for user_id in list_id:
                user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, autoconfirm, time_depart = handler_db.fetch_user_for_plan(
                    user_id)
                fio = f'{user_id} {surname} {name} '
                if not password or not messaging:
                    continue
                if '07:00' > current_time > '00:00' and not night_notify:  # обычно ['key'] выдает ошибку в некоторых местах нет ключа keyerror хотя ключ есть, а с методом get ключ видит
                    continue
                if messaging and password:
                    new_document, strings_to_file = check_news.parser(tab_number, password, user_id)
                    if strings_to_file is None:
                        continue
                    availability_for_planing = True
                    path_plan = "/usr/local/bin/bot/plans/plans" + str(user_id) + ".txt"
                    # path_plan = "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\telebot\\plans\\plans" + str(user_id) + ".txt" #
                    #  #  #
                    if os.path.exists(path_plan):
                        with open(path_plan, 'r',
                                  encoding='utf-8') as original:  # TODO выдает ошибку нет такойц директории, хотя файл есть
                            old_file = original.read()
                            if 'не найдено' in old_file or 'Отпуск' in old_file:
                                availability_for_planing = False

                    if new_document is not None and availability_for_planing:
                        doc_path = "/usr/local/bin/bot/documents/doc" + str(
                            user_id) + ".txt"  # "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\telebot\\documents\\doc" + str(user_id) + ".txt" #
                        #

                        if not os.path.exists(doc_path):
                            with open(doc_path, 'w', encoding='utf-8') as new:
                                new.write(strings_to_file)
                                bot.send_message(user_id, new_document, reply_markup=document_btn, parse_mode='html')
                                # bot.send_message(157758328, f'{fio} {new_document}', reply_markup=document_btn,
                                #                  parse_mode='html')
                                sent_doc_counter += 1
                                sent_doc_list.append(fio)

                        else:
                            with open(doc_path, 'r', encoding='utf-8') as old_file:
                                old_file = old_file.read()
                                if strings_to_file not in old_file:  # TODO нужно более точное сравнение
                                    with open(doc_path, 'a', encoding='utf-8') as new_data:
                                        new_data.write(f"\n{strings_to_file}")
                                        bot.send_message(user_id, new_document, reply_markup=document_btn,
                                                         parse_mode='html')
                                        # bot.send_message(157758328, f'{fio} {new_document}', reply_markup=document_btn,
                                        #                  parse_mode='html')
                                        sent_doc_counter += 1
                                        sent_doc_list.append(fio)
            # bot.send_message(157758328, f'бот закончил проверку документов')
            # if sent_doc_counter > 0:
            #     bot.send_message(157758328,
            #                      f'общий отчет: документы высланы {sent_doc_counter} чел. {", ".join(sent_doc_list)}')
        except Exception as e:
            exception_logger.writer(exc=e, request="извлечение ключа словаря user_id при автоматической отправке плана",
                                    fio=fio, answer='поймали ошибку во внешнем try except')
            bot.send_message(157758328, f'поймали ошибку во внешнем try except: {fio}: {traceback.format_exc()}')
        # bot.send_message(157758328, f'Бот закончил проверку планов пользователей и лег спать на 5 мин.')
        time.sleep(10)

# cycle_plan_notify()
