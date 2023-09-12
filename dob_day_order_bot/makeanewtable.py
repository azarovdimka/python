import os
from datetime import datetime, timedelta
import pytz
import time
import sqlite3
import pandas as pd
import pathlib
import os
import day_off_dict

file_path = "day_off_dict.py"


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
    for day in range(0, 31): #TODO Сделано по декабрь
        date = get_future_date(53 + day) # 53 дня между 7 февраля и 1 апреля для создания словаря с 1 апреля
        for city in ["Шереметьево", "Пулково", "Красноярск"]:
            if city == "Шереметьево": # 2 ИПБ, 7 СБ, 7 BS, 12БП
                for position in ["ИПБ", "ИПБ",
                                 'СБ', 'СБ', 'СБ', 'СБ', 'СБ', 'СБ', 'СБ',
                                 'BS', 'BS', 'BS', 'BS', 'BS', 'BS', 'BS',
                                 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП']:
                    count += 1
                    dict_test[count] = {'date': date, 'tab_number': '', 'oke': str(city), 'surname': '', 'name': '', 'position': position, 'comment': ''}
            if city == "Пулково": # 2 ИПБ, 7 СБ, 7 BS, 12БП
                for position in ["ИПБ", "ИПБ", 
                                 'СБ', 'СБ', 'СБ', 'СБ', 'СБ', 'СБ', 'СБ',
                                 'BS', 'BS', 'BS', 'BS', 'BS', 'BS', 'BS',
                                 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП']:
                    count += 1
                    dict_test[count] = {'date': date, 'tab_number': '', 'oke': str(city), 'surname': '', 'name': '', 'position': position, 'comment': ''}
            if city == "Красноярск": # 2 ИПБ, 7 СБ, 7 BS, 12БП
                for position in ["ИПБ", "ИПБ",
                                 'СБ', 'СБ', 'СБ', 'СБ', 'СБ', 'СБ', 'СБ',
                                 'BS', 'BS', 'BS', 'BS', 'BS', 'BS', 'BS',
                                 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП', 'БП']:
                    count += 1
                    dict_test[count] = {'date': date, 'tab_number': '', 'oke': str(city), 'surname': '', 'name': '', 'position': position, 'comment': ''}

    return dict_test


table = run()
print(table)


with open(file_path, 'w', encoding='utf-8') as modified:
    modified.write(f'day_off_dict = {table}')
    print(f'словарь записан в файл {pathlib.Path(__file__).parent.resolve()}\{file_path}')


os.remove('day_off_requests.db')
print(f'удалена старая база данных day_off_requests.db')

def to_create_day_off_requests_db():
    """Создает базу данных day_off_requests.db для заказа выходных"""
    with sqlite3.connect('day_off_requests.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS day_off(
                id INT,
                date TEXT, 
                tab_number INT PRIMARY KEY,
                oke TEXT,
                surname TEXT,
                name TEXT,
                position TEXT,
                comment TEXT);
                ''')
        print("Создана пустая база данных для сбора выходных 'day_off_requests.db' ")

to_create_day_off_requests_db()


def from_day_dict_to_sql(dictionary, name_table):
    """Переносит данные из словаря в базу данных."""
    with sqlite3.connect('day_off_requests.db') as con:  # создаем подключение к базе
        df = pd.DataFrame.from_dict(dictionary).transpose()  # передаем в базу имеющийся словарь и развораиваем его
        df['id'] = df.index  # копируем индексы в отдельный столбец, они помещаются в конец таблицы
        df = df.reset_index(drop=True)  # удаляет со старыми индексами, но столбец с индексами остается
        df = df[['id', 'date', 'tab_number', 'oke', 'surname', 'name', 'position', 'comment']]  # двигаем колонку с индексами вперед
        df = df.rename_axis(None)  # удаляет  название столбца индекса
        df.to_sql(name_table, con=con, if_exists='replace')
        print("Перенесены данные из словаря заготовки таблицы в базу данных. База данных в telebot\day_off_requests.db \n"
              "файлы нужно скопировать в папку общего телеграм-бота на сервере в папке bot")


from_day_dict_to_sql(day_off_dict.day_off_dict, 'day_off')  # TODO обратить внимание на число
# новая таблица создана по адресу telebot\day_off_requests.db
# Осталось заменить базы данных на сервере пустыми базами в папку общего телеграм-бота
# НИЖЕ НИЧЕГО НЕТ