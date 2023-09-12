# !/usr/bin/env python3
import traceback
import \
    telebot as t  # чтобы работал telebot - удалить telebot, и установить Pytelegrambotapi, написанным оставить telebot
from telebot import types
from datetime import datetime, timedelta
import pytz
import settings
import time
import sys
from os import path  # извлекать пути и папки
import handler_db
import random
import questions as ql
from collections import Counter
import os

bot = t.TeleBot(settings.TOKEN)


bot.send_message(157758328, f"бот перезапущен")  # , reply_markup=select_action_krs()


krs_list = [157758328, 240176167, 5208899957, 5275895896, 5006193045, 1068718455, 417491851, 953262479]
            # 5006193045 Алексеев КРС # 202 Алексеев обычный
            # 157758328, - это я

flight_dict = {}


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


def check_list_of_tab_numbers(user_id, tab_numbers):
    """проверяет список табельных номеров полученных от СБ, что это именно список табельных номеров"""

    if len(tab_numbers) >= 2 and ' ' in tab_numbers and tab_numbers.split(' ')[1].isdigit():
        tab_number_sb = handler_db.get_tab_number_from_general_db(user_id)
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


def check_asked_question(chosen_list, chosen_question, answered_list):
    if chosen_question in answered_list:
        chosen_question = random.choice(chosen_list)
        check_asked_question(chosen_list, chosen_question, answered_list)
    else:
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
                chosen_list = random.choice(ql.question_list)
                if isinstance(chosen_list, dict):
                    # handler_db.upload_flight_journal_to_excel()  ## ВЫСЫЛАЕТ ЖУРНАЛ
                    # bot.send_document(message.chat.id, open(f'briefing_journal.xlsx', "rb"),
                    #                   reply_markup=select_action_krs())
                    type = handler_db.get_aircraft(message.chat.id)
                    chosen_question = random.choice(chosen_list.get(type))
                else:
                    chosen_question = random.choice(chosen_list)

                answered_list = flight_dict[message.chat.id]['answered_quest_list']
                if not check_asked_question(chosen_list, chosen_question, answered_list):
                    bot.send_message(message.chat.id, f'Следующий вопрос для {position} {fio_bp} ({tab_bp}):\n\n'
                                                      f'{fio_bp.split(" ")[1]}, расскажите {chosen_question.lower()}', reply_markup=select_answer())
                    answered_list.append(chosen_question)
                    flight_dict[message.chat.id]['current_question'] = chosen_question
                    return
                else:
                    bot.send_message(message.chat.id, f'224: Не знаю что делать')
                    return

        else:
            bot.send_message(message.chat.id, f'Опрос окончен. Завершить опрос?', reply_markup=finish_briefing())
            handler_db.del_user_from_general_db(message.chat.id)
            return

    if message.text.lower() in ['выгрузить журнал', 'журнал', "сохранить таблицу", "выгрузить таблицу", "получить отчет"] and message.chat.id in krs_list:
        handler_db.upload_flight_journal_to_excel()
        bot.send_document(message.chat.id, open(f'briefing_journal.xlsx', "rb"), reply_markup=select_action_krs())
        bot.send_message(157758328, f" файл с таблицей отправлен пользователю {message.chat.id}")

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
        bot.send_message(message.chat.id, f'Когда будуете готовы - нажмите "Начать новый брифинг".', reply_markup=start_briefing())
        return

    else:
        bot.send_message(message.chat.id, f'Ошибка!\nПопробуйте еще раз.')
        return


bot.polling(none_stop=True)
