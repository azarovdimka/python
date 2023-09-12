from datetime import datetime, timedelta
import pytz
import time


start_date = '15'
finish_date = '03'
plus_period_days = 56
plus_period_days_after_finish = 36


def get_future_date():
    days = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31, }
    future_month_dict_names = {1: 'ЯНВАРЬ', 2: "ФЕВРАЛЬ", 3: "МАРТ", 4: "АПРЕЛЬ", 5: "МАЙ", 6: "ИЮНЬ", 7: "ИЮЛЬ",
                               8: "АВГУСТ", 9: "СЕНТЯБРЬ", 10: "ОКТЯБРЬ", 11: "НОЯБРЬ", 12: "ДЕКАБРЬ", }
    current_datetime = time.strftime('%d.%m.%Y %H:%M')
    current_month = time.strftime('%m')

    dt_utc = datetime.strptime(current_datetime, '%d.%m.%Y %H:%M').replace(tzinfo=pytz.utc)
    dt_future = dt_utc.astimezone(pytz.utc) + timedelta(days=plus_period_days)
    future_month_int = int(dt_future.month)

    dt_future_after_finish = dt_utc.astimezone(pytz.utc) + timedelta(days=plus_period_days_after_finish)
    future_month_int_after_finish = int(dt_future_after_finish.month)

    future_year = str(dt_future.year)[2:]
    future_month_big_name = future_month_dict_names[future_month_int]
    future_month_big_name_after_finish = future_month_dict_names[future_month_int_after_finish + 1]
    if current_month == '12':
        future_month_big_name_forbidden = future_month_dict_names[1]
    else:
        future_month_big_name_forbidden_after_finish = future_month_dict_names[int(current_month)]
        future_month_big_name_forbidden = future_month_dict_names[int(current_month) + 1]
    return future_month_int, days[future_month_int], future_month_big_name, future_year, future_month_big_name_forbidden, \
           future_month_big_name_forbidden_after_finish, future_month_big_name_after_finish, future_month_int_after_finish


def convert_from_month(future_date_int):
    """Функия для подстановки верной строки числового выражения месяца в образец текста для заказа выходных.
    Проверяет нужно ли добавить ноль перед числом месяца, если нужно - добавляет, возвращает с нолем"""

    if future_date_int == 1:
        month_int = 11
    elif future_date_int == 2:
        month_int = 12
    else:
        month_int = future_date_int-2
    if month_int < 10:
        month_int = '0' + str(month_int)
    return month_int


def convert_till_month(future_date_int):
    """Функия для подстановки верной строки числового выражения месяца в образец текста для заказа выходных.
    Проверяет нужно ли добавить ноль перед числом месяца, если нужно - добавляет, возвращает с нолем"""
    if future_date_int == 1:
        month_int = 12
    else:
        month_int = future_date_int - 1

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


    # day = '31'

    current_time = f'{hour}:{minute}'
       # 15                                        # 03
    if start_date <= day <= '31' or '01' <= day <= finish_date:  # current_time >= '00:00' and
        return True
        # print(f'Заказ выходных принимаются.')
    else:
        return False
        # print(f'Заказ выходных прекращен')

future_month_int = get_future_date()[0]
future_month_int_after_finish = get_future_date()[7]
future_month_big_name = get_future_date()[2]
future_month_big_name_after_finish = get_future_date()[6]
future_month_big_name_forbidden = get_future_date()[4]
future_month_big_name_forbidden_after_finish = get_future_date()[5]
from_month = convert_from_month(future_month_int)
till_month = convert_till_month(future_month_int)
from_month_aft_fin = convert_from_month(future_month_int_after_finish + 1)
till_month_aft_fin = convert_till_month(future_month_int_after_finish + 1)
permission_message = f'С 15.{from_month} по 03.{till_month} заказы принимаются на {future_month_big_name}.'  # "'На данный момент заказы на выходные не принимаются. \n\nС 00:00 25 мая будет открыт прием заявок на выходные дни в ИЮЛЕ. \n\nПо всем вопросам и проблемам с заказом выходных обращаться напрямую к разработчику @DeveloperAzarov.'
forbidden_message = f' Прием выходных на {future_month_big_name_forbidden} прекращен. Выходные на {future_month_big_name_after_finish} ' \
                    f'будут приниматься с 15.{from_month_aft_fin} по 03.{till_month_aft_fin}. \n Если Вам требуется отменить ранее заказанный выходной - ' \
                    f'обратитесь к своему начльнику ОКЭ.'


def notification():
    if permission_period():
        print(permission_message)
    if not permission_period():
        print(forbidden_message)
        return



notification()