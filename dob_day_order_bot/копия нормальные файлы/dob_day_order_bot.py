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


file_path = path.abspath(__file__)  # путь к текущему файлу в абсолютном виде под свою систему
cur_dir = path.dirname(file_path)  # папка того файла в который мы импортируем
folder = path.dirname(cur_dir)  # папка более верхнего уровня
folder = path.join(folder, 'bot')  # TODO бот исправить на телебот при запуске с домашнего компа (bot на сервер) # вторым параметром указываем дочернюю папку
sys.path.append(folder)  # path - временное окружение # делает видимым путь

import handler_db


handler_db.db_root = folder + path.sep  # sep слэш под каждую систему свой

bot = t.TeleBot(settings.TOKEN)

start_date = '15'
finish_date = '03'
plus_period_days = 56
# 157758328, - это я
krs_list = [
    # 157758328,
            240176167, 5208899957, 5275895896, 5006193045, 1068718455, 417491851,
            953262479]  # 5006193045 Алексеев КРС # 202 Алексеев обычный

stop_list = [100585, 111846, 101851, 122527, 101993, 104245, 104148, 105050, 105326, 104694, 100509, 124575, 120845,
             102295, 110127, 100667, 105249, 120036, 105251, 104259, 104331, 104911, 119185, 100609, 105261, 100610,
             104161, 102607]


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
    btn1 = types.KeyboardButton('Заказать\nвыходной')
    # btn2 = types.KeyboardButton('Свободные\nдаты')
    btn3 = types.KeyboardButton('Удалить\nвыходной')
    btn4 = types.KeyboardButton('Выгрузить таблицу')
    # btn5 = types.KeyboardButton('Выйти')
    select_action.add(btn1, btn3, btn4)
    return select_action


def select_action_in_cancel():
    """При выдаче заказанных дней спрашивает что сдлеать с заказанными днями"""
    select_action_in_cancel_btns = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Заказать\nвыходной')
    btn3 = types.KeyboardButton('Отменить\nвыходной')
    btn4 = types.KeyboardButton('Свободные\nдаты')
    btn5 = types.KeyboardButton('Выйти')
    select_action_in_cancel_btns.add(btn1, btn3, btn4, btn5)
    return select_action_in_cancel_btns


def select_position():
    position_btn = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    ipb = types.KeyboardButton('ИПБ')
    sb = types.KeyboardButton('СБ')
    bs = types.KeyboardButton('BS')
    simple = types.KeyboardButton('БП')
    position_btn.add(ipb, sb, bs, simple)
    return position_btn


def otdelenie():
    otdelenie_btn = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    svo = types.KeyboardButton('Шереметьево')
    led = types.KeyboardButton('Пулково')
    kja = types.KeyboardButton('Красноярск')
    otdelenie_btn.add(svo).add(led).add(kja)
    return otdelenie_btn


def check_or_add_tab_surname_name_to_db(message):
    """добавляет нового пользователя в случае представления"""
    mess = message.text.split()
    if len(mess) == 3 and message.text.split()[0].isdigit() and len(message.text.split()[0]) > 2:
        user_id = message.chat.id
        tab_number = message.text.split()[0]
        name = message.text.split()[2].capitalize()
        surname = message.text.split()[1].capitalize()
        user_id_in_db = handler_db.get_user_id_by_tab_number(
            tab_number)  # получить по табельному месадж чат айди и потом проверить по полученому месадж чат ай ди его доступ
        if user_id_in_db:
            # bot.send_message(157758328,
            #                  f'{message.text} Этот пользователь уже был зарегестрирваон в базе ранее')  # добавлено для теста
            return True  # False поменял на True
        else:
            handler_db.add_new_user_to_db_users_from_day_order(user_id, surname, name, tab_number)
            # bot.send_message(157758328,
            #                  f'добавлен новый пользователь {user_id}, {surname}, {name}, {tab_number}')  # добавлено для теста
            return True
    else:
        # добавлено для теста
        # bot.send_message(157758328,
        #                  f'НЕ добавлен новый пользователь {message.text} len(mess) == 3 {len(mess) == 3} and message.text.split()[0].isdigit() {message.text.split()[0].isdigit()} and len(message.text.split()[0]) > 2 {len(message.text.split()[0]) > 2}')
        return False


def get_future_date():
    days = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31, }
    future_month_dict_names = {1: 'ЯНВАРЬ', 2: "ФЕВРАЛЬ", 3: "МАРТ", 4: "АПРЕЛЬ", 5: "МАЙ", 6: "ИЮНЬ", 7: "ИЮЛЬ",
                               8: "АВГУСТ", 9: "СЕНТЯБРЬ", 10: "ОКТЯБРЬ", 11: "НОЯБРЬ", 12: "ДЕКАБРЬ", }
    current_datetime = time.strftime('%d.%m.%Y %H:%M')
    current_month = time.strftime('%m')

    dt_utc = datetime.strptime(current_datetime, '%d.%m.%Y %H:%M').replace(tzinfo=pytz.utc)
    dt_future = dt_utc.astimezone(pytz.utc) + timedelta(days=plus_period_days)  # 48 # TODO плюс day на 266 строке закоментить
    future_month_int = int(dt_future.month)
    future_year = str(dt_future.year)[2:]
    future_month_big_name = future_month_dict_names[future_month_int]

    if current_month == '12':
        future_month_big_name_forbidden = future_month_dict_names[1]
    else:
        future_month_big_name_forbidden = future_month_dict_names[int(current_month) + 1]
    return future_month_int, days[future_month_int], future_month_big_name, future_year, future_month_big_name_forbidden


def check_true_position(message):
    """Проверяет правильность введеной позиции"""
    if message.text.lower() in "инструктор ипб":
        return "ИПБ"
    if message.text.lower() in "бортпроводник бп рядовой провод проводник":
        return "БП"
    if message.text.lower() in "бизнес класс бизнес-класс bs":
        return "BS"
    if message.text.lower() in "сб старший бортпроводник":
        return "СБ"
    else:
        return False


def check_true_oke(message):
    """Проверяет корректность введеного номера отряда"""
    oke = ''
    if message.text.lower() in "шереметьево москва":
        oke = "Шереметьево"
    if message.text.lower() in "пулково питер санкт-петербург":
        oke = "Пулково"
    if message.text.lower() in "красноярск емельяново":
        oke = "Красноярск"
    return oke


