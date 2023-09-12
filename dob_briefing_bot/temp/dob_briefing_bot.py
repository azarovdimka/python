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
counter_1 = 0
counter_2 = 0


def start_briefing():
    """Кнопка начать брифинг"""
    start_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton('Начать новый брифинг')
    start_kb.add(btn)
    return start_kb

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
    btn1 = types.KeyboardButton('Верно')
    btn2 = types.KeyboardButton('Не верно')
    btn3 = types.KeyboardButton('Частично верно')
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


def check_list_of_tab_numbers(tab_numbers):
    """проверяет список табельных номеров полученных от СБ, что это именно список табельных номеров"""
    if len(tab_numbers) >= 2 and ' ' in tab_numbers and tab_numbers.split(' ')[1].isdigit():
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
            handler_db.add_new_user_to_db_users(user_id, tab_number, surname, name)
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


@bot.message_handler(commands=['start'])
def welcome(message):
    """При первом подключении пользователя к боту - выводит приветсвенный стикер, приветсвенную речь."""
    with open('static/AnimatedSticker.tgs', 'rb') as sti:
        bot.send_sticker(message.chat.id, sti)
        # notification(message)
        bot.send_message(message.chat.id, f"Пожалуйста, введите свой табельный номер.")
        return


@bot.message_handler(content_types=["text"])  #
def conversation(message):

    def write_to_table(answer):
        reg_date = flight_dict[message.chat.id]['reg_date']
        reg_time = flight_dict[message.chat.id]['reg_time']
        tab_bp = flight_dict[message.chat.id]['current_tab_bp']
        flight_number = flight_dict[message.chat.id]['flight_number']
        aircraft = flight_dict[message.chat.id]['aircraft']
        tab_number_sb = flight_dict[message.chat.id]['tab_number_sb']
        fio_sb = handler_db.get_fio_crew(tab_number_sb)[2]
        fio_bp = handler_db.get_fio_crew(tab_bp)[2]
        flight_dict[message.chat.id]['fio_bp'] = fio_bp
        question = flight_dict[message.chat.id]['current_question']
        id = int(handler_db.get_len_flight_db()) + 1
        handler_db.insert_new_flight(id=str(id), date=reg_date, time_briefing=reg_time, flight_number=flight_number,
                                     aircraft=aircraft, tab_number_sb=tab_number_sb, fio_sb=fio_sb,
                                     tab_bp=tab_bp, fio_bp=fio_bp, question=question, answer=answer)
        bot.send_message(message.chat.id,
                         f"записали строку в базу данных с параметрами id={str(id)}, date={reg_date}, time_briefing={reg_time}, "
                         f"flight_number={flight_number}, aircraft= {aircraft}, tab_number_sb= {tab_number_sb}, fio_sb= {fio_sb},"
                         f" tab_bp= {tab_bp}, fio_bp= {fio_bp}, question= {question}, answer= {answer}")
        return

    def survey(message):
        numbers_list = flight_dict[message.chat.id]['numbers_list']
        # bot.send_message(message.chat.id,
        #                  f"извлекли numbers_list из словаря {numbers_list}")
        successfull_answered = flight_dict[message.chat.id]['successful_tab_bp']
        # bot.send_message(message.chat.id,
        #                  f"извлекли successfull_answered из словаря {successfull_answered}")
        unsuccessfull_answered = flight_dict[message.chat.id]['unsuccessful_tab_bp']
        # bot.send_message(message.chat.id,
        #                  f"извлекли unsuccessfull_answered из словаря {unsuccessfull_answered}")
        # bot.send_message(message.chat.id,
        #                  f"сейчас пойдем в цикл for tab_bp in numbers_list:")
        for tab_bp in numbers_list:
            # bot.send_message(message.chat.id,
            #                  f"Зашли в цикл списка тебльных в фунции survey. Берем табельный {tab_bp} из списка numbers_list {numbers_list}")
            if tab_bp in successfull_answered:
                # bot.send_message(message.chat.id,
                #                  f"этот табельный {tab_bp} есть списке успешно ответивших successfull_answered {successfull_answered}. continue Пропускаем итерацию")
                continue
            if tab_bp in unsuccessfull_answered or tab_bp not in unsuccessfull_answered:
                # bot.send_message(message.chat.id,
                #                  f"Зашли в цикл if tab_bp in unsuccessfull_answered or tab_bp not in unsuccessfull_answered:")
                # bot.send_message(message.chat.id,
                #                  f"ЛИБО этот табельный {tab_bp} есть списке неуспешно ответивших successfull_answered {unsuccessfull_answered} \n\n"
                #                  f"ЛИБО "
                #                  f"этот табельный {tab_bp} нет списке неуспешно ответивших unsuccessfull_answered {unsuccessfull_answered} \n\n"
                #                  f" \n"
                #                  f"ПОЭТОМУ ИДЕМ ДАЛЬШЕ")

                flight_dict[message.chat.id]['tab_bp'] = tab_bp
                flight_dict[message.chat.id]['current_tab_bp'] = tab_bp
                fio_bp = handler_db.get_fio_crew(tab_bp)[2]
                flight_dict[message.chat.id]['fio_bp'] = fio_bp
                position = handler_db.get_fio_crew(tab_bp)[3]
                chosen_list = random.choice(ql.question_list)
                if isinstance(chosen_list, dict):
                    type = handler_db.get_aircraft(message.chat.id, flight_dict[message.chat.id]['reg_date'])
                    chosen_question = random.choice(chosen_list.get(type))
                else:
                    chosen_question = random.choice(chosen_list)

                # if '{' in chosen_list:
                #     chosen_question = chosen_question.get(handler_db.get_aircraft(message.chat.id, flight_dict[message.chat.id]['reg_date']))

                bot.send_message(message.chat.id,
                                 f"выбран вопрос  {chosen_question}")
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
                bot.send_message(message.chat.id, f'Опрос окончен.', reply_markup=start_briefing())
                return

    # bot.send_message(157758328, f"{flight_dict}")

    if 'выгрузить журнал' in message.text.lower():
        handler_db.upload_flight_journal_to_excel()
        bot.send_document(message.chat.id, open(f'briefing_journal.xlsx', "rb"), reply_markup=select_action_krs())
        bot.send_message(157758328, f" файл с таблицей отправлен пользователю {message.chat.id}")

    if 'Начать новый брифинг' in message.text:
        # """Предложение об Авторизации СБ"""
        bot.send_message(message.chat.id, f"Введите свой табельный номер.")
        return

    if message.text.isdigit() and 4 <= len(message.text) <= 6:
        # """Авторизация СБ Проверка на табельный СБ и сохранение ее в переменную tab_number_sb"""
        tab_number_sb = message.text
        name_sb = handler_db.get_name_from_excel(tab_number_sb)
        fio_sb = handler_db.get_fio_crew(tab_number_sb)[2]

        reg_date = time.strftime('%d.%m.%Y')
        reg_time = time.strftime('%H:%M')

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

        # id = int(handler_db.get_len_flight_db())+1
        # handler_db.insert_new_flight(id=str(id), date=reg_date, time_briefing=reg_time, flight_number='', aircraft='', tab_number_sb=tab_number_sb, fio_sb=fio_sb)

        bot.send_message(message.chat.id,
                         f'{name_sb}, введите через дефис номер рейса, который вы собираетесь выполнять, например: 6013-6014')  # Если не None
        return

    if '-' in message.text and len(message.text) == 9:
        # """Проверка на номер рейса и сохранение его в переменную flight_number, предалгаем выбрать тип ВС"""
        flight_number = message.text
        flight_dict[message.chat.id]['flight_number'] = flight_number
        bot.send_message(message.chat.id,
                         f'Выберите тип ВС, на котором вы сегодня полетите.', reply_markup=select_type_of_aircraft())
        return

    if message.text in ['A319/320', 'B737', 'B747', 'B777', 'RRJ95']:
        type_of_aircraft = message.text
        reg_date = flight_dict[message.chat.id]['reg_date']
        reg_time = flight_dict[message.chat.id]['reg_time']
        flight_dict[message.chat.id]['aircraft'] = type_of_aircraft
        handler_db.update_type_of_aircraft(type_of_aircraft, reg_date, reg_time)
        bot.send_message(message.chat.id,
                         f'Введите табельные номера бортпроводников через пробел.')
        return

    if check_list_of_tab_numbers(message.text):
        flight_dict[message.chat.id]['numbers_list'] = message.text.split(' ')
        bot.send_message(message.chat.id, f'Начать опрос бортпроводников? Нажмите, как будете готовы.', reply_markup=start_opros())
        return

    if message.text == "Начать опрос":
        survey(message)
        return

    if "Верно" in message.text: # TODO все что ниже сделать в олдну функцию и вызывать ее просто после каждого ответа, передавать в нее просто ансвер, а остальное все то же самое?
        answer = message.text
        # bot.send_message(message.chat.id,
        #                  f"зашли в иф верно, answer {answer}")
        write_to_table(answer)
        # bot.send_message(message.chat.id,
        #                  f"вышли из write_to_table")
        current_tab_bp = flight_dict[message.chat.id]['current_tab_bp']
        # bot.send_message(message.chat.id,
        #                  f"current_tab_bp {current_tab_bp}")
        successfull = flight_dict[message.chat.id]['successful_tab_bp']
        # bot.send_message(message.chat.id,
        #                  f"successfull {successfull}")
        successfull.append(current_tab_bp)
        # bot.send_message(message.chat.id,
        #                  f"добавили успешный табельный {current_tab_bp} в список {successfull}")
        # bot.send_message(message.chat.id,
        #                  f"запишем список successfull в словарь flight_dict[message.chat.id]['successful_tab_bp'] {flight_dict[message.chat.id]['successful_tab_bp']} ")
        flight_dict[message.chat.id]['successful_tab_bp'] = successfull
        # bot.send_message(message.chat.id,
        #                  f"вызываем функцию survey с message.text {message.text}")
        # bot.send_message(message.chat.id,
        #                  f"счетчик успешных {Counter(flight_dict[message.chat.id]['successful_tab_bp'])}")
        survey(message)
        # bot.send_message(message.chat.id,
        #                  f"счетчик успешных {Counter(flight_dict[message.chat.id]['successful_tab_bp'])}")
        # bot.send_message(message.chat.id,
        #                  f"вышли из survey")
        # bot.send_message(message.chat.id,
        #                  f"счетчик{flight_dict[message.chat.id]}")
        return

    if "Не верно" in message.text or "Частично верно" in message.text:
        if "Частично верно" in message.text:
            bot.send_message(message.chat.id, f"Скорректируйте устно ответ бортпроводника и задайте следующий вопрос.")
        answer = message.text
        write_to_table(answer)
        current_tab_bp = flight_dict[message.chat.id]['current_tab_bp']
        unsuccessfull = flight_dict[message.chat.id]['unsuccessful_tab_bp']
        unsuccessfull.append(current_tab_bp)
        flight_dict[message.chat.id]['unsuccessful_tab_bp'] = unsuccessfull
        bot.send_message(message.chat.id,
                         f"счетчик неуспешных {Counter(flight_dict[message.chat.id]['unsuccessful_tab_bp'])}")
        survey(message)
        cnt = Counter(flight_dict[message.chat.id]['unsuccessful_tab_bp'])
        bot.send_message(message.chat.id, f"счетчик неуспешных {cnt}")
        if cnt.get(current_tab_bp) >= 3:
            fio_bp = handler_db.get_fio_crew(current_tab_bp)[2]

            bot.send_message(message.chat.id,
                             f'{fio_bp.split(" ")[1]} должна быть отстранена от рейса.')
            # TODO помечать раздели из колорых были заданы вопросы
        return

    # if "Частично верно" in message.text:
    #     bot.send_message(message.chat.id, f"Скорректируйте устно ответ бортпроводника и задайте следующий вопрос.")
    #     answer = message.text
    #     write_to_table(answer)
    #     current_tab_bp = flight_dict[message.chat.id]['current_tab_bp']
    #     semisuccessfull = flight_dict[message.chat.id]['semisuccessful_tab_bp']
    #     semisuccessfull.append(current_tab_bp)
    #     flight_dict[message.chat.id]['semisuccessful_tab_bp'] = semisuccessfull
    #
    #     bot.send_message(message.chat.id,
    #                      f"счетчик частично верных {Counter(flight_dict[message.chat.id]['semisuccessful_tab_bp'])}")
    #     survey(message)
    #     cnt = Counter(flight_dict[message.chat.id]['semisuccessful_tab_bp'])
    #     bot.send_message(message.chat.id, f"счетчик частично верных {cnt}")
    #     if cnt.get(current_tab_bp) >= 2:
    #         bot.send_message(message.chat.id,
    #                          f"Текущий табельный {Counter(flight_dict[message.chat.id]['semisuccessful_tab_bp'])} больше или равно трём. ЗНАЧИТ СНИЗИТЬ ОЦЕНКУ")
    #
    #     return


    if "Ответа нет" in message.text:
        answer = message.text
        write_to_table(answer)
        return

    if "Опрос окончен" in message.text:
        answer = message.text
        bot.send_message(message.chat.id, f"Опрос окончен.", reply_markup=start_briefing())
        return

    else:
        bot.send_message(message.chat.id, f'Попробуйте еще раз.')
        return


bot.polling(none_stop=True)
