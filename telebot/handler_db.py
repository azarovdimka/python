"""Библиотека для обработки sql-запросов и работой с базой данных SQlite3 General.bd"""

import sqlite3
import pandas as pd
import dict_users


def to_create_general_db():
    """Создает базу данных и таблицы"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users(
                user_id INT PRIMARY KEY,
                surname TEXT,
                name TEXT,
                city TEXT,
                link TEXT,
                exp_date TEXT,
                tab_number INT,
                password TEXT,
                access INT,
                messaging INT,
                check_permissions INT,
                night_notify INT,
                plan_notify INT,
                autoconfirm INT,
                time_depart INT,
                time_arrive INT);
            ''')

        cur.execute('''CREATE TABLE IF NOT EXISTS day_off(
                user_id INT,
                tab_number INT PRIMARY KEY,
                date TEXT,
                total_days TEXT);
            ''')

        cur.execute('''CREATE TABLE IF NOT EXISTS user_requests(
                user_id INT PRIMARY KEY,
                date TEXT,
                request TEXT);
            ''')


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


def fetch_user_for_plan(user_id):
    """Используется внутри цикла проверки планов работ для внутренних переменных"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute(
            "select user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, autoconfirm, time_depart from users where user_id = ?",
            (user_id,))
        for row in cur:
            user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, autoconfirm, time_depart = \
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]
            return user_id, surname, name, tab_number, password, messaging, check_permissions, night_notify, plan_notify, autoconfirm, time_depart


def from_dict_to_sql(dictionary, name_table):
    """Переносит данные из словаря в базу данных."""
    with sqlite3.connect('general.db') as con:  # создаем подключение к базе
        df = pd.DataFrame.from_dict(dictionary).transpose()  # передаем в базу имеющийся словарь и развораиваем его
        df['user_id'] = df.index  # копируем индексы в отдельный столбец, они помещаются в конец таблицы
        df = df.reset_index(
            drop=True)  # копирует индексы в новый столбец и удаляет со старыми индексами, но столбец с индексами остается
        df = df[['user_id', 'surname', 'name', 'city', 'link', 'exp_date', 'tab_number', 'password',
                 'access', 'messaging', 'check_permissions', 'night_notify', 'plan_notify', 'autoconfirm',
                 'time_depart', 'time_arrive']]  # двигаем колонку с индексами вперед
        df = df.rename_axis(None)  # удаляет  название столбца индекса
        # print(df.isna().sum())
        # print(df[df['status'].isna()])
        df.to_sql(name_table, con=con,
                  if_exists='replace')  # TODO добавить index=False чтобы не залились индексы 0,1,2,3 в каждой строке и проверить как меняются функции и индексы


def insert_login_password(message, user_id):
    """РАБОТАЕТ!!!! Добавляет логин и пароль в базу данных для самостоятельного добавления пользователем"""
    with sqlite3.connect('general.db') as con:
        login = message[0]
        password = message[1]
        cur = con.cursor()

        sql_update_query = "UPDATE users SET tab_number = ?, password = ? WHERE user_id = ?"
        data = (login, password, user_id)
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.tab_number from users u where u.user_id = ?)", (user_id,))
        return result


def update_password_for_user(password, user_id):
    """При помощи этой функции администратор может заменить пароль вместо пользователя удаленно."""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET password = ? WHERE user_id = ?"
        data = (password, user_id)
        cur.execute(sql_update_query, data)
        return


def insert_utc_msk(message, user_id):
    """РАБОТАЕТ!!!! Добавляет часовые пояса utc msk в базу данных для самостоятельного добавления пользователем"""
    with sqlite3.connect('general.db') as con:
        depart = message.split()[0]
        arrive = message.split()[1]
        cur = con.cursor()

        sql_update_query = "UPDATE users SET time_depart = ?, time_arrive = ? WHERE user_id = ?"
        data = (depart, arrive, user_id)
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.time_depart from users u where u.user_id = ?)", (user_id,))
        return result


