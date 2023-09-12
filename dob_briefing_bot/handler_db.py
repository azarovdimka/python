"""Библиотека для обработки sql-запросов и работой с базой данных SQlite3 General.bd"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import time


def to_create_general_db():
    """Создает общую пустую базу данных бортпроводников, таблица users"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users(
                user_id INT PRIMARY KEY,
                tab_number TEXT,
                surname TEXT,
                name TEXT,
                oke TEXT,
                position TEXT,
                aircraft TEXT,
                current_tab_bp TEXT,
                flight_number TEXT
                )  
            ''')# добавил эти три строчки последние три колонки проверить будет ли с ними работать
    # add_new_user_to_db_users('157758328', '119221', 'Азаров', 'Дмитрий', '4', 'СБ')


# to_create_general_db()


def create_flight_db():
    """Создает пустую базу данных выполняемых рейсов (проведенных брифингов)"""
    with sqlite3.connect('flight.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS flight(
                messagechatid INT,
                id TEXT PRIMARY KEY,
                date TEXT,
                time_briefing TEXT,
                flight_number TEXT,
                aircraft TEXT,
                tab_number_sb TEXT,
                fio_sb TEXT,
                tab_bp TEXT,
                fio_bp TEXT,
                question TEXT,
                answer TEXT
                )'''
                )


# create_flight_db()


def add_new_user_to_db_users(user_id, tab_number, surname, name, oke, position):
    """РАБОТАЕТ!!!! Добавляет нового пользователя в словарь. Функция для общего телеграм-бота"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (user_id, tab_number, surname, name, oke, position) "
            "VALUES (?, ?, ?, ?, ?, ?)", (user_id, tab_number, surname, name, oke, position,))


def select_from_general_db(messagechatid, item):
    """Извлекает любой параметр из основной базы данных из строки относительно одного старшего"""
    with sqlite3.connect("general.db") as con:
        cur = con.cursor()
        cur.execute(f"""SELECT {item}
                        FROM users 
                        WHERE messagechatid = {messagechatid}""")
        answer = cur.fetchone()
        return answer


def update_aircraft_in_general_db(user_id, aircraft):
    """Добавляет тип ВС в общую базу данных general"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        update_query = """UPDATE users 
                          SET aircraft = ? 
                          WHERE user_id = ?"""
        data = (aircraft, user_id)
        cur.execute(update_query, data)  #


def print_all():
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute("""SELECT * FROM users""")
        return cur.fetchall()


def del_user_from_general_db(user_id):
    """Удаляет бортпрводника из общей базы данных"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute("""DELETE FROM users
                       WHERE user_id = ?""", (user_id, ))


def get_user_from_general_db(user_id):
    """Извлекает данные пользователя из общей базы данных."""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute(f"""SELECT tab_number, surname, name, oke, position
                       FROM users
                       WHERE user_id={user_id}""")
        return cur.fetchone()[0]


def get_tab_number_from_general_db(user_id):
    """Извлекает данные пользователя из общей базы данных."""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute(f"""SELECT tab_number
                       FROM users
                       WHERE user_id={user_id}""")
        try:
            return cur.fetchone()[0]
        except Exception:
            return False


# get_tab_number_from_general_db(157758328)


def get_len_flight_db():
    """Считает количество записей в базе данных"""
    with sqlite3.connect('flight.db') as con:
        cur = con.cursor()
        cur.execute("""SELECT Count(*) 
                       FROM flight""")
        return cur.fetchone()[0]


def insert_new_flight(messagechatid, id, date, time_briefing, flight_number, aircraft, tab_number_sb, fio_sb, tab_bp,
                      fio_bp, question, answer):
    """Добавляет новый рейс"""
    with sqlite3.connect('flight.db') as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO flight "
            "(messagechatid, id, date, time_briefing, flight_number, aircraft, tab_number_sb, fio_sb, tab_bp, fio_bp, question, answer) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (messagechatid, id, date, time_briefing, flight_number, aircraft, tab_number_sb, fio_sb, tab_bp, fio_bp, question, answer,))


def update_type_of_aircraft(aircraft, date, time):
    with sqlite3.connect('flight.db') as con:
        cur = con.cursor()
        sql_update_query = """UPDATE flight
                              SET aircraft = ?
                              WHERE date = ? AND time_briefing = ?"""  # f-строка тут не работает
        data = (aircraft, date, time)
        cur.execute(sql_update_query, data)


def get_question():
    """Извлекает случайный вопрос из экселя"""


def update_flight_number(flight_number, date, time):
    with sqlite3.connect('flight.db') as con:
        cur = con.cursor()
        sql_update_query = """UPDATE flight
                              SET flight_number = ?
                              WHERE date = ? AND time_briefing = ?"""  # f-строка тут не работает
        data = (flight_number, date, time)
        cur.execute(sql_update_query, data)

 # перед запуском функции удалить старую базу бортпроводников из директории


def check_position(user_id):
    """Проверяет записана ли должность в общей базе"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        request = f"SELECT position FROM users WHERE user_id={user_id};"
        cur.execute(request)
        for position in cur.fetchone():
            if position == 0:
                return False
            else:
                return position


def check_oke(user_id):
    """Проверяет записано ли отделение в общей базе"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        request = f"SELECT oke FROM users WHERE user_id={user_id};"
        cur.execute(request)
        for oke in cur.fetchone():
            if int(oke) == 0:
                return False
            else:
                return oke


def check_access(user_id):
    """РАБОТАЕТ!!!!!! Проверяет есть ли пользователь в базе для предоставления доступа
    Возвращает ноль или единицу"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        request = f"SELECT count(1) FROM users WHERE user_id={user_id};"
        cur.execute(request)
        for i in cur.fetchone():
            if int(i) == 0:
                return False
            else:
                return True


