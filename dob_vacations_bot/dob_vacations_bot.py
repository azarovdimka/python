# !/usr/bin/env python3
import traceback

import telebot as t
# чтобы работал telebot - удалить telebot, и установить Pytelegrambotapi, написанным оставить telebot
from telebot import types
from datetime import datetime, timedelta
import handler_vacations_db as handler_db
import settings
import time
import sys
from os import path  # извлекать пути и папки

bot = t.TeleBot(settings.TOKEN)
bot.send_message(157758328, f"бот перезапущен")


def select_action():
    """Основаня клавиатура внизу экрана: выбор первичного дейсвтия заказать выходной, просмотреть свободные дни, отменить"""
    select_action = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Заказать\nвыходные')
    btn2 = types.KeyboardButton('Отменить\nвыходные')
    btn3 = types.KeyboardButton('Заказанные даты')
    # btn4 = types.KeyboardButton('Выйти')
    select_action.add(btn1, btn2, btn3)  # , btn4
    return select_action


def select_date_from():
    """предлагает выбрать число с которого выбрать выходные"""
    from_date = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=4)
    btn1 = types.KeyboardButton('1')
    btn2 = types.KeyboardButton('2')
    btn3 = types.KeyboardButton('3')
    btn4 = types.KeyboardButton('4')
    btn5 = types.KeyboardButton('5')
    btn6 = types.KeyboardButton('6')
    btn7 = types.KeyboardButton('7')
    btn8 = types.KeyboardButton('8')
    from_date.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
    return from_date


def select_duration():
    """предлагает выбрать продолжительность выходных"""
    select_duration = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=4)
    btn1 = types.KeyboardButton('1')
    btn2 = types.KeyboardButton('2')
    btn3 = types.KeyboardButton('3')
    btn4 = types.KeyboardButton('4')
    btn5 = types.KeyboardButton('5')
    btn6 = types.KeyboardButton('6')
    btn7 = types.KeyboardButton('7')
    btn8 = types.KeyboardButton('8')
    select_duration.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
    return select_duration


@bot.message_handler(commands=['start'])
def welcome(message):
    """При первом подключении пользователя к боту - выводит приветсвенный стикер, приветсвенную речь."""
    # TODO УВЕДОМЛЕНИЕ!! (всего три 259, 288, 292) RETURN ВХОДИТ В УВЕДОМЛЕНИЕ

    with open('static/AnimatedSticker.tgs', 'rb') as sti:
        bot.send_sticker(message.chat.id, sti)

    bot.send_message(message.chat.id, f"Прием заказов выходных дней на новогодние праздники прекращен. Если Вам требуется отменить ранее сделанный заказ - обратитесь к своему начальнику ОКЭ.")
    # bot.send_message(message.chat.id, f"Представьтесь, пожалуйста. Напишите свой табельный номер, фамилию, имя через "
    #                                   f"пробел (три слова через пробел и без других лишних символов). "
    #                                   f"Например: \n123456 Смирнов Иван")
    return