def insert_confirm(confirm, user_id):
    """РАБОТАЕТ!!!! Добавляет подтверждение плана работ в базу данных для самостоятельного добавления пользователем"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET autoconfirm = ? WHERE user_id = ?"
        data = (confirm, user_id)
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.autoconfirm from users u where u.user_id = ?)", (user_id,))
        return result


def update_plan_notify(plan_notify, user_id):
    """РАБОТАЕТ!!!! Добавляет подтверждение плана работ в базу данных для самостоятельного добавления пользователем"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET plan_notify = ? WHERE user_id = ?"
        data = (plan_notify, user_id)
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.plan_notify from users u where u.user_id = ?)", (user_id,))
        return result


def update_messaging(messaging, user_id):
    """Обновляет True/False в поле messaging: меняет разрешение присылать сообщения и рассылку """
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET messaging = ? WHERE user_id = ?"
        data = (messaging, user_id)
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.messaging from users u where u.user_id = ?)", (user_id,))
        return result


def update_night_notify(night_notify, user_id):
    """РАБОТАЕТ!!!! Добавляет подтверждение плана работ в базу данных для самостоятельного добавления пользователем"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET night_notify = ? WHERE user_id = ?"
        data = (night_notify, user_id)
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.night_notify from users u where u.user_id = ?)", (user_id,))
        return result


def update_city(city, user_id):
    """Меняет город у пользователя в базе данных"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET city = ? WHERE user_id = ?"
        data = (city, user_id)
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.city from users u where u.user_id = ?)", (user_id,))
        return result


def list_user_id():
    """РАБОТАЕТ!!!! Используется в цикле для извлечения списка user_id для дальнейшего переборка списка циклом по порядку для
    проверки планов работ в цикле."""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()  # обязательно должно быть с запятой # select exists возвращает true
        cur.execute("select * from users")
        list_id = []
        for row in cur:
            list_id.append(row[1])
        return list_id


def check_users_in_db_id(user_id):
    """ЕДИНСТВЕННАЯ РАБОТАЕТ!!!!!!!! Проверяет есть ли пользователь в базе по id"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute("select users.* from users where user_id = ?", (user_id,))
        try:
            if cur:
                for row in cur:
                    return f"человек \n user_id: {row[1]} \nsurname: {row[2]} \nname:{row[3]} \ncity:{row[4]} \nlink:{row[5]} \nexp_date:{row[6]} \nтаб№ {row[7]} \npassword {row[8]} \naccess {row[9]} \nmessaging {row[10]} \ncheck_permission {row[11]} \nnight_notyfy {row[12]} \nplan_notify {row[13]} \nautoconfirm {row[14]} \ntime_depart {row[15]} \ntime_arrive {row[16]}\n     есть в базе"
        except Exception as exc:
            return f"Пользователь отсутсвует в базе данных!!: {exc}"


def delete_user_from_db(user_id):
    """РАБОТАЕТ!!!! Удаляет пользователя из базы данных"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute("DELETE from users where user_id = ?", (user_id,))
    # TODO работает, но провести проверку не удается, насколько успешно удалился, такак возвращает данные как будто объект есть в базе


def select_all_data_of_person(user_id):
    """РАБОТАЕТ!!! извлекает из бызы определенные параметры:
    user_id, surname, name, tab_number, password, messaging, check_permissions, autoconfirm"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        request = f"select * from users where user_id = {user_id}"
        cur.execute(request)
        result_set = cur.fetchone()
        string = ''
        try:
            for i in result_set:
                string += f'{i} '
        except Exception as exc:
            return f"Пользователя нет в базе!\n\n{exc}"
        return string


def check_user_id_in_db(user_id):
    """Используется после добавления пользвоателя в базу для проверки: выдаёт user_id, если пользователь в базе есть"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute("""select * from users where user_id = ?""", (user_id,))
        if cur:
            for row in cur:
                return row[1]


def get_three_last():
    """РАБОТАЕТ!!!! Выдает три посление фамилии из базы"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()  # обязательно должно быть с запятой # select exists возвращает true
        cur.execute("select * from users")
        result = cur.fetchall()
        return result[-3:]


