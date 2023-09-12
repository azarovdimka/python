# !/usr/bin/env python3
import traceback
import \
    telebot as t  # чтобы работал telebot - удалить telebot, и установить Pytelegrambotapi, написанным оставить telebot
from telebot import types
# from datetime import datetime, timedelta
# import pytz
import settings
import time
# import sys
# from os import path  # извлекать пути и папки
import handler_db
import random
import questions as ql
from collections import Counter
# import os


bot = t.TeleBot(settings.TOKEN)


bot.send_message(157758328, f"бот перезапущен")  # , reply_markup=select_action_krs()


krs_list = [157758328, 240176167, 5208899957, 5275895896, 5006193045, 1068718455, 417491851, 953262479]
            # 5006193045 Алексеев КРС # 202 Алексеев обычный
            # 157758328, - это я

flight_dict = {}
cnt = 0


def start_briefing():
    """Кнопка начать брифинг"""
    start_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton('Начать новый брифинг')
    start_kb.add(btn)
    return start_kb


def finish_briefing():
    """Кнопка завершить опрос"""
    finish_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton('Завершить опрос')
    finish_kb.add(btn)
    return finish_kb


def select_action_krs():
    """Клавиатура для КРС внизу экрана: выбор первичного дейсвтия заказать выходной, просмотреть свободные дни, отменить"""
    select_action = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton('Выгрузить журнал')
    select_action.add(btn)
    return select_action


def select_otdelenie():
    otdelenie_btn = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    oke_1 = types.KeyboardButton('ОКЭ 1')
    oke_2 = types.KeyboardButton('ОКЭ 2')
    oke_3 = types.KeyboardButton('ОКЭ 3')
    oke_4 = types.KeyboardButton('ОКЭ 4')
    oke_5 = types.KeyboardButton('ОКЭ 5')
    otdelenie_btn.add(oke_1, oke_2, oke_3, oke_4, oke_5)
    return otdelenie_btn


def select_position():
    position_btn = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    ipb = types.KeyboardButton('ИПБ')
    sb = types.KeyboardButton('СБ')
    bs = types.KeyboardButton('BS')
    simple = types.KeyboardButton('БП')
    position_btn.add(ipb, sb, bs, simple)
    return position_btn


def select_answer():
    answer_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Следующий БП')
    btn2 = types.KeyboardButton('Дополнительный вопрос')
    btn3 = types.KeyboardButton('Завершить опрос')
    answer_kb.add(btn1, btn2, btn3)
    return answer_kb


def crew_kb():
    crew_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    crew_btn = types.KeyboardButton('Экипаж')
    crew_kb.add(crew_btn)
    return crew_kb


def select_type_of_aircraft():
    aircraft_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    t_1 = types.KeyboardButton('A319/320')
    t_3 = types.KeyboardButton('B737')
    t_4 = types.KeyboardButton('B747')
    t_5 = types.KeyboardButton('B777')
    t_6 = types.KeyboardButton('RRJ95')
    aircraft_kb.add(t_1, t_3, t_4, t_5, t_6)
    return aircraft_kb


def start_opros():
    start_opros_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton('Начать опрос')
    start_opros_kb.add(btn)
    return start_opros_kb


def continue_survey():
    """Кнопка продолжает опрос оставшихся проводников"""
    continue_opros_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton('Опросить оставшихся БП')
    btn1 = types.KeyboardButton('Завершить опрос')
    continue_opros_kb.add(btn, btn1)
    return continue_opros_kb


