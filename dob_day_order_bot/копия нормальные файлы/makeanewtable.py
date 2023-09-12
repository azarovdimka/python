import os
from datetime import datetime, timedelta
import pytz
import time

file_path = "day_off_31_dict.py"


def get_future_date(day):  # day - сколько прибавляем дней
    """ Генерирует дату в человеческом виде, добавляет нолики ко дням недели и месяцм, если число до 10. Функция
    используется для последующего вызова в функции для генерации таблицы (словаря) с датами."""
    current_datetime = time.strftime('%d.%m.%Y %H:%M')
    dt_utc = datetime.strptime(current_datetime, '%d.%m.%Y %H:%M').replace(tzinfo=pytz.utc)
    dt_future = dt_utc.astimezone(pytz.utc) + timedelta(days=day)  # сколько прибавляем дней
    day = str(dt_future.day)
    if len(day) == 1:
        day = f'0{day}'
    month = str(dt_future.month)
    if len(month) == 1:
        month = f'0{month}'
    year = str(dt_future.year)[2:]
    return f'{day}.{month}.{year}'

dict_test = {}


def run():
    """Генерирует таблицу (словарь) от 1 до 30(31) на полтора месяца вперед для заказа выходных, но оснвании которой
    будет потом сфорирвоана база данных. сохраняет в корень \GitHub\\dob_day_order_bot\\day_off_31_dict.py перенести его потом в базу общего бота"""
    count = 0
    for day in range(1, 32): #TODO c 8 числа стоит
        date = get_future_date(47 + day) # 53 дня между 7 февраля и 1 апреля для создания словаря с 1 апреля
        for oke in range(1, 6):
            for position in ['СБ', 'СБ', 'BS', 'BS', 'БП', 'БП', 'БП']:
                count += 1
                dict_test[count] = {'date': date, 'tab_number': '', 'oke': str(oke), 'surname': '', 'name': '', 'position': position, 'comment': ''}
    return dict_test


table = run()
print(table)
# ПЛАН ВПЕРВЫЕ РАНЬШЕ НЕ БЫЛО

with open(file_path, 'w', encoding='utf-8') as modified:
    modified.write(f'day_off_dict = {table}')