def import_users_to_excel():
    """Создает в папке эксель файл с пользователями на основе обще базы данных бортпроводников general.db"""
    with sqlite3.connect('general.db') as con:
        df = pd.read_sql("SELECT * FROM users", con)
        df = df[['user_id', 'surname', 'name', 'tab_number', 'oke', 'position']]
        df.to_excel('general_db.xlsx', index=False)


def get_user_id_by_tab_number(tab_number):
    """Извлекает user_id (message.chat.id) по табельному номеру, если удалось извлечь, то возвращает True, в противном случае None"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute("""SELECT user_id
                       FROM users
                       WHERE tab_number = ?""", (tab_number,))
        try:
            for user_id in cur.fetchone():
                return user_id
        except Exception:
            return None


def get_name_surname(user_id):
    """Извлекает имя фамилию  бортпроводника из основной базы данных по user_id"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute(f"""SELECT name, surname 
                        FROM users 
                        WHERE user_id = {user_id}""")
        name = ''
        try:
            for i in cur.fetchone():
                name += f'{i} '
            return name
        except Exception:
            return False


def update_position(user_id, position):
    """РАБОТАЕТ!!!! Добавляет должность бортпроводника в таблицу users и возвращает позицию из базы как проверку"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        sql_update_query = """UPDATE users
                              SET position = ?
                              WHERE user_id = ?"""  # f-строка тут не работает
        data = (position, user_id)
        cur.execute(sql_update_query, data)

        cur.execute(f"""SELECT position 
                        FROM users 
                        WHERE user_id = {user_id}""")
        return cur.fetchone()[0]


def update_oke(user_id, oke):
    """РАБОТАЕТ!!!! Добавляет отделение бортпроводника в таблицу users и возвращает позицию из базы как проверку"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        sql_update_query = """UPDATE users
                              SET oke = ?
                              WHERE user_id = ?"""  # f-строка тут не работает
        data = (oke, user_id)
        cur.execute(sql_update_query, data)

        cur.execute(f"""SELECT oke 
                        FROM users 
                        WHERE user_id = {user_id}""")
        return cur.fetchone()[0]


def update_tab_other_bp(fio_sb,  tab_number_other_bp, flight_number):
    """НЕ РАБОТАЕТ"""
    with sqlite3.connect('flight.db') as con:
        cur = con.cursor()
        sql_update_query = """UPDATE flight
                              SET tab_number_other_bp = ?
                              WHERE fio_sb = ? AND flight_number = ?"""  # f-строка тут не работает
        data = (tab_number_other_bp, fio_sb, flight_number)
        cur.execute(sql_update_query, data)


def update_fio_other_bp(fio_sb,  fio_other_bp, flight_number):
    """НЕ РАБОТАЕТ"""
    with sqlite3.connect('flight.db') as con:
        cur = con.cursor()
        sql_update_query = """UPDATE flight
                              SET fio_other_bp = ? 
                              WHERE fio_sb = ? AND flight_number = ?"""  # f-строка тут не работает
        data = (fio_other_bp, fio_sb, flight_number)
        cur.execute(sql_update_query, data)


def get_aircraft(user_id):
    """Извлекает type of aircraft из основной базы данных по user_id"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute(f"""SELECT aircraft 
                        FROM users 
                        WHERE user_id = {user_id}""")
        # print(f'cur.fetchone() {cur.fetchone()}, \n cur.fetchone()[0] {cur.fetchone()[0]}')
        return cur.fetchone()[0]


# get_aircraft('119221', '25.06.2023')


def get_fio_crew(tab_number):
    """Извлекает список бортпроводников для данного рейса. tab_number must be integer. return list oke, tab_number, fio, position"""
    df = pd.read_excel('crew.xlsx', engine='openpyxl')  # [отряд, табельный, фио, должность]
    # crew_df = df[['Табельный №', 'Фамилия Имя Отчество']]
    person = df[df['Табельный №'] == int(tab_number)]
    person_list = person.iloc[0].tolist()
    oke = person_list[0]
    tab_number = person_list[1]
    fio = person_list[2]
    position = person_list[3]
    return oke, str(tab_number), fio, position


def get_name_from_excel(tab_number):
    """Извлекает имя по tab_number. return name"""
    df = pd.read_excel('crew.xlsx', engine='openpyxl')  # [отряд, табельный, фио, должность]
    person = df[df['Табельный №'] == int(tab_number)]
    person_list = person.iloc[0].tolist()
    name = person_list[2].split(' ')[1]
    return name


def upload_flight_journal_to_excel(): # ИЗМЕНЕНИЯ ЗДЕСЬ 152 и 153 строки.. 154 на русском
    """экспортирует sql_db таблицу рейсов в эксель"""
    with sqlite3.connect('flight.db') as con:
        df = pd.read_sql("SELECT * FROM flight", con)
        # df['surname'].replace('', np.nan, inplace=True)
        # df.dropna(subset=['surname'], inplace=True)
        df.columns = ['message.chat.id', 'id', 'Дата бриф.', 'Время бриф.', 'Рейс', 'Тип ВС', 'Таб.№ СБ', 'ФИО СБ', "Таб.№ БП", "ФИО БП", "Вопрос", "Ответ"]
        # df = df[['Дата', 'Локация', 'Табельный', 'Фамилия', 'Имя', 'Должность']]
        df.to_excel(f'briefing_journal.xlsx', index=False)

