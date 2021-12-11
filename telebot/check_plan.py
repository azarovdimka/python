import traceback

import telebot
from telebot.types import InlineKeyboardMarkup
from telebot import types
import time
import settings
import handler_db
import notificator
import exception_logger

bot = telebot.TeleBot(settings.TOKEN)


def cycle_plan_notify():
    while True:
        # bot.send_message(157758328, f'Бот начал проверку планов пользователей')
        counter_users = 0
        sent_plan_counter = 0
        sent_plan_list = []
        current_time = time.strftime('%H:%M')
        if current_time == '00:00':
            time.sleep(60)
        list_id = handler_db.list_user_id()
        try:

            for user_id in list_id:
                user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, autoconfirm, time_depart = handler_db.fetch_user_for_plan(
                    user_id)
                fio = f'{user_id} {surname} {name} '  # TODO почему-то бывает периодчески по некоторым значениям возвращает None
                counter_users += 1
                if not password or not plan_notify:
                    continue
                if '07:00' > current_time > '00:00' and not night_notify:  # обычно ['key'] выдает ошибку в некоторых местах нет ключа keyerror хотя ключ есть, а с методом get ключ видит
                    continue
                else:
                    try:
                        notification = notificator.notify(user_id, tab_number, password, autoconfirm, night_notify,
                                                          time_depart)  # TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС ФАЙЛА в НОТИФИКАТОРЕ!!!
                        if notification is None:
                            continue
                        if notification.split()[0] == 'Проблема':
                            time.sleep(300)
                            continue
                        if notification != None:  # не равно none - получили план. будет ошибка, если ему не удалось отправить ему его план - по
                            plan_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает???
                            btn = types.InlineKeyboardButton(text="Открыть план работ в OpenSky",
                                                             url='https://edu.rossiya-airlines.com/workplan/')
                            plan_btn.add(btn)
                            bot.send_message(user_id, notification, reply_markup=plan_btn, parse_mode='html')
                            sent_plan_counter += 1
                            sent_plan_list.append(fio)
                    except Exception as exc:
                        exc_event = exception_logger.writer(exc=exc,
                                                            request="отправка плана пользователю в атоматическом режиме",
                                                            fio=fio, answer='не удалось отправить план')
                        bot.send_message(157758328, f'не удалось отправить план: \n{exc_event}')
                        continue

            if sent_plan_counter > 0:
                bot.send_message(157758328,
                                 f'общий отчет: план выслан {sent_plan_counter} чел. {", ".join(sent_plan_list)}')
        except Exception as e:
            exception_logger.writer(exc=e, request="извлечение ключа словаря user_id при автоматической отправке плана",
                                    fio=fio, answer='поймали ошибку во внешнем try except')
            bot.send_message(157758328, f'поймали ошибку во внешнем try except: {fio}: {traceback.format_exc()}')
        # bot.send_message(157758328, f'Бот закончил проверку планов пользователей и лег спать на 5 мин.')
        time.sleep(300)