def ask_or_generate_new_question(message_chat_id, chosen_list, chosen_question, answered_list, fio_bp, tab_bp, position):
    if not check_asked_question(message_chat_id, chosen_list, chosen_question, answered_list, cnt):
        bot.send_message(message_chat_id, f'Следующий вопрос для {position} {fio_bp} ({tab_bp}):\n\n'
                                          f'{fio_bp.split(" ")[1]}, расскажите{chosen_question}',
                         reply_markup=select_answer())
        answered_list.append(chosen_question)
        flight_dict[message_chat_id]['current_question'] = chosen_question
        return
    elif "Вопросы закончились, заканчивайте брифинг.":
        bot.send_message(message_chat_id, f'Вопросы закончились, заканчивайте брифинг.',
                         reply_markup=finish_briefing())
        return
    else:
        chosen_question = random.choice(chosen_list)
        ask_or_generate_new_question(message_chat_id, chosen_list, chosen_question, answered_list)



def check_list_of_tab_numbers(user_id, tab_numbers):
    """проверяет список табельных номеров полученных от СБ, что это именно список табельных номеров"""

    if len(tab_numbers) >= 2 and ' ' in tab_numbers and tab_numbers.split(' ')[1].isdigit():
        tab_number_sb = handler_db.get_tab_number_from_general_db(user_id)
        if not tab_number_sb:
            bot.send_message(user_id, f'Введите свой табельный еще раз.')
            return
        name_sb = handler_db.get_name_from_excel(tab_number_sb)

        for tab_number in tab_numbers.split(' '):
            try:
                handler_db.get_fio_crew(tab_number)
            except Exception:
                bot.send_message(user_id, f"{name_sb}, вероятно, допущена ошибка. Табельный номер {tab_number} не найден в базе. \nВведите еще раз список табельных номеров через пробел.")
                return

        return True


def check_or_add_tab_surname_name_to_db(message):
    """добавляет нового пользователя в случае представления"""
    mess = message.text.split()
    if len(mess) == 3 and message.text.split()[0].isdigit() and len(message.text.split()[0]) > 2:
        user_id = message.chat.id
        tab_number = message.text.split()[0]
        name = message.text.split()[2].capitalize()
        surname = message.text.split()[1].capitalize()
        user_id_in_db = handler_db.get_user_id_by_tab_number(tab_number)  # None или True
        if user_id_in_db:
            # bot.send_message(message.chat.id, f'Нажмите кнопку "Экипаж", чтобы полчуить список ФИО бортпроводников и зарегистрировать их в системе.', reply_markup=crew_kb())# Если не None
            return True
        else:
            handler_db.add_new_user_to_db_users(user_id, tab_number, surname, name, oke=None, position=None)
            bot.send_message(157758328, f'добавлен новый пользователь {user_id}, {surname}, {name}, {tab_number}. Предложим нажать кнопку экипаж')  # добавлено для теста
            return True
    else:
        bot.send_message(157758328,
                         f'НЕ добавлен новый пользователь {message.text} len(mess) == 3 {len(mess) == 3} and message.text.split()[0].isdigit() {message.text.split()[0].isdigit()} and len(message.text.split()[0]) > 2 {len(message.text.split()[0]) > 2}')
        return False


def check_asked_question(message_chat_id, chosen_list, chosen_question, answered_list, cnt):
    """Проверяет, задавался ли вопрос ранее, если нет, то возвращает false"""

    if chosen_question in answered_list:
        cnt += 1
        if cnt == 10:
            bot.send_message(message_chat_id, f'Вопросы закончились, заканчивайте брифинг.')
            return "Вопросы закончились, заканчивайте брифинг."
        bot.send_message(157758328, f'счетчик стал +1 = {cnt}.')

        question_list_copy = ql.question_list.copy()
        flight_dict[message_chat_id]['question_list_copy'] = question_list_copy
        if isinstance(chosen_list, dict):
            type_aircraft = handler_db.get_aircraft(message_chat_id)
            chosen_question = random.choice(chosen_list.get(type_aircraft))
            chosen_list.get(type_aircraft).remove(chosen_question)
        else:
            chosen_question = random.choice(chosen_list)
            chosen_list.remove(chosen_question)

        check_asked_question(message_chat_id, chosen_list, chosen_question, answered_list, cnt)

    if chosen_question not in answered_list:
        return False