@bot.message_handler(content_types=["text"])  #
def conversation(message):
    bot.send_message(message.chat.id,
                     f"Прием заказов выходных дней на новогодние праздники прекращен. Если Вам требуется отменить ранее сделанный заказ - обратитесь к своему начальнику ОКЭ.")
    return

    handler_db.to_create_users_db()
    handler_db.to_create_vacations_db()
    # if "создать базу пользователей" in message.text.lower():
    #     result = handler_db.to_create_users_db()
    #     bot.send_message(157758328, result)
    #     return
    #
    # if "создать таблицу на январь" in message.text.lower():
    #     result = handler_db.to_create_vacations_db()
    #     bot.send_message(157758328, result)
    #     return

    tab_number_surname_name = handler_db.get_tab_number_name_surname(message.chat.id)
    if tab_number_surname_name:
        tab_number = tab_number_surname_name.split()[0]
        surname = tab_number_surname_name.split()[0]
        name = tab_number_surname_name.split()[2]

    if "удалить пользователя" in message.text.lower():
        user = message.text.split()
        handler_db.delete_user_from_db(user[-1])
        result = handler_db.select_all_data_of_person(user[-1])
        bot.send_message(157758328, result)
        return

    if "очистить базу данных пользователей отчистить базу данных пользователей" in message.text.lower(): # TODO не работает проверить почему
        handler_db.to_create_general_db()
        handler_db.import_users_to_excel()
        bot.send_document(message.chat.id, open('users.xlsx', "rb"))
        bot.send_message(157758328, "база данных пользователй очищена.")
        return

    if 'сохранить пользователей в excel' in message.text.lower() and message.chat.id == 157758328:
        handler_db.import_users_to_excel()
        bot.send_document(message.chat.id, open('users.xlsx', "rb"))
        return

    if (message.text.lower() in "сохранить выходные в excel выгрузить таблицу"): # and message.chat.id in krs_list
        handler_db.import_vacations_to_excel()
        bot.send_document(message.chat.id, open(f'vacations.xlsx', "rb"))
        bot.send_message(157758328, f" файл с таблицей отправлен")
        return

    if message.text.lower() in "заказать\nканикулы заказать\nвыходные заказать выходные на январь":
        tab_number_surname_name = handler_db.get_tab_number_name_surname(message.chat.id)
        if tab_number_surname_name:
            tab_number = tab_number_surname_name.split()[0]
            name = tab_number_surname_name.split()[2]
            vacations = handler_db.get_vacations(tab_number)
            if not vacations:
                bot.send_message(message.chat.id, f"Вы можете заказать себе любое количество дней подряд в "
                                                  f"период с 1 по 8 января.")
                bot.send_message(message.chat.id, f"{name}, с какого числа Вы планируете начать выходные в новогодние праздники?", reply_markup=select_date_from())
                handler_db.add_from_ask_to_temp(tab_number, True)
                return

            else:
                bot.send_message(message.chat.id, f"{name}, у вас уже заказаны выходные {vacations.lower()} января.", reply_markup=select_action())
            return

    if message.text.lower() in "отменить каникулы отменить\nвыходные удалить выходной снять выходные отменить\nканикулы":
        tab_number_surname_name = handler_db.get_tab_number_name_surname(message.chat.id).split()
        tab_number = tab_number_surname_name[0]
        vacations = handler_db.get_vacations(tab_number)
        if vacations:
            result_date = handler_db.delete_date(tab_number, vacations)
            result_temp = handler_db.delete_from_temp(tab_number)
            if result_date and result_temp:
                bot.send_message(message.chat.id, f'Выходные {vacations.lower()} января удалены успешно.', reply_markup=select_action())
                handler_db.add_new_user_to_temp_db(message.chat.id, tab_number)
                return

        else:
            bot.send_message(message.chat.id, f'У Вас не было ранее заказанных больших выходных на новогодние праздники.', reply_markup=select_action())
        return

    if message.text.lower() in "заказанные даты":
        tab_number_surname_name = handler_db.get_tab_number_name_surname(message.chat.id).split()
        tab_number = tab_number_surname_name[0]
        name = tab_number_surname_name[2]
        vacations = handler_db.get_vacations(tab_number)
        if vacations:
            handler_db.delete_date(message.chat.id, vacations)
            bot.send_message(message.chat.id, f'{name}, мы записали Ваши пожелания {vacations.lower()} января.', reply_markup=select_action())
            return

        else:
            bot.send_message(message.chat.id, f'У Вас не было ранее заказанных больших выходных на новогодние праздники.', reply_markup=select_action())
            return

    if message.text.lower() in ["выйти", "отмена", "стоп", "отбой", "назад", "спасибо", "круто", "супер", "отлично", "прекрасно"]:
        bot.send_message(message.chat.id, f"Если что, обращайтесь.")
        return

    if not handler_db.check_access(message.chat.id):
        if len(message.text.split()) != 3:
            bot.send_message(message.chat.id,
                             f"Представьтесь, пожалуйста. Напишите свой табельный номер, фамилию, имя через пробел (три слова через пробел и без других лишних символов). Например: \n123456 Смирнов Иван")
            return
        if len(message.text.split()) == 3 and message.text.split()[0].isdigit() and message.text.split()[1].isalpha():
            tab_number = message.text.split()[0]
            surname = message.text.split()[1]
            name = message.text.split()[2]

            try:
                handler_db.add_new_user_to_users_db(message.chat.id, surname, name, tab_number)
            except Exception as exc:
                bot.send_message(157758328, f"181: ошибка {exc}.")
                bot.send_message(message.chat.id, f"Что-то пошло не так... Вероятно, вы уже зарегестрированны с таким табельным номером, либо попробуйте снова...")
                return

            handler_db.add_new_user_to_temp_db(message.chat.id, tab_number)
            tab_number_surname_name = handler_db.get_tab_number_name_surname(message.chat.id)
            if tab_number_surname_name:
                tab_number = tab_number_surname_name.split()[0]
                surname = tab_number_surname_name.split()[1]
                name = tab_number_surname_name.split()[2]
                bot.send_message(157758328, f"Пользователь id {message.chat.id} {tab_number} {surname} {name} добавлен успешно.")
                bot.send_message(message.chat.id, f"Вы можете заказать себе любое количество дней подряд в "
                                                  f"период с 1 по 8 января.")
                bot.send_message(message.chat.id, f"{name}, с какого числа Вы планируете начать выходные в новогодние праздники?",
                                 reply_markup=select_date_from())
                handler_db.add_from_ask_to_temp(tab_number, True)
                # bot.send_message(message.chat.id, f" проверили спросили ли с какого числа нужны выходные {handler_db.get_from_ask(tab_number)}")
                return

    if handler_db.check_access(message.chat.id) and (len(message.text.split()) == 3 and message.text.split()[0].isdigit() and message.text.split()[1].isalpha()):
        bot.send_message(message.chat.id, f"Вы уже регистрировались ранее.", reply_markup=select_action())
        return

    if message.text.lower() in ['привет', "здорово", "здорова", "как дела", "добрый день", "добрый вечер", "доброе утро", "как заказать выходные"]:
        bot.send_message(message.chat.id, f"Здравствуйте, чем могу помочь?", reply_markup=select_action())
        return

    # if message.text is not bool:
    #     bot.send_message(message.chat.id, f" message.text {message.text} is not bool")

    #     tab_number_surname_name = handler_db.get_tab_number_name_surname(message.chat.id)
    #     tab_number = tab_number_surname_name.split()[0]
    #     name = tab_number_surname_name.split()[2]
    #

    # bot.send_message(message.chat.id, f"tab_number {tab_number}")

    try:
        if handler_db.get_from_ask(tab_number) is None:
            handler_db.add_from_ask_to_temp(tab_number, False)
    except Exception as e:
        bot.send_message(message.chat.id, f"Представьтесь, пожалуйста. Напишите свой табельный номер, фамилию, имя через "
                                          f"пробел (три слова через пробел и без других лишних символов). "
                                          f"Например: \n123456 Смирнов Иван")
        bot.send_message(157758328, f"218: Предотвратили ошибку {e}\n\n попросили представиться {message.chat.id} {handler_db.get_tab_number_name_surname(message.chat.id)}")
        return

    if message.text.isdigit() and handler_db.get_from_ask(tab_number) and (handler_db.get_from_date(tab_number) == '0' or handler_db.get_from_date(tab_number) is None):
        if len(message.text) == 1 and message.text.isdigit():
            handler_db.add_from_date_to_temp(tab_number, message.text)
        else:
            bot.send_message(message.chat.id, f"делайте, что говорят")
        if 0 < int(message.text) > 8:
            bot.send_message(message.chat.id, "Число должно быть от 1 до 8. Выберете число, с которого Вы "
                                              f"планируете начать выходные в новогодние праздники.",
                             reply_markup=select_date_from())
            return
        handler_db.add_from_date_to_temp(tab_number, message.text)
        bot.send_message(message.chat.id, f"Сколько выходных дней Вам понадобится?", reply_markup=select_duration())
        return

    if message.text.isdigit() and handler_db.get_from_ask(tab_number) and handler_db.get_from_date(tab_number):
        vacations = handler_db.get_vacations(tab_number)
        if vacations:
            bot.send_message(message.chat.id, f"У Вас уже заказаны даты {vacations.lower()}",
                             reply_markup=select_action())
            return

        duration = message.text
        if int(duration) > 8:
            bot.send_message(message.chat.id,
                             f"{name}, продолжительность выходных дней в новогодние праздники не может превышать 8 дней. \nСколько выходных дней Вам понадобится на новогодние праздники?",
                             reply_markup=select_duration())
            return

        handler_db.add_duration_to_temp(tab_number, duration)
        from_date = int(handler_db.get_from_date(tab_number))

        duration = int(handler_db.get_duration(tab_number))
        till_date = from_date + duration - 1

        if till_date > 8:
            bot.send_message(message.chat.id, f"{name}, выходные дни могут быть заказаны только по 8 января. \nСколько выходных дней Вам понадобится?", reply_markup=select_duration())
            till_date = '8'
            return
        if till_date <= 8:
        # if len(message.text.split()) >= 4 and message.text.split()[0].isalpha() and message.text.split()[1].isdigit() and message.text.split()[2].isalpha():
            if till_date == from_date:
                date = till_date
                vacations = f'{date}'
            else:
                vacations = f'с {from_date} по {till_date}'
            tab_number_surname_name = handler_db.get_tab_number_name_surname(message.chat.id)
            if tab_number_surname_name:
                tab_number = tab_number_surname_name.split()[0]
                surname = tab_number_surname_name.split()[1]
                name = tab_number_surname_name.split()[2]
                try:
                    result_ok = handler_db.add_vacations_to_vacations_db(message.chat.id, tab_number, surname, name, from_date, till_date, duration)
                except Exception as exc:
                    vacations = handler_db.get_vacations(tab_number)
                    bot.send_message(message.chat.id,
                                     f"{name}, у вас уже заказаны даты {vacations.lower()}.", reply_markup=select_action())
                    return
                if result_ok:
                    bot.send_message(message.chat.id, f"{name}, мы записали Ваши пожелания {vacations.lower()} января.", reply_markup=select_action())
                    bot.send_message(157758328,
                                     f"Пользователь id {message.chat.id} {tab_number} {surname} {name} заказал выходные {vacations.lower()} января.")
                    # bot.send_message(message.chat.id, f"{name}, у Вас заказаны дополнительные выходные {vacations} января.")
                return


    else:
        bot.send_message(message.chat.id, f"Я могу только записать любые ваши желаемые даты на отдых в период с 1 по 8 января.", reply_markup=select_action())
        try:
            tab_number_surname_name = handler_db.get_tab_number_name_surname(message.chat.id).split()
        except Exception as exc:
            bot.send_message(message.chat.id, f"ошибка {exc}")
            bot.send_message(message.chat.id,
                             f"Представьтесь, пожалуйста. Напишите свой табельный номер, фамилию, имя через пробел (три слова через пробел и без других лишних символов). Например: \n123456 Смирнов Иван")
            return

        tab_number = tab_number_surname_name[0]
        vacations = handler_db.get_vacations(tab_number)
        name = handler_db.get_tab_number_name_surname(message.chat.id).split()[2]
        if vacations:
            bot.send_message(message.chat.id, f"{name}, cейчас у Вас уже заказаны даты {vacations.lower()} января.", reply_markup=select_action())
        else:
            bot.send_message(message.chat.id, f"Сейчас у Вас еще нет заказанных выходных на январь. Если вы хотите заказать себе выходные в период новогодних праздников - выберите число, с которого Вы бы хотели, чтобы начинались выходные дни.", reply_markup=select_date_from())
            return
        return


bot.polling(none_stop=True)
