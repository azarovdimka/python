import traceback

import \
    telebot as t  # чтобы работал telebot - удалить telebot, и установить Pytelegrambotapi, написанным оставить telebot
from telebot import types
from datetime import datetime, timedelta
import pytz
import settings
import time
import sys
from os import path


def get_future_date():
    days = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31, }
    future_month_dict_names = {1: 'ЯНВАРЬ', 2: "ФЕВРАЛЬ", 3: "МАРТ", 4: "АПРЕЛЬ", 5: "МАЙ", 6: "ИЮНЬ", 7: "ИЮЛЬ",
                               8: "АВГУСТ", 9: "СЕНТЯБРЬ", 10: "ОКТЯБРЬ", 11: "НОЯБРЬ", 12: "ДЕКАБРЬ", }
    current_datetime = time.strftime('%d.%m.%Y %H:%M')
    current_month = time.strftime('%m')

    dt_utc = datetime.strptime(current_datetime, '%d.%m.%Y %H:%M').replace(tzinfo=pytz.utc)
    dt_future = dt_utc.astimezone(pytz.utc) + timedelta(days=70)
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
    if message.text in "1 ОКЭ 1 первый отряд 1 отделение 1окэ1 первое отделение":
        oke = "1"
    if message.text in "2 ОКЭ 2 (ЕКБ) второй отряд 2 отделение 2окэ2 второе отделение":
        oke = "2"
    if message.text in "3 ОКЭ 3 третий отряд 3 отделение 3окэ3 третье отделение":
        oke = "3"
    if message.text in "4 ОКЭ 4 четвертый отряд 4 отделение 4окэ4 четвертое отделение":
        oke = "4"
    if message.text in "5 ОКЭ 5 пятый отряд 5 отделение 5окэ5 пятое отделение":
        oke = "5"
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

    current_time = f'{hour}:{minute}'

    if '25' <= day <= '31' or '01' <= day <= '08':  # current_time >= '00:00' and
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
permission_message = f'С 25.{from_month} по 8.{till_month} заказы принимаются на {future_month_big_name}.'  # "'На данный момент заказы на выходные не принимаются. \n\nС 00:00 25 мая будет открыт прием заявок на выходные дни в ИЮЛЕ. \n\nПо всем вопросам и проблемам с заказом выходных обращаться напрямую к разработчику @DeveloperAzarov.'
forbidden_message = f'Прием выходных на {future_month_big_name_forbidden} прекращен. Выходные на {future_month_big_name} ' \
                    f'будут приниматься с 25.{from_month} по 8.{till_month}.\n Если Вам требуется отменить ранее заказанный выходной - ' \
                    f'обратитесь к своему начльнику ОКЭ.'


def notification():
    if permission_period():
        print(permission_message)
    if not permission_period():
        print(forbidden_message)
        return


notification()