def start_45(message):
    flight_dict[message.chat.id]['flight_number'] = message.text
    msga45 = bot.send_message(message.chat.id, f'Выберите тип ВС, на котором вы сегодня полетите.', reply_markup=select_type_of_aircraft())
    # bot.register_next_step_handler(msga45, nalet_handler)


@bot.message_handler(commands=['start'])
def welcome(message):
    """При первом подключении пользователя к боту - выводит приветсвенный стикер, приветсвенную речь."""
    with open('static/AnimatedSticker.tgs', 'rb') as sti:
        bot.send_sticker(message.chat.id, sti)
        bot.send_message(message.chat.id, f"Пожалуйста, введите свой табельный номер.")
        if message.chat.id in krs_list:
            bot.send_message(message.chat.id,
                             f'Для того, чтобы выгрузить журнал проведения брифинга в любое время - отправьте сообщение "Выгрузить журнал"',
                             reply_markup=select_action_krs())
        return


@bot.message_handler(content_types=["text"])  #
def conversation(message):

    def write_to_table(answer):
        reg_date = flight_dict[message.chat.id]['reg_date']  # get
        reg_time = flight_dict[message.chat.id]['reg_time']  # get
        tab_bp = flight_dict[message.chat.id]['current_tab_bp']  # get
        flight_number = flight_dict[message.chat.id]['flight_number']  # get
        aircraft = flight_dict[message.chat.id]['aircraft']  # get
        tab_number_sb = flight_dict[message.chat.id]['tab_number_sb']  # get
        fio_sb = handler_db.get_fio_crew(tab_number_sb)[2]
        fio_bp = handler_db.get_fio_crew(tab_bp)[2]
        flight_dict[message.chat.id]['fio_bp'] = fio_bp  # update
        question = flight_dict[message.chat.id]['current_question']  # get
        id = int(handler_db.get_len_flight_db()) + 1
        handler_db.insert_new_flight(messagechatid=message.chat.id, id=str(id), date=reg_date, time_briefing=reg_time, flight_number=flight_number,
                                     aircraft=aircraft, tab_number_sb=tab_number_sb, fio_sb=fio_sb,
                                     tab_bp=tab_bp, fio_bp=fio_bp, question=question, answer=answer)
        return

    def survey(message):

        try:
            proverka = flight_dict[message.chat.id]
        except Exception:
            bot.send_message(message.chat.id, f"Вы что-то сделали не так, работайте последовательно.")
            return False

        numbers_list = flight_dict[message.chat.id]['numbers_list']  # get
        successfull_answered = flight_dict[message.chat.id]['successful_tab_bp']  # get
        unsuccessfull_answered = flight_dict[message.chat.id]['unsuccessful_tab_bp']  # get
        deleted_bp = flight_dict[message.chat.id]['deleted_tab_bp']  # get

        for tab_bp in numbers_list:
            if tab_bp in successfull_answered or tab_bp in deleted_bp:
                continue

            if tab_bp in unsuccessfull_answered or tab_bp not in unsuccessfull_answered:
                flight_dict[message.chat.id]['tab_bp'] = tab_bp
                flight_dict[message.chat.id]['current_tab_bp'] = tab_bp
                try:
                    fio_bp = handler_db.get_fio_crew(tab_bp)[2]
                except Exception:
                    bot.send_message(message.chat.id, f'Вероятно, была допущена ошибка. Бортпроводник с тебельным '
                                                      f'номером {tab_bp} не найден в базе. \nВведите еще раз список '
                                                      f'тебльных номеров через пробел.')
                    return
                flight_dict[message.chat.id]['fio_bp'] = fio_bp
                position = handler_db.get_fio_crew(tab_bp)[3]
                question_list_copy = ql.question_list.copy()
                flight_dict[message.chat.id]['question_list_copy'] = question_list_copy
                chosen_list = random.choice(question_list_copy)
                if isinstance(chosen_list, dict):
                    type_aircraft = handler_db.get_aircraft(message.chat.id)
                    try:
                        chosen_question = random.choice(chosen_list.get(type_aircraft))
                        chosen_list.get(type_aircraft).remove(chosen_question)
                    except Exception:
                        bot.send_message(157758328,
                                         f"280: Ошибка при выборе вопроса: из этого списка chosen_list {chosen_list} "
                                         f"выбрали {chosen_question}. Запустили функцию survey() еще раз.")
                        survey()

                else:
                    try:
                        chosen_question = random.choice(chosen_list)
                    except Exception:
                        bot.send_message(157758328,
                                         f"280: Ошибка при выборе вопроса: из этого списка chosen_list {chosen_list} "
                                         f"выбрали {chosen_question}. Запустили функцию survey() еще раз.")
                        survey()
                    chosen_list.remove(chosen_question)

            answered_list = flight_dict[message.chat.id]['answered_quest_list']
            ask_or_generate_new_question(message.chat.id, chosen_list, chosen_question, answered_list, fio_bp, tab_bp, position)
            return

        else:
            bot.send_message(message.chat.id, f'Опрос окончен. Завершить опрос?', reply_markup=finish_briefing())
            handler_db.del_user_from_general_db(message.chat.id)
            return

    if message.text.lower() in ['выгрузить журнал', 'журнал', "сохранить таблицу", "выгрузить таблицу", "получить отчет"] and message.chat.id in krs_list:
        handler_db.upload_flight_journal_to_excel()
        bot.send_document(message.chat.id, open(f'briefing_journal.xlsx', "rb"), reply_markup=select_action_krs())
        bot.send_message(157758328, f" файл с таблицей отправлен пользователю {message.chat.id}")
        return

    if 'Начать новый брифинг' in message.text:
        # """Предложение об Авторизации СБ"""
        bot.send_message(message.chat.id, f"Введите свой табельный номер.")
        return

    if message.text.isdigit() and 4 <= len(message.text) <= 6:
        # """Авторизация СБ Проверка на табельный СБ и сохранение ее в переменную tab_number_sb"""
        # check_tab_number(message.chat.id)
        tab_number_sb = message.text
        name_sb = handler_db.get_name_from_excel(tab_number_sb)
        oke, tab_number_sb, fio_sb, position = handler_db.get_fio_crew(tab_number_sb)

        try:
            handler_db.add_new_user_to_db_users(message.chat.id, tab_number_sb, fio_sb, name_sb, oke, position)
        except Exception:
            pass

        reg_date = time.strftime('%d.%m.%Y')
        reg_time = time.strftime('%H:%M')

        # bot.send_message(157758328, f" reg_date {reg_date} reg_time {reg_time}")

        flight_dict[message.chat.id] = {}
        flight_dict[message.chat.id]['reg_date'] = reg_date
        flight_dict[message.chat.id]['reg_time'] = reg_time
        flight_dict[message.chat.id]['flight_number'] = None
        flight_dict[message.chat.id]['aircraft'] = None
        flight_dict[message.chat.id]['tab_number_sb'] = tab_number_sb
        flight_dict[message.chat.id]['fio_sb'] = fio_sb
        flight_dict[message.chat.id]['numbers_list'] = []
        flight_dict[message.chat.id]['tab_bp'] = None
        flight_dict[message.chat.id]['fio_bp'] = None
        flight_dict[message.chat.id]['answered_quest_list'] = []
        flight_dict[message.chat.id]['current_tab_bp'] = None
        flight_dict[message.chat.id]['current_question'] = None
        flight_dict[message.chat.id]['successful_tab_bp'] = []
        flight_dict[message.chat.id]['unsuccessful_tab_bp'] = []
        flight_dict[message.chat.id]['semisuccessful_tab_bp'] = []
        flight_dict[message.chat.id]['deleted_tab_bp'] = ''

        id = int(handler_db.get_len_flight_db())+1
        # handler_db.insert_new_flight(messagechatid=message.chat.id, id=str(id), date=reg_date, time_briefing=reg_time, flight_number='', aircraft='',
        #                              tab_number_sb=tab_number_sb, fio_sb=fio_sb, tab_bp='', fio_bp='', question='', answer='')

        ask_flight_number = bot.send_message(message.chat.id,
                         f'{name_sb}, введите прямой номер рейса, который вы собираетесь выполнять, например: 6013')  # Если не None
        bot.register_next_step_handler(ask_flight_number, start_45)
        return

    # if len(message.text) == 4 and message.text.isdigit():
    #     """Проверка на номер рейса и сохранение его в переменную flight_number, предалгаем выбрать тип ВС"""
    #     flight_number = message.text
    #     flight_dict[message.chat.id]['flight_number'] = flight_number
    #     bot.send_message(message.chat.id,
    #                      f'Выберите тип ВС, на котором вы сегодня полетите.', reply_markup=select_type_of_aircraft())
    #     return


    if "/complain" in message.text:
        bot.send_message(message.chat.id, f'Для того, чтобы сообщить о возникшей ошибке или проблеме - напишите Дмитрию @AnalystAzarov')
        return

    if "/faq" in message.text:
        bot.send_message(message.chat.id, f'- *Как начать брифинг:* введите свой табельный номер или нажмите кнопку "Начать брифинг" или /start. \n'
                                          f'- *Ввели данные с ошибкой:* введите запрашиваемые данные еще раз повторно.\n'
                                          f'- *Бот завис и не реагирует:* нажмите или отправьте сообщение /start \n'
                                          f'- *Забыли как проводить брифинг:* нажмите /algoritm или отправьте сообщение "Алгоритм проведения брифинга" \n'
                                          f'- *Возникли другие вопросы:* пишите Дмитрию @AnalystAzarov', parse_mode='Markdown')
        return

    if "/algoritm" in message.text or "алгоритм проведения брифинга" in message.text.lower():
        bot.send_message(message.chat.id, f'*Алгоритм проведения предполётного брифинга:*\n'
                  '- Представление СБ и ЛЭ.\n'
                  '- Сверка табельного номера и ФИО.\n'
                  '- Контроль внешнего вида.\n'
                  '- Контроль наличия необходимых документов для выполнения рейса.\n'
                  '- Доведение новой информации.\n'
                  '- Номер рейса, маршрут полета.\n'
                  '- Время полета, разница во времени с базовым аэропортом, время стоянки, погодные условия;\n'
                  '- Номер стоянки ВС, тип и номер ВС.\n'
                  '- Количество пассажиров по классам обслуживания.\n'
                    '- Особые категории (SSR), определяющие особые требования к обслуживанию: '
                    'участники бонусных программ, специальное питание, маломобильные, инфанты, несопровождаемые дети и др.\n'
                    '- Распределение обязанностей ЧКЭ в соответствии с РТК. \n'
                    '- Назначение РСБ и старшего в экономе, при необходимости.\n'
                    '- Особенности рейса.\n'
                    '- Рационы\n'
                    '- Наличие иммиграционных карт и таможенных/медицинских деклараций.\n'
                    '- Таможенные, санитарные и пограничные правила (ограничения) страны назначения.\n'
                    '- Правила доступа в кабину ЛЭ и код доступа.\n'
                    '- Правила нахождения на отдыхе в эстафетном (транзитном) аэропорту.\n'
                    '- Время выезда/выхода КЭ из офиса в здание аэропорта.\n'
                    '- Опрос ЧКЭ по процедурам обеспечения безопасности полета, авиационной безопасности, оказания '
                    'первой помощи и штатным процедурам, и сервисным процедурам при выполнении рейса. (Задать несколько '
                    'вопросов и получить ответ на каждый вопрос).\n', parse_mode='Markdown')
        return

    if message.text in ['A319/320', 'B737', 'B747', 'B777', 'RRJ95']:
        type_of_aircraft = message.text
        reg_date = flight_dict[message.chat.id]['reg_date']
        reg_time = flight_dict[message.chat.id]['reg_time']
        flight_dict[message.chat.id]['aircraft'] = type_of_aircraft
        handler_db.update_aircraft_in_general_db(message.chat.id, type_of_aircraft)
        handler_db.update_type_of_aircraft(type_of_aircraft, reg_date, reg_time)
        bot.send_message(message.chat.id,
                         f'Введите табельные номера бортпроводников через пробел.')
        return

    if check_list_of_tab_numbers(message.chat.id, message.text):

        flight_dict[message.chat.id]['numbers_list'] = message.text.split(' ')
        bot.send_message(message.chat.id, f'Начать опрос бортпроводников? Нажмите, как будете готовы.', reply_markup=start_opros())
        return

    if message.text in ["Начать опрос", "Опросить оставшихся БП"]:
        bot.send_message(157758328, f"Начат опрос бортпроводников пользователем {flight_dict[message.chat.id]['fio_sb']} id {message.chat.id} ")
        survey(message)
        return

    if "следующий бп" in message.text.lower(): # TODO все что ниже сделать в олдну функцию и вызывать ее просто после каждого ответа, передавать в нее просто ансвер, а остальное все то же самое?
        answer = "Верно"
        write_to_table(answer)
        current_tab_bp = flight_dict[message.chat.id]['current_tab_bp']
        successfull = flight_dict[message.chat.id]['successful_tab_bp']
        unsuccessfull = flight_dict[message.chat.id]['unsuccessful_tab_bp']
        successfull.append(current_tab_bp)
        flight_dict[message.chat.id]['successful_tab_bp'] = successfull
        if current_tab_bp in unsuccessfull:
            unsuccessfull.remove(current_tab_bp)
            flight_dict[message.chat.id]['unsuccessful_tab_bp'] = unsuccessfull
        survey(message)
        return

    if message.text.lower() in ["дополнительный вопрос"]:
        # if "Частично верно" in message.text:
        #     bot.send_message(message.chat.id, f"Скорректируйте устно ответ бортпроводника и задайте следующий вопрос.")
        answer = "Дополнительный вопрос"
        write_to_table(answer)
        current_tab_bp = flight_dict[message.chat.id]['current_tab_bp']
        unsuccessfull = flight_dict[message.chat.id]['unsuccessful_tab_bp']
        unsuccessfull.append(current_tab_bp)
        flight_dict[message.chat.id]['unsuccessful_tab_bp'] = unsuccessfull
        cnt = Counter(flight_dict[message.chat.id]['unsuccessful_tab_bp'])
        if cnt.get(current_tab_bp) >= 30:
            bot.send_message(message.chat.id,
                             f'Опросить оставшихся БП?', reply_markup=continue_survey())
            numbers_list = flight_dict[message.chat.id]['numbers_list']

            numbers_list.remove(current_tab_bp)
            flight_dict[message.chat.id]['deleted_tab_bp'] = current_tab_bp
            flight_dict[message.chat.id]['unsuccessful_tab_bp'] = []
            flight_dict[message.chat.id]['numbers_list'] = numbers_list

        else:
            survey(message)    # TODO помечать раздели из колорых были заданы вопросы
        return

    if "ответа нет" in message.text.lower():
        answer = message.text
        write_to_table(answer)
        return

    if "опрос окончен" in message.text.lower():
        bot.send_message(message.chat.id, f"Опрошены все бортпроводники. Завершить опрос?", reply_markup=finish_briefing())
        return

    if "завершить опрос" in message.text.lower() or "Завершить опрос" in message.text.lower():
        bot.send_message(message.chat.id, f'Этот брифинг завершен.')
        bot.send_message(message.chat.id, f'Когда будете готовы начать следующий брифинг - нажмите "Начать новый брифинг".', reply_markup=start_briefing())
        return

    else:
        bot.send_message(message.chat.id, f'Ошибка!\nПопробуйте еще раз.')
        return


bot.polling(none_stop=True)