def check_true_date(message):
    """Проверяет насколько корректно ввдена дата. Возвращает False Либо дату/ Дату """
    future_month_int, future_days, future_month_big_name, future_year, forbidden = get_future_date()  # формирует путем прибавления определнного числа к введенному числу, чтобы сформировать желаему дату
    months_list = ['января', "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября",
                   "ноября", "декабря"]
    day = ''
    comment = '-'

    if ' ' in message:
        date = message.split(' ')[0]
        if message.split(' ')[1:]:
            second_part = message.split(' ')[1:]
            second_part = ' '.join(second_part)
        else:
            comment = '-'
        for m in months_list:
            if m in second_part:
                comment = second_part.replace(m, '')

        if '/' in date:
            day = date.split('/')[0]
            requested_month = date.split('/')[1]
            if requested_month == '' or int(requested_month) != future_month_int:
                if len(str(future_month_int)) < 2:
                    future_month = '0' + str(future_month_int)
                else:
                    future_month = str(future_month_int)
                return f'{day}.{future_month}.{future_year}', comment
        if ',' in date:
            day = date.split(',')[0]
            requested_month = date.split(',')[1]
            if requested_month == '' or int(requested_month) != future_month_int:
                if len(str(future_month_int)) < 2:
                    future_month = '0' + str(future_month_int)
                else:
                    future_month = str(future_month_int)
                return f'{day}.{future_month}.{future_year}', comment
    if '.' in message:
        day = message.split('.')[0]
        requested_month = message.split('.')[1]
        if message.split(' ')[1:]:
            comment = message.split(' ')[1:]
            comment = ' '.join(comment)
        else:
            comment = '-'
            try:
                if requested_month == '' or int(requested_month) != future_month_int:
                    return f'month_incorrect', False
            except Exception:
                return False, False

    if message.isdigit():
        day = message
        comment = '-'
    if len(message.split()) > 1:
        if message.split()[0].isdigit():
            day = message.split()[0]
            # comment = message.split()[1]
    if day and len(day) < 2:
        day = '0' + day
    if not day.isdigit():
        return False, False
    if len(day) > 2 or abs(int(day)) > future_days:
        return False, False
    if day is None:
        return False, False
    else:
        if len(str(future_month_int)) < 2:
            future_month = '0' + str(future_month_int)
        else:
            future_month = str(future_month_int)
        return f'{day}.{future_month}.{future_year}', comment.strip()


def convert_month_end(lower_month):
    """Получает будущий месяц в именительном падеже, на который заказываем выходной. Формирует правильное окончание у
    месяца для будущей подстановки месяца в пример даты как образец запроса."""
    if lower_month in 'август март':
        lower_month += 'а'
    else:
        lower_month = lower_month[:-1] + 'я'
    return lower_month


def convert_month_int():
    """Функия для подстановки верной строки числового выражения месяца в образец текста для заказа выходных.
    Проверяет нужно ли добавить ноль перед числом месяца, если нужно - добавляет, возвращает с нолем"""
    month_int = get_future_date()[0]
    if month_int < 10:
        month_int = '0' + str(month_int)
    return month_int


def permission_period():
    """Извлекает текущее время, на основе него разрешает принимать выходные или нет. Автоматизирует запуск и завершение приема выходных."""
    current_datetime = time.strftime('%d.%m.%Y %H:%M')
    dt = datetime.strptime(current_datetime, '%d.%m.%Y %H:%M')

    hour = dt.strftime('%H')
    minute = dt.strftime('%M')
    day = dt.strftime('%d')
    month = dt.strftime('%m')
    year = dt.strftime('%Y')


    # day = '26'

    current_time = f'{hour}:{minute}'

    if start_date <= day <= '31' or '01' <= day <= finish_date:  # current_time >= '00:00' and
        return True
        # print(f'Заказ выходных принимаются.')
    else:
        return False
        # print(f'Заказ выходных прекращен')


def convert_from_month():
    """Функия для подстановки верной строки числового выражения месяца в образец текста для заказа выходных.
    Проверяет нужно ли добавить ноль перед числом месяца, если нужно - добавляет, возвращает с нолем"""
    future_date_int = get_future_date()[0]
    if future_date_int == 1:
        month_int = 11
    elif future_date_int == 2:
        month_int = 12
    else:
        month_int = future_date_int-2
    if month_int < 10:
        month_int = '0' + str(month_int)
    return month_int


def convert_till_month():
    """Функия для подстановки верной строки числового выражения месяца в образец текста для заказа выходных.
    Проверяет нужно ли добавить ноль перед числом месяца, если нужно - добавляет, возвращает с нолем"""
    future_date_int = get_future_date()[0]
    if future_date_int == 1:
        month_int = 12
    else:
        month_int = future_date_int - 1

    if month_int < 10:
        month_int = '0' + str(month_int)
    return month_int


future_month_int = get_future_date()[0]
future_month_big_name = get_future_date()[2]
future_month_big_name_forbidden = get_future_date()[4]
from_month = convert_from_month()
till_month = convert_till_month()
permission_message = f'С 15.07 по 3.08 заказы принимаются на СЕНТЯБРЬ.'  # "'На данный момент заказы на выходные не принимаются. \n\nС 00:00 25 мая будет открыт прием заявок на выходные дни в ИЮЛЕ. \n\nПо всем вопросам и проблемам с заказом выходных обращаться напрямую к разработчику @DeveloperAzarov.'
forbidden_message = f'Прием выходных на СЕНТЯБРЬ прекращен. \n' \
                    f'Выходные на ОКТЯБРЬ будут приниматься с 15.08 по 3.09.\n' \
                    f'Если Вам требуется отменить ранее заказанный выходной - ' \
                    f'обратитесь к своему начльнику ОКЭ.'

# permission_message = f'С 25.{from_month} по 8.{till_month} заказы принимаются на {future_month_big_name}.'  # "'На данный момент заказы на выходные не принимаются. \n\nС 00:00 25 мая будет открыт прием заявок на выходные дни в ИЮЛЕ. \n\nПо всем вопросам и проблемам с заказом выходных обращаться напрямую к разработчику @DeveloperAzarov.'
# forbidden_message = f'Прием выходных на {future_month_big_name_forbidden} прекращен. Выходные на {future_month_big_name} ' \
#                     f'будут приниматься с 25.{from_month} по 8.{till_month}.\n Если Вам требуется отменить ранее заказанный выходной - ' \
#                     f'обратитесь к своему начльнику ОКЭ.'


def notification(message):
    if permission_period():
        bot.send_message(message.chat.id, permission_message)
    if not permission_period():
        bot.send_message(message.chat.id, forbidden_message)
        return


bot.send_message(157758328, f"бот перезапущен", reply_markup=select_action_krs())


@bot.message_handler(commands=['start'])
def welcome(message):
    """При первом подключении пользователя к боту - выводит приветсвенный стикер, приветсвенную речь."""
    # TODO УВЕДОМЛЕНИЕ!! (всего три 259, 288, 292) RETURN ВХОДИТ В УВЕДОМЛЕНИЕ

    with open('static/AnimatedSticker.tgs', 'rb') as sti:
        bot.send_sticker(message.chat.id, sti)
        notification(message)
    if handler_db.check_access(message.chat.id):
        name = handler_db.get_name_surname(message.chat.id).split()[0]
        # bot.send_message(message.chat.id, permission_message, reply_markup=select_action())
    elif message.chat.id in krs_list:
        bot.send_message(message.chat.id, f'Бот находится в режиме КРС.', reply_markup=select_action_krs())
    elif message.chat.id not in krs_list:
        bot.send_message(message.chat.id, f'Чем могу помочь?', reply_markup=select_action_krs())
    else:
        bot.send_message(message.chat.id,
                         f"Представьтесь, пожалуйста. Напишите свой табельный номер, фамилию, имя через пробел. Например: \n123456 Смирнов Иван")
        return