def add_new_user_to_db_users(user_id, surname, name, city, link, exp_date, tab_number, password, access, messaging,
                             check_permissions, night_notify, plan_notify, autoconfirm, time_depart, time_arrive):
    """РАБОТАЕТ!!!! Добавляет нового пользователя в словарь"""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (user_id, surname, name, city, link, exp_date, tab_number, password, access, messaging, check_permissions, night_notify, plan_notify, autoconfirm, time_depart, time_arrive) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            user_id, surname, name, city, link, exp_date, tab_number, password, access, messaging, check_permissions,
            night_notify, plan_notify, autoconfirm, time_depart, time_arrive,))


def count_users():
    """РАБОТАЕТ!!!! Считает размер таблицы Users (количество бортпроводников, которым предоставлен доступ)."""
    with sqlite3.connect('general.db') as con:
        cur = con.cursor()
        cur.execute("select count(*) from users")
        for i in cur.fetchone():
            return i


if "name" == __name__:
    pass

# to_create_general_db()
# from_dict_to_sql(dict_users.users, 'users')

# df = pd.DataFrame.from_dict(dict_users.users).transpose() # передаем в базу имеющийся словарь и развораиваем его
# df['user_id'] = df.index  # копируем индексы в отдельный столбец, они помещаются в конец таблицы
# df = df.reset_index(drop=True)  # копирует индексы в новый столбец и удаляет со старыми индексами, но столбец с индексами остается
# df = df[['user_id', 'surname', 'name', 'city', 'link', 'exp_date', 'tab_number', 'password',
#          'access', 'night_notify', 'plan_notify', 'autoconfirm', 'messaging',
#          'check_permissions', 'time_depart', 'time_arrive']]  # двигаем колонку с индексами вперед
# df = df.rename_axis(None) # удаляет  название столбца индекса
# print(df.loc[171])
# print(df[df.surname == "Иванова"])
# print(df)

# string = select(305665787)
# print(string)

# чтобы использовать f-строку, нужно добавлять круглы скобки f"text ({a}) text"

# СПРАВКА
# https://pythonru.com/osnovy/sqlite-v-python

# cur.execute("SELECT * FROM users;")
# TODO извлечь полученный один результат
#  one_result = cur.fetchone()
# print(one_result)
# [(1, 'Alex', 'Smith', 'male')]

# TODO вывести три результата из таблицы
#  three_results = cur.fetchmany(3)
# print(three_results)
# Он вернет следующее:
# [(1, 'Alex', 'Smith', 'male'), (2, 'Lois', 'Lane', 'Female'), (3, 'Peter',


# TODO Вывести все результаты из таблицы
#  all_results = cur.fetchall()
# print(all_results)
# Выдаст все результаты из таблицы

# TODO итератор cur.__next__
# все методы fetchone и fetchall по сути наделены итератором
# cur.execute("SELECT * FROM sections")
# cur.fetchone()
# (1, 'Information')
# cur.fetchone()
# (2, 'Digital Systems')
# cur.__next__()
# (3, 'Boolean Algebra')

# >>> cur.execute("SELECT * FROM sections")
# <sqlite3.Cursor object at 0x7fd0f16fe110>
# >>> cur.fetchmany(2)
# [(1, 'Information'), (2, 'Digital Systems')]
# >>> cur.fetchmany(2)
# [(3, 'Boolean Algebra'), (4, 'Algorithm')]
# >>> cur.fetchmany(2)

# TODO Удаление пользователя
#  cur.execute("DELETE FROM users WHERE lname='Parker';")
# conn.commit()
# Если затем сделать следующей запрос:
# cur.execute("select * from users where lname='Parker'")
# print(cur.fetchall())
# Будет выведен пустой список, подтверждающий, что запись удалена.

# TODO Объединение таблиц
# cur.execute("""SELECT *, users.fname, users.lname FROM orders
#     LEFT JOIN users ON users.userid=orders.userid;""")
# print(cur.fetchall())

# TODO Вставить несколько значений
# >>> themes = [
# ... (1, 'Information'),
# ... (2, 'Digital Systems'),
# ... (3, 'Boolean Algebra')]
#
# >>> cur.executemany('''
# ... INSERT INTO sections
# ... VALUES (?, ?)''', themes)