order_dict = {}


@bot.message_handler(content_types=["text"])  #
def conversation(message):

    if "написать по id" in message.text.lower():
        mess = message.text.split()
        try:
            bot.send_message(int(mess[3]), ' '.join(mess[4:]).capitalize())
            bot.send_message(157758328, "Сообщение пользователю отправлено успешно.")
        except Exception:
            bot.send_message(157758328, f"Пользователь не подключен к телеграм-боту.\n {traceback.format_exc()}")
        return

    if message.chat.id not in krs_list:
        if not permission_period():
            notification(message)  # TODO RETURN внутри функции
            return
        order_dict[message.chat.id] = {}

    if not handler_db.check_access(message.chat.id):  # not in krs_list: # TODO можно ли сюда добавить not in krs_list чтоб инструктора не представлялись каждый раз
        if check_or_add_tab_surname_name_to_db(message):
            name_surname = handler_db.get_name_surname(
                message.chat.id)  # TODO как избежать двойной проверки в базе данных
            if name_surname:
                name = name_surname.split()[0]
                surname = name_surname.split()[1]
            else:
                tab_number = message.text.split()[0]
                surname = message.text.split()[1]
                name = message.text.split()[2]
                handler_db.add_new_user_to_db_users_from_day_order(message.chat.id, surname, name, tab_number)
                notification(message)
                # TODO Stop_list реализован здесь
                # if tab_number in stop_list:
                #     bot.send_message(message.chat.id, f"{name}, для заказа выходного обратитесь к начальнику Вашего отделения.")
                #     return
                if message.chat.id in krs_list:
                    bot.send_message(message.chat.id, f"{name}, чем могу помочь?", reply_markup=select_action_krs())
        else:
            notification(message)
            bot.send_message(message.chat.id,
                             f"Представьтесь, пожалуйста. Напишите свой табельный номер, фамилию, имя через пробел без других лишних символов, например: \n123456 Иванов Иван")
            return

    # if message.text.lower() in "/day_order заказ\nвыходных заказ выходных":
    #     bot.send_message(message.chat.id, f'С 25 февраля по 5 марта заказы принимаются на {get_future_date()[2]}.')

    # if message.chat.id not in krs_list: # TODO нельзя это делать потому что потом нужна переменная name
    user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, \
    autoconfirm, time_depart = handler_db.fetch_user_for_plan(message.chat.id)

    ask_order_or_cancel = f"{name}, Вы хотите заказать выходной или отменить ранее заказанный выходной?"

    ask_position = 'Укажите Вашу позицию в экипаже'
    lower_month = get_future_date()[2].lower()
    lower_month = convert_month_end(lower_month)
    future_month_int = convert_month_int()
    ask_date = f'Укажите дату в любом формате, например: \n25\n25.{future_month_int}\n25.{future_month_int}.22\n25 {lower_month}\n\n' \
               '' \
               'Один запрос может содержать только одну дату. \n' \
               '\n*На какую дату Вы бы хотели заказать выходной?*'
    ask_oke = "Укажите Вашу локацию"

    if "удалить" == message.text.lower():
        bot.send_message(message.chat.id,
                         f'Чтобы отменить заказанный выходной, напишите слово удалить и число, например:\n\n'
                         f'удалить 25')  # if "удалить выходной " будет написано в общем коде
        return

    def output_free_dates1(message):
        """Проверяет должность position и записывает ее базу. Выдает список свободных дат по запросу"""
        if check_true_position(message):
            message.text = check_true_position(message)
            # position = order_dict[message.chat.id]['position'] = message.text
            position = handler_db.update_position(message.chat.id, message.text)
            tab_number = handler_db.get_tab_number(message.chat.id)
            oke = order_dict[message.chat.id]['oke']
            oke = handler_db.get_oke(tab_number)
            free_dates = handler_db.check_free_dates(position, oke)
            ordered_before = handler_db.what_dates_order(tab_number)
            output_free_dates = None
            name_surname = handler_db.get_name_surname(message.chat.id)


            if free_dates == '':

                # if oke == "Красноярск":
                #     bot.send_message(message.chat.id,
                #                      f'К сожалению, инструкторам из Красноярска нельзя заказывать выходные.',
                #                      reply_markup=select_action(), parse_mode='Markdown')
                #     bot.send_message(157758328,
                #                      f'Выдано сообщение, что инструкторам из Красноярска нельзя заказывать выходные.',
                #                      reply_markup=select_action_krs(), parse_mode='Markdown')
                #     return
                #
                # else:
                if oke is None:
                    bot.send_message(message.chat.id,
                                     f'Для начала укажите свою локацию.',
                                     reply_markup=otdelenie(), parse_mode='Markdown')
                    msg58 = bot.send_message(message.chat.id, ask_oke, reply_markup=otdelenie(), parse_mode='Markdown')
                    bot.register_next_step_handler(msg58, ask_position_func_1)
                    return

                bot.send_message(message.chat.id,
                             f'Нет свободных дат, доступных для заказа для {position} из {oke}. Всё занято.',
                             reply_markup=select_action(), parse_mode='Markdown')
                bot.send_message(157758328,
                             f'Выдано сообщение пользователю {message.chat.id} {tab_number} {name_surname}, Нет свободных дат, доступных для заказа для {position} из {oke}. Всё занято.',
                             reply_markup=select_action_krs(), parse_mode='Markdown')
                return

            for i in free_dates.split('\n'):
                for j in ordered_before.split('\n'):
                    if j == '':
                        continue
                    if j in i:
                        output_free_dates = free_dates = free_dates.replace(f'{i}\n', '')
                if output_free_dates is None:
                    output_free_dates = free_dates
            if output_free_dates != '':
                bot.send_message(message.chat.id,
                                 f'Свободные даты, доступные Вам для заказа: \n{output_free_dates}',
                                 reply_markup=select_action(), parse_mode='Markdown')
                return
            else:
                bot.send_message(message.chat.id,
                                 f'Вам доступен для заказа любой день.',
                                 reply_markup=select_action(), parse_mode='Markdown')
            return
        else:
            bot.send_message(message.chat.id,
                             "Необходимо вводить Вашу позицию в экипаже корректно и нажимать на кнопки, представленные ниже. Нажмите Выйти и начните процедуру заново.")
            return

    def ask_position_func_1(message):
        """записывает окэ, спрашивает позицию для свободных дат"""
        oke = check_true_oke(message)
        # order_dict[message.chat.id]['oke'] = oke
        # bot.send_message(157758328, f'локация {oke}')
        # tab_number = handler_db.get_tab_number(message.chat.id)
        res = handler_db.update_oke(message.chat.id, oke)
        # bot.send_message(157758328, f'{message.chat.id} локация res oke {res}')
        msg667 = bot.send_message(message.chat.id, ask_position, reply_markup=select_position(), parse_mode='Markdown')
        bot.register_next_step_handler(msg667, output_free_dates1)
        return

    def start_04(message):
        """Проверяет дату на корректность, заносит дату в словарь...."""
        date, comment = check_true_date(message.text)

        if date == 'month_incorrect':
            bot.send_message(message.chat.id,
                             f"Выходные на этот месяц не принимаются. На данный момент, выходные принимаются на {get_future_date()[2]}.",
                             reply_markup=select_action())
            return

        # TODO временное ограничение
        # day = date.split('.')[0]
        # if 1 <= day <= 8:
        #     bot.send_message(message.chat.id,
        #                      f"Для заказа выходных на эти даты воспользуйтесь другим ботом @dob_vacations_bot",
        #                      reply_markup=select_action())
        #     return

        if type(date) is bool:
            bot.send_message(message.chat.id, f"Введенная дата некорректна. Начните процедуру заново.",
                             reply_markup=select_action())
            return

        order_dict[message.chat.id]['comment'] = comment
        tab_number = handler_db.get_tab_number(message.chat.id)

        oke = handler_db.get_oke(tab_number)
        # handler_db.update_oke(message.chat.id, oke)
        ordered_days = handler_db.what_dates_order(tab_number)
        position = handler_db.get_position(tab_number)

        ordered_before = handler_db.check_ordered_before(date=date, tab_number=tab_number)

        if ordered_before:
            bot.send_message(message.chat.id, f"Сейчас у Вас заказан выходной на\n{ordered_days}",
                             reply_markup=select_action())
            return

        more_two_days_in_row = handler_db.check_two_days_in_row(date=date, tab_number=tab_number)
        if more_two_days_in_row:
            bot.send_message(message.chat.id,
                             f"Заказать можно не более двух дней подряд. \nУ Вас уже заказаны даты:\n{ordered_days}",
                             reply_markup=select_action())
            return

        if date:
            order_dict[message.chat.id]['date'] = date
            available = handler_db.check_free_place(date, position, oke)

            free_days_before = int(available)
            if free_days_before > 0:
                #TODO ###################################################### ВРЕМЕННОЕ ОГРАНИЧЕНИЕ
                result_int = handler_db.count_strings(oke, date, position)
                # bot.send_message(157758328, f'{date} {position} {oke}  в базе {result_int} дней. type result_int {type(result_int)}',
                #                  reply_markup=select_action_krs())
                if position == 'СБ' and result_int >= 7:
                    bot.send_message(message.chat.id, f'{name}, {date} свободные места закончились. Предлагаем '
                                                      f'рассмотреть другие даты.', reply_markup=select_action())
                    # bot.send_message(157758328, f'547-570: id {message.chat.id} {position} {surname} {name} {tab_number} из {oke}\n'
                    #                             f'сработало временное ограничение, отказано в заказе на {date}.',
                    #              reply_markup=select_action_krs())
                    return
                if position == 'БП' and result_int >= 12:
                    bot.send_message(message.chat.id, f'{name}, {date} свободные места закончились. Предлагаем '
                                                      f'рассмотреть другие даты.', reply_markup=select_action())
                    # bot.send_message(157758328, f'547-570: id {message.chat.id} {position} {surname} {name} {tab_number} из {oke}\n'
                    #                             f'сработало временное ограничение, отказано в заказе на {date}.',
                    #              reply_markup=select_action_krs())
                    return
                if position == 'BS' and result_int >= 7:
                    bot.send_message(message.chat.id, f'{name}, {date} свободные места закончились. Предлагаем '
                                                      f'рассмотреть другие даты.', reply_markup=select_action())
                    # bot.send_message(157758328, f'547-570: id {message.chat.id} {position} {surname} {name} {tab_number} из {oke}\n'
                    #                             f'сработало временное ограничение, отказано в заказе на {date}.',
                    #              reply_markup=select_action_krs())
                    return
                if position == 'ИПБ' and result_int >= 2:
                    bot.send_message(message.chat.id, f'{name}, {date} свободные места закончились. Предлагаем '
                                                      f'рассмотреть другие даты.', reply_markup=select_action())
                    # bot.send_message(157758328, f'547-570: id {message.chat.id} {position} {surname} {name} {tab_number} из {oke}\n'
                    #                             f'сработало временное ограничение, отказано в заказе на {date}.',
                    #              reply_markup=select_action_krs())
                    return
                # TODO ###################################################### ВРЕМЕННОЕ ОГРАНИЧЕНИЕ

                handler_db.update_date(date, tab_number, surname, name, position, oke,
                                       comment)
                bot.send_message(message.chat.id, f'{name}, дата {date} успешно записана.',
                                 reply_markup=select_action())
                ordered_end = 'заказала' if name[-1:] == 'а' or name[-1:] == 'я' else "заказал"
                bot.send_message(157758328, f'535: id {message.chat.id} {position} {surname} {name} {tab_number} из {oke} {ordered_end} выходной на {date}.',
                                 reply_markup=select_action_krs())
                # counter_days = handler_db.get_counter_days(tab_number)
                ordered_days = handler_db.what_dates_order(tab_number)
                bot.send_message(message.chat.id,
                                 f'Ваш заказ выходных на {get_future_date()[2]}:\n{ordered_days}',
                                 reply_markup=select_action())
                # time.sleep(2)
                # bot.send_message(message.chat.id, f'{name}, Вам понравилась возможность заказа выходных дней через Telegram? \n'
                #                                   f'Предлагаю Вам добровольно пожертвовать любую сумму на поддержку бота переводом по номеру телефона 89992023315.\n\n'
                #                                   f'Существование этого бота не бесплатное. Ежемесячно регистратору (провадйеру) '
                #                                   f'я плачу по 3000 руб. за хостинг, аренду сервера, SSL-сертификаты, домен и т.д. чтобы этот бот был доступен... '
                #                                   f'Финансировать этого бота ежемесячно за свой счет я устал и нахожу несправедливым, в силу разных очевидных причин, '
                #                                   f'либо будем собирать заказы на выходные по-старому.\n '
                #                                   f'{name}, большое спасибо.',
                #                  reply_markup=select_action())
                return
            else: # TODO ПОПРОБУЕМ если что убрать 566-568

                if oke == '' or oke is None: #TODO проверка попробовал исправить когда нет оке и выдавал сообщение что нет дат
                    bot.send_message(message.chat.id, f'{name}, для того чтобы ответить, мне нужно знать все Ваши необходимые данные. Вы указали Ваш базовый аэропорт?', reply_markup=otdelenie(), parse_mode='Markdown')
                    msg58 = bot.send_message(message.chat.id, ask_oke, reply_markup=otdelenie(), parse_mode='Markdown')
                    bot.register_next_step_handler(msg58, ask_position_func_1)
                    return
                
                else:
                    bot.send_message(message.chat.id,
                                 f'{date} не осталось свободных мест, либо на этот день нельзя заказать выходной день.\n'
                                 f'Попробуйте эти даты проверить позже, возможно кто-то из бортпроводников отменит свои выходные {date}.',
                                 reply_markup=select_action())

                    bot.send_message(157758328, f'id {message.chat.id} {position} {surname} {name} {tab_number}-{oke}, \nне смог заказать выходной {date} available: {available} \n\n'
                                     f'554: {date} не осталось свободных мест.')
                    bot.send_message(message.chat.id, f'{name}, давайте посмотрим, когда можно заказать выходной...\n',
                                     reply_markup=select_action())
                    free_dates()
                    return
        else:
            bot.send_message(message.chat.id, f'Введенная дата некорректна. Нажмите Выйти и начните процедуру заново.',
                             reply_markup=select_action())
            return

    def start_003(message):
        """записывает оке в общую базу данных и словарь спрашивает желаемую дату"""
        oke = check_true_oke(message)
        handler_db.update_oke(message.chat.id, oke)
        msg41 = bot.send_message(message.chat.id, ask_date, parse_mode='Markdown')
        bot.register_next_step_handler(msg41, start_04)

    def start_03(message):
        """Проверяет позицию на корректность, заносит позицию в две базы данных
        спрашивает желаемую дату"""
        if check_true_position(message):
            message.text = check_true_position(message)
            handler_db.update_position(message.chat.id, message.text)
            msg58 = bot.send_message(message.chat.id, ask_oke, reply_markup=otdelenie(), parse_mode='Markdown')
            bot.register_next_step_handler(msg58, start_003)
            return
        else:
            bot.send_message(message.chat.id,
                             "Необходимо вводить Вашу позицию в экипаже корректно и нажимать на кнопки, представленные ниже. Начните процедуру заново.")
            return

    def check_limit():
        """Проверяет исчерпан ли лимит в три дня у конкретного бортпроводника"""
        tab_number = handler_db.get_tab_number(message.chat.id)
        three_days = handler_db.check_three_days_in_row(tab_number)
        if three_days:
            ordered_days = handler_db.what_dates_order(tab_number)
            bot.send_message(message.chat.id,
                             f"{name}, заказать можно не более трех дней в месяц. \nВаши заказанные дни:\n{ordered_days}",
                             reply_markup=select_action())
            return True
        else:
            return False

    def delete_day(message):
        """удаляет ранее заказанный выходной день"""
        tab_number = handler_db.get_tab_number(message.chat.id)

        try:
            day = message.text.split()[1]
        except Exception as exc:
            bot.send_message(157758328,
                             f'625: ОШИБКА {exc}\n'
                             f'id {message.chat.id} {surname} {name} {tab_number}, \nне смог удалить выходной \n'
                             f'Попытались извлечь второе слово с индексом [1] - должен быть day из строки message.text: {message.text}')
            bot.send_message(message.chat.id,
                             f"{name}, убедительна просьба делать так, как просят это в сообщениях выше. \n"
                             f"За один раз вы можете удалить только одну дату, для этого надо в одном сообщении написать один раз слово удалить и через пробел один раз число, например: удалить 25\n"
                             f"Возможно, Вы что-то сделали не так и произошла ошибка {exc}. \n"
                             f"Отправьте скриншот на @DeveloperAzarov.",
                             reply_markup=select_action())
            return

        date = check_true_date(day)[0]
        ordered_days = handler_db.what_dates_order(tab_number)
        was_ordered = None

        if day in ordered_days:
            was_ordered = True

        try:
            dates = handler_db.delete_date(tab_number, date)
            if date not in dates:
                if was_ordered:
                    bot.send_message(message.chat.id, f"{day} числа выходной успешно удален.", reply_markup=select_action())
                    bot.send_message(157758328,
                                     f'615: id {message.chat.id} {tab_number} {surname} {name} удалил выходной {date}')
                else:
                    bot.send_message(message.chat.id, f"{day} числа у Вас не было заказано выходного дня.",
                                     reply_markup=select_action())
        except Exception as exc:
            bot.send_message(157758328,
                             f'621: ОШИБКА {exc}\n'
                             f'id {message.chat.id} {surname} {name} {tab_number}, \nне смог удалить выходной \n'
                             f'date: {date}\n'
                             f'dates: {dates}\n')
            bot.send_message(message.chat.id, f"Возможно, Вы что-то сделали не так и произошла ошибка {exc}. Отправьте скриншот на @DeveloperAzarov.", reply_markup=select_action())

        if dates:
            bot.send_message(message.chat.id, f"Ваши заказанные даты:\n{dates}", reply_markup=select_action())
        else:
            bot.send_message(message.chat.id, f"У Вас нет заказанных выходных.", reply_markup=select_action())
        return

    def free_dates():
        if check_limit():
            return
        else:
            oke = handler_db.get_oke(handler_db.get_tab_number(message.chat.id))
            if oke == '' or oke is None:
                msg66555 = bot.send_message(message.chat.id, ask_oke, reply_markup=otdelenie(), parse_mode='Markdown')
                bot.register_next_step_handler(msg66555, ask_position_func_1)
                return
            if handler_db.get_position(handler_db.get_tab_number(message.chat.id)) is None:
                msg552 = bot.send_message(message.chat.id, ask_position, reply_markup=select_position(),
                                          parse_mode='Markdown')
                bot.register_next_step_handler(msg552, output_free_dates1)
                return
            else:
                message.text = handler_db.get_position(handler_db.get_tab_number(message.chat.id))
                output_free_dates1(message)
                return

    if message.text.lower() in ["выйти", "отмена", "стоп", "отбой", "назад"]:
        bot.send_message(message.chat.id, f"{name}, хорошего дня!")
        return

    if "удалить пользователя" in message.text.lower():
        user = message.text.split()
        handler_db.delete_user_from_db(user[-1])
        result = handler_db.select_all_data_of_person(user[-1])
        bot.send_message(157758328, result)
        return

    if "добавить позицию" in message.text.lower():
        user_id = message.text.split()[-2]
        position = message.text.split()[-1]
        handler_db.update_position(user_id, position)
        result = handler_db.select_all_data_of_person(user_id)
        bot.send_message(157758328, result)
        return

    if "добавить отряд" in message.text.lower():
        user_id = message.text.split()[-2]
        oke = message.text.split()[-1]
        handler_db.update_oke(user_id, oke)
        result = handler_db.select_all_data_of_person(user_id)
        bot.send_message(157758328, result)
        return

    if "очистить базу данных пользователей отчистить базу данных пользователей" in message.text.lower(): # TODO не работает проверить почему
        handler_db.to_create_general_db()
        handler_db.import_users_to_excel()
        bot.send_document(message.chat.id, open('general_db.xlsx', "rb"))
        bot.send_message(157758328, "база данных пользователй очищена.")
        return

    if 'сохранить пользователей в excel' in message.text.lower() and message.chat.id == 157758328:
        handler_db.import_users_to_excel()
        bot.send_document(message.chat.id, open('general_db.xlsx', "rb"))
        return

    # if "создать таблицу на новый месяц" in message.text.lower():
    #     to_create_day_off_requests_db()
    #     from_day_dict_to_sql(day_off_30_dict.day_off_dict, 'day_off')

    if "2DH64rf2" in message.text.lower():
        bot.send_document(message.chat.id, "- сохранить пользователей в excel \n"
                                           "- очистить базу данных пользователей\n"
                                           "- добавить отряд message.chat.id N\n"
                                           "- добавить позицию message.chat.id BS\n"
                                           "- удалить пользователя message.chat.id\n")
        return

    if message.chat.id in krs_list:

        if (message.text.lower() in "сохранить выходные в excel выгрузить таблицу") and message.chat.id in krs_list:
            handler_db.import_daysoff_to_excel()
            bot.send_document(message.chat.id, open(f'ordered_days.xlsx', "rb"), reply_markup=select_action_krs())
            # ordered_days_total = handler_db.count_lines()
            # bot.send_document(message.chat.id, f'уже заказано {ordered_days_total} выходных на данный момент. ', reply_markup=select_action_krs())
            bot.send_message(157758328, f" файл с таблицей отправлен", reply_markup=select_action_krs())
            return

        if message.text.lower() in "заказать выходной заказать\nвыходной":
            bot.send_message(message.chat.id,
                             f'Введите через пробел табельный номер бортпроводника, его фамилию и имя, например: \n123456 Смирнов Иван',
                             reply_markup=select_action_krs())
            return
        try:
            if len(message.text.split()) == 3 and message.text.split()[0].isdigit():
                order_dict[message.chat.id] = {}
                order_dict[message.chat.id]['tab_number'] = tab_number = message.text.split()[0]
                order_dict[message.chat.id]['surname'] = surname = message.text.split()[1].capitalize()
                order_dict[message.chat.id]['name'] = name = message.text.split()[2].capitalize()
                try:
                    oke = handler_db.get_oke(tab_number)
                    # order_dict[message.chat.id]['oke'] = oke
                    if oke is None:
                        bot.send_message(message.chat.id, f'Базовый аэропорт бортпроводника?', reply_markup=otdelenie())
                        return
                    bot.send_message(157758328,
                                     f"записаны данные табельный: {order_dict[message.chat.id]['tab_number']} фамилия: {order_dict[message.chat.id]['surname']} name: {order_dict[message.chat.id]['name']} oke: {oke}")
                    bot.send_message(message.chat.id,
                                     f"На какое число заказать выходной в {get_future_date()[2].lower()[:-1]}е? \n\nВведите число, например: 12",
                                     reply_markup=select_action_krs())
                    return
                except Exception:
                    bot.send_message(message.chat.id, f'Базовый аэропорт бортпроводника?', reply_markup=otdelenie())
                    return

            elif message.text in ['Шереметьево', "Пулково", "Красноярск"]:
                oke = check_true_oke(message)
                # order_dict[message.chat.id]['oke'] = oke
                name = order_dict[message.chat.id]['name']
                handler_db.update_oke(message.chat.id, oke)
                bot.send_message(message.chat.id, f'Укажите дату')
                return

            elif message.text.split()[0].isdigit() and len(message.text.split()[0]) <= 2:  # проверяет дату
                # bot.send_message(157758328,
                #                  f"message.text.split()[0].isdigit() {message.text.split()[0].isdigit()} len(message.text.split()[0]) <= 2 {len(message.text.split()[0]) <= 2}")
                order_dict[message.chat.id]['date'] = check_true_date(message.text.split()[0])[0]
                name = order_dict[message.chat.id]['name']
                bot.send_message(message.chat.id, f'Укажите позицию в экпиаже', reply_markup=select_position())
                return

            elif message.text.isalpha() and check_true_position(message):
                order_dict[message.chat.id]['position'] = position = check_true_position(message)
                tab_number = order_dict[message.chat.id]['tab_number']
                date = order_dict[message.chat.id]['date']
                oke = handler_db.get_oke(tab_number)
                ordered_before = handler_db.check_ordered_before(date=date, tab_number=tab_number)
                ordered_days = handler_db.what_dates_order(tab_number)
                two_days = handler_db.check_two_days_in_row(date, tab_number)
                three_days = handler_db.check_three_days_in_row(tab_number)
                counter_days = handler_db.get_counter_days(tab_number)
                if two_days:
                    bot.send_message(message.chat.id, f'Вы попытались заказать более двух дней подряд, либо заказываете ту дату, которая уже была заказана.')
                    bot.send_message(message.chat.id,
                                     f'уже заказано на {get_future_date()[2]} месяц {counter_days} дн.:\n{ordered_days}',
                                     reply_markup=select_action_krs)
                    bot.send_message(message.chat.id, f'Выходной на {date} не заказн.')
                    return
                if three_days:
                    bot.send_message(message.chat.id,
                                     f'У этого бортпроводника превышен трехдневных лимит на заказ выходных.')
                    bot.send_message(message.chat.id,
                                     f'уже заказано на {get_future_date()[2]} месяц {counter_days} дн.:\n{ordered_days}',
                                     reply_markup=select_action_krs())
                    bot.send_message(message.chat.id, f'Выходной на {date} не заказн.')
                    return

                date, comment = check_true_date(date)

                # TODO временное ограничение
                day = date.split('.')[0]
                if 1 <= int(day) <= 8 and date.split('.')[1] == '01':
                    bot.send_message(message.chat.id,
                                     f"Для заказа выходных {date} даты воспользуйтесь другим ботом @dob_vacations_bot.  Там можно заказать любое количество дней с 1 по 8 число, хоть один день, хоть все восемь.",
                                     reply_markup=select_action())
                    bot.send_message(157758328, f"790: направили {tab_number} {surname} {name} в другого бота с датой {date}")

                    return
                order_dict[message.chat.id]['comment'] = comment
                if date == 'month_incorrect':
                    bot.send_message(message.chat.id,
                                     f"Выходные на этот месяц не принимаются. На данный момент, выходные принимаются на {get_future_date()[2]}.",
                                     reply_markup=select_action_krs())
                    return
                if type(date) is bool:
                    bot.send_message(message.chat.id, f"Введенная дата некорректна. Начните процедуру заново.",
                                     reply_markup=select_action_krs())
                    return

                if ordered_before:
                    bot.send_message(message.chat.id, f"Сейчас у Вас заказан выходной на:\n{ordered_days}",
                                     reply_markup=select_action_krs())
                    return

                if date:
                    available = handler_db.check_free_place(date, position, oke)
                    bot.send_message(157758328,
                                     f'812: date: {date}, position: {position}, oke: {oke}, available: {available}')
                    if int(available) == 0:
                        bot.send_message(message.chat.id,
                                         f'{date} не осталось свободных мест, либо на этот день нельзя заказать выходной день.\n',
                                         reply_markup=select_action_krs())
                        return

                    # TODO налепил на пробу на проверку даты не осталось свободной ^^^^^^^^^^^^^^^^^^^^^^^^^^^

                    else:
                        # oke = order_dict[message.chat.id]['oke']
                        oke = handler_db.get_oke(tab_number)
                        surname = order_dict[message.chat.id]['surname']
                        name = order_dict[message.chat.id]['name']
                        position = order_dict[message.chat.id]['position']
                        handler_db.update_order_for_other(tab_number, oke, surname, name, position, date)
                        ordered_days = handler_db.what_dates_order(tab_number)
                    bot.send_message(message.chat.id,
                                     f'Выходной успешно заказан. \n{name} {surname} будет отдыхать \n{ordered_days}',
                                     reply_markup=select_action_krs())
                    bot.send_message(157758328, f'НОКЭ Заказал выходной.')
                    return
        except Exception:
            ordered_days = handler_db.what_dates_order(tab_number)
            if not ordered_days:
                bot.send_message(message.chat.id, f"Вы хотите заказать или отменить ранее заказанный выходной?",
                                 reply_markup=select_action_krs())
                return
            if ordered_days:
                bot.send_message(message.chat.id, f"Уже заказаны даты:\n{ordered_days}",
                                 reply_markup=select_action_krs())

            count_ordered = len(ordered_days.split('\n')) - 1
            if count_ordered == 3:
                bot.send_message(message.chat.id, f"Можно заказывать не более трех дней.")
                return

        if message.text.lower() in "удалить выходной удалить\nвыходной":
            bot.send_message(message.chat.id, f"Табельный номер бортпроводника?")
            return

        if message.text.isdigit() and len(
                message.text) >= 4:  # TODO Доделать - срабатывает после кнопки удалить|nвыходной
            order_dict[message.chat.id] = {}
            order_dict[message.chat.id]['tab_number'] = message.text
            bot.send_message(message.chat.id,
                             f"Какого числа удалить выходной? \nНапишите в ответном сообщении удалить и число, например: \n\nудалить 25")
            return

        if "удалить" in message.text.lower() and len(message.text.split()) == 2:
            try:
                tab_number = order_dict[message.chat.id]['tab_number']
            except Exception as exc:
                bot.send_message(message.chat.id,
                                 f"Напомните, как Вас зовут? Напишите табельный фамилию имя, например: 123456 Иванов Иван")
                return
            date = check_true_date(message.text.split()[1])[0]
            ordered_days = handler_db.what_dates_order(tab_number)
            was_ordered = None

            if date in ordered_days:
                was_ordered = True
            dates = handler_db.delete_date(tab_number, date)
            if date not in dates:
                if was_ordered:
                    bot.send_message(message.chat.id, f"Выходной {date} успешно удален.",
                                     reply_markup=select_action_krs())
                else:
                    bot.send_message(message.chat.id, f"{date} не был заказан выходной день.")
            if dates:
                bot.send_message(message.chat.id, f"Заказанные даты:\n{dates}", reply_markup=select_action_krs())
            else:
                bot.send_message(message.chat.id, f"У этого бортпроводника нет заказанных выходных.",
                                 reply_markup=select_action_krs())
            return

        else:
            bot.send_message(message.chat.id, "Чем могу помочь?", reply_markup=select_action_krs(),
                             parse_mode='Markdown')
            return

    if message.text.lower() in "заказать выходной заказать\nвыходной":
        if check_limit():
            return
        else:
            bot.send_message(message.chat.id, f"Заказы принимаются на {get_future_date()[2]} месяц. ")  # оставить своё пожелание о предоставлении выходных дней
                             # "Обратите внимание, что установлена ежедневная квота на каждое ОКЭ:\n"
                             # "- 2 СБ;\n"
                             # "- 2 BS;\n"
                             # "- 3 БП.\n"
            bot.send_message(message.chat.id, f"Вы можете заказать не более двух дней подряд и не более трёх выходных в месяц всего.\n\n"
                                              f"За заказ более двух выходных в месяце - лишают премии за недоступность к планированию.\n\n"
                                              f"Заказывать выходной на день рождения и на следующий за ним день не нужно, т.к."
                                              f"вам поставят выходные в эти дни за вас в отделе планирования сами. \n\n"
                                              f"До дня рождения и после дня рождения должно быть не менее пяти рабочих дней, чтобы можно было заказать следующий выходной.\n\n"
                                              f"Если у вас планируется отпуск в том месяце, в котором вы заказываете выходной, то выходной вам не дадут.\n\n ")
            # bot.send_message(message.chat.id, f"За заказ более двух дней - лишают премии за недоступность к планированию.")

            ################ TODO принудительно всегда спрашивать позицию - убрать проверку на None

            if handler_db.get_position(handler_db.get_tab_number(message.chat.id)) is None:
                msg2 = bot.send_message(message.chat.id, ask_position, reply_markup=select_position(),
                                        parse_mode='Markdown')
                bot.register_next_step_handler(msg2, start_03)
                return
            if handler_db.get_oke(handler_db.get_tab_number(message.chat.id)) is None:
                msg58 = bot.send_message(message.chat.id, ask_oke, reply_markup=otdelenie(), parse_mode='Markdown')
                bot.register_next_step_handler(msg58, start_003)
                return
            else:
                msg41 = bot.send_message(message.chat.id, ask_date, parse_mode='Markdown')
                bot.register_next_step_handler(msg41, start_04)
                return

    if message.text.lower() in "отменить\nвыходной отменить выходной":
        tab_number = handler_db.get_tab_number(message.chat.id)
        ordered_days = handler_db.what_dates_order(tab_number)

        if ordered_days != '':
            bot.send_message(message.chat.id,
                             f'{name}, сейчас у Вас заказаны выходные на:\n{ordered_days}\n\n'
                             f'Чтобы отменить заказанный выходной, напишите слово удалить и число, например:\n\n'
                             f'удалить 25')  # if "удалить выходной " будет написано в общем коде и продублировано ниже
        else:
            bot.send_message(message.chat.id,
                             f'У Вас не было ранее заказанных выходных дней.', reply_markup=select_action())  # if "у
        return

    if message.text.lower() in "заказанные даты":
        tab_number = handler_db.get_tab_number(message.chat.id)
        counter_days = handler_db.get_counter_days(tab_number)
        ordered_days = handler_db.what_dates_order(tab_number)
        if counter_days != 0:
            bot.send_message(message.chat.id,
                             f'{name}, у Вас заказано на {get_future_date()[2].lower()} месяц {counter_days} дн.:\n{ordered_days}',
                             reply_markup=select_action())
            return
        else:
            bot.send_message(message.chat.id,
                             f'На этот месяц у Вас нет заказнанных выходных дней.',
                             reply_markup=select_action())
            return

    if "свободные\nдаты" in message.text.lower():
        free_dates()
        return

    if "нокэ заказ" in message.text.lower():
        try:
            tab_number = message.text.split()[2]
            oke = message.text.split()[3]
            surname = message.text.split()[4].capitalize()
            name = message.text.split()[5].capitalize()
            position = message.text.split()[6].upper()
            date = check_true_date(message.text.split()[7])[0]

            counter_days = handler_db.get_counter_days(tab_number)
            ordered_days = handler_db.what_dates_order(tab_number)
            three_days = handler_db.check_three_days_in_row(tab_number)
            two_days = handler_db.check_two_days_in_row(date, tab_number)

            if three_days:
                bot.send_message(message.chat.id,
                                 f'У этого бортпроводника превышен трехдневных лимит на заказ выходных.')
                bot.send_message(message.chat.id,
                                 f'уже заказано на {get_future_date()[2]} месяц {counter_days} дн.:\n{ordered_days}',
                                 reply_markup=select_action())
                bot.send_message(message.chat.id, f'Выходной на {date} не заказн.')
                return
            if two_days:
                bot.send_message(message.chat.id, f'Вы попытались заказть более двух дней подряд, либо заказываете ту дату, которая уже была заказана..')
                bot.send_message(message.chat.id,
                                 f'уже заказано на {get_future_date()[2]} месяц {counter_days} дн.:\n{ordered_days}',
                                 reply_markup=select_action())
                bot.send_message(message.chat.id, f'Еще один выходной на {date} не заказн.')
                return

            else:
                handler_db.update_order_for_other(tab_number, oke, surname, name, position, date)
                ordered_days = handler_db.what_dates_order(tab_number)
            bot.send_message(message.chat.id,
                             f'Для {surname} {name} выходной успешно заказан на: \n{ordered_days}',
                             reply_markup=select_action())
            bot.send_message(157758328, f'НОКЭ Заказал выходной.')
            return
        except Exception:

            bot.send_message(message.chat.id,
                             f'Выходной заказать не удалось: проверьте свободные даты и корректность введенных данных. Вводить нужно по шаблону: нокэ заказ 123456 4 Иванов Иван СБ 25',
                             reply_markup=select_action())
            try:
                bot.send_message(message.chat.id, f"уже заказанны даты:\n{ordered_days}", reply_markup=select_action())
                count_ordered = len(ordered_days.split('\n')) - 1
                if count_ordered == 3:
                    bot.send_message(message.chat.id, f"можно заказываать не более трех дней")
                    return

                free_dates = handler_db.check_free_dates(position, oke)
                ordered_before = handler_db.what_dates_order(tab_number)
                output_free_dates = None

                for i in free_dates.split('\n'):
                    for j in ordered_before.split('\n'):
                        if j == '':
                            continue
                        if j in i:
                            output_free_dates = free_dates = free_dates.replace(f'{i}\n', '')
                    if output_free_dates is None:
                        output_free_dates = free_dates
                if output_free_dates != '':
                    bot.send_message(message.chat.id,
                                     f'Свободные даты, доступные Вам для заказа: \n{output_free_dates}',
                                     reply_markup=select_action(), parse_mode='Markdown')
                    return
                else:
                    bot.send_message(message.chat.id,
                                     f'Вам доступен для заказа любой день.',
                                     reply_markup=select_action(), parse_mode='Markdown')
                    return
            except Exception:
                return

    if "нокэ удалить" in message.text.lower():
        tab_number = message.text.split()[2]
        date = check_true_date(message.text.split()[3])[0]
        ordered_days = handler_db.what_dates_order(tab_number)
        was_ordered = None

        if date in ordered_days:
            was_ordered = True
        dates = handler_db.delete_date(tab_number, date)
        if date not in dates:
            if was_ordered:
                bot.send_message(message.chat.id, f" выходной {date} успешно удален.", reply_markup=select_action())
            else:
                bot.send_message(message.chat.id, f"{date} не было заказано выходного")
        if dates:
            bot.send_message(message.chat.id, f"заказанные даты:\n{dates}", reply_markup=select_action())
        else:
            bot.send_message(message.chat.id, f"У него нет заказанных выходных.", reply_markup=select_action())
        return

    if "удалить" in message.text.lower():
        delete_day(message)
        return

    if message.text.split()[0].isdigit() and len(message.text.split()[0]) <= 2:
        if handler_db.get_oke(handler_db.get_tab_number(message.chat.id)) is None:
            msg58 = bot.send_message(message.chat.id, ask_oke, reply_markup=otdelenie(), parse_mode='Markdown')
            bot.register_next_step_handler(msg58, start_003)
            return
        if check_limit():
            return
        else:
            tab_number = handler_db.get_tab_number(message.chat.id)
            date = check_true_date(message.text)[0]

            # TODO временное ограничение
            # day = date.split('.')[0]
            # if 1 <= int(day) <= 8 and date.split('.')[1] == '01':
            #     bot.send_message(message.chat.id,
            #                      f"Для заказа выходных на {date} воспользуйтесь другим ботом @dob_vacations_bot.  Там можно заказать любое количество дней с 1 по 8 число, хоть один день, хоть все восемь.",
            #                      reply_markup=select_action())
            #     bot.send_message(157758328, f"1069: направили {tab_number} {surname} {name} в другого бота с датой {date}")
            #     return

            ordered_days = handler_db.what_dates_order(tab_number)
            two_days = handler_db.check_two_days_in_row(date, tab_number)
            counter_days = handler_db.get_counter_days(tab_number)
            if two_days:
                bot.send_message(message.chat.id, f'НАРУШЕНЫ УСЛОВИЯ! \n{name}, вероятно, Вы попытались заказать более двух дней подряд, либо этот день Вы уже заказали ранее.')
                bot.send_message(message.chat.id,
                                 f'Cейчас у Вас уже заказано на {get_future_date()[2]} месяц {counter_days} дн.:\n{ordered_days}',
                                 reply_markup=select_action())
                # bot.send_message(message.chat.id, f'Выходной на {date} не заказн.')
                return
            start_04(message)
            return


    else:
        bot.send_message(message.chat.id, "Нажмите на одну из кнопок, представленных ниже.",
                         reply_markup=select_action())

    bot.send_message(message.chat.id, ask_order_or_cancel, reply_markup=select_action())

    # TODO ВЫХОДНЫЕ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


bot.polling(none_stop=True)
