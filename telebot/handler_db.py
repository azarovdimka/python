"""Библиотека для обработки sql-запросов и работой с базой данных SQlite3 General.bd"""

import sqlite3
import pandas as pd
import day_off_31_dict

db_root = ""


def to_create_day_off_requests_db():
    """Создает базу данных для заказа выходных"""
    with sqlite3.connect(db_root + 'day_off_requests.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS day_off(
                user_id INT,
                tab_number INT PRIMARY KEY,
                oke TEXT,
                position TEXT,
                date TEXT,
                comment TEXT);
                ''')


# to_create_day_off_requests_db()


def from_day_dict_to_sql(dictionary, name_table):
    """Переносит данные из словаря в базу данных."""
    with sqlite3.connect(db_root + 'day_off_requests.db') as con:  # создаем подключение к базе
        df = pd.DataFrame.from_dict(dictionary).transpose()  # передаем в базу имеющийся словарь и развораиваем его
        df['id'] = df.index  # копируем индексы в отдельный столбец, они помещаются в конец таблицы
        df = df.reset_index(drop=True)  # удаляет со старыми индексами, но столбец с индексами остается
        df = df[['id', 'date', 'tab_number', 'oke', 'surname', 'name', 'position',
                 'comment']]  # двигаем колонку с индексами вперед
        df = df.rename_axis(None)  # удаляет  название столбца индекса
        # print(df.isna().sum())
        # print(df[df['status'].isna()])
        df.to_sql(name_table, con=con, if_exists='replace')


# from_day_dict_to_sql(day_off_31_dict.day_off_dict, 'day_off')


def check_requests_before(user_id):
    """РАБОТАЕТ!!!!!! Проверяет заказывал ли бортпроводник выходные ранее в этом месяце"""
    with sqlite3.connect(db_root + 'day_off_requests.db') as con:
        cur = con.cursor()
        request = f"SELECT count(1) FROM day_of WHERE user_id={user_id};"
        cur.execute(request)
        for i in cur.fetchone():
            if int(i) == 0:
                return False
            else:
                return True


def update_date(date, tab_number, surname, name, position, oke, comment):
    """Добавляет заказ на определенную дату"""  # TODO записывает заказ вместо 4 в 5 отряд (переписыват 4 на 5)
    with sqlite3.connect(db_root + 'day_off_requests.db') as con:
        cur = con.cursor()
        select = """SELECT id FROM day_off 
                    WHERE date = ? AND position = ? AND oke = ? AND surname = '' LIMIT 1"""
        data = (date, position, oke)
        cur.execute(select, data)
        index = cur.fetchone()[0]
        sql_update_query = "UPDATE day_off SET tab_number = ?, surname = ?, name = ?, comment = ? WHERE id = ? AND oke = ?"  # AND tab_number is NULL
        data_update = (tab_number, surname, name, comment, index, oke)
        cur.execute(sql_update_query, data_update)

        # print_all()

# update_date(tab_number='119221', date='28.02.22', position='СБ', surname='Azarov', name='Dima')


def what_dates_order(tab_number):
    """РАБОТАЕТ!!! выдает заказанные даты по табельному номеру"""
    with sqlite3.connect(db_root + 'day_off_requests.db') as con:
        cur = con.cursor()
        query = """SELECT date FROM day_off where tab_number = ?"""
        data = (tab_number,)
        cur.execute(query, data)
        unique = []
        for i in cur.fetchall():
            unique.append(i)
        unique = sorted(set(unique))
        outputinfo = ''
        for i in unique:
            for b in i:
                outputinfo += f'{b}\n'
        return outputinfo


def delete_date(tab_number, date):
    """Удаляет заказанный выходной из базы по message.chat.id"""
    with sqlite3.connect(db_root + 'day_off_requests.db') as con:
        cur = con.cursor()
        select = """UPDATE day_off SET surname = '', name = '', tab_number = '', comment = '' WHERE date = ? AND tab_number = ?"""
        data = (date, tab_number)
        cur.execute(select, data)

    ordered_dates = what_dates_order(tab_number)
    if ordered_dates is not None:
        return ordered_dates
    else:
        return "У вас нет заказанных выходных"


def check_ordered_before(date, tab_number):
    """проверяет наличие заказанной такой же даты ранее"""
    with sqlite3.connect(db_root + 'day_off_requests.db') as con:
        cur = con.cursor()
        query = """SELECT date FROM day_off where tab_number = ?"""
        data = (tab_number,)
        cur.execute(query, data)
        unique_from_db = []
        for i in cur.fetchall():
            unique_from_db.append(i)
        unique_from_db = set(unique_from_db)
        dates_int_list_from_db = []
        for tuple_date_db in unique_from_db:
            for d in tuple_date_db:
                d = d.split('.')[0]
                dates_int_list_from_db.append(int(d))
        day = date.split('.')[0]
        if int(day) in dates_int_list_from_db:
            return True
        else:
            return False


def check_two_days_in_row(date, tab_number):
    """проверяет наличие более двух дней подряд: к полученной дате прибавляет два раза и отнимает два раза чтобы
    проверить в две стороны"""
    date_minus_2 = int(date.split('.')[0]) - 2
    date_minus_1 = int(date.split('.')[0]) - 1
    date_ordered = int(date.split('.')[0])
    date_plus_1 = int(date.split('.')[0]) + 1
    date_plus_2 = int(date.split('.')[0]) + 2
    check_dates_list = [date_minus_2, date_minus_1, date_ordered, date_plus_1, date_plus_2]
    coincidence_counter = 0

    with sqlite3.connect(db_root + 'day_off_requests.db') as con:
        cur = con.cursor()
        query = """SELECT date FROM day_off where tab_number = ?"""
        data = (tab_number,)
        cur.execute(query, data)
        unique_from_db = []
        for i in cur.fetchall():
            unique_from_db.append(i)
        unique_from_db = set(unique_from_db)
        dates_int_list_from_db = []
        for tuple_date_db in unique_from_db:
            for date in tuple_date_db:
                date = date.split('.')[0]
                dates_int_list_from_db.append(int(date))

        for int_date_db in dates_int_list_from_db:
            for int_check_date in check_dates_list:
                if int_check_date == int_date_db:
                    coincidence_counter += 1
        if coincidence_counter >= 2:
            return True
        else:
            return False

        # return length


# print(check_two_days_in_row(date='05.02.2022', tab_number='119221'))

def check_three_days_in_row(tab_number):
    """проверяет наличие всего трех дней в сумме"""
    with sqlite3.connect(db_root + 'day_off_requests.db') as con:
        cur = con.cursor()
        query = """SELECT date FROM day_off where tab_number = ?"""
        data = (tab_number,)
        cur.execute(query, data)
        unique_from_db = []
        for i in cur.fetchall():
            unique_from_db.append(i)
        if len(unique_from_db) >= 3:
            return True
        else:
            return False


def check_free_place(date, position, oke):
    """проверяет свододные места на выбранную дату и должность: считает свободные места, возвращает число"""
    with sqlite3.connect(db_root + 'day_off_requests.db') as con:
        cur = con.cursor()
        query = """SELECT date FROM day_off WHERE position = ? AND date = ? AND tab_number = ? AND oke = ?"""
        data = (position, date, '', oke)
        cur.execute(query, data)
        if cur:
            return len(cur.fetchall())


# date='01.02.22'
# position='СБ'
# print(check_free_place(date, position))

def check_free_dates(position, oke):
    """проверяет свододные даты,  возвращает даты"""
    with sqlite3.connect(db_root + 'day_off_requests.db') as con:
        cur = con.cursor()  # TODO добавить проверку была ли заказана дата эта уже
        query = """SELECT date FROM day_off 
                   WHERE position = ? AND oke = ? AND tab_number = ?"""
        data = (position, oke, '')
        cur.execute(query, data)
        output_info = ''
        if cur:
            for i in cur.fetchall():
                for b in i:
                    if b not in output_info:
                        output_info += f'{b}\n'
            return output_info
        else:
            return "Свободных дат нет."

    # """РАБОТАЕТ!!! выдает заказанные даты по табельному номеру"""
    # with sqlite3.connect('day_off_requests.db') as con:
    #     cur = con.cursor()
    #     query = """SELECT date FROM day_off where tab_number = ?"""
    #     data = (tab_number,)
    #     cur.execute(query, data)
    #     unique = []
    #     for i in cur.fetchall():
    #         unique.append(i)
    #     unique = sorted(set(unique))
    #     outputinfo = ''
    #     for i in unique:
    #         for b in i:
    #             outputinfo += f'{b}\n'
    #     return outputinfo


# print(check_free_dates(position='СБ', oke='5'))


def get_counter_days(tab_number):
    """ПРОВЕРИТЬ!!!! Извлекает количество ранее заказанных выходных из базы и возвращает число"""
    with sqlite3.connect(db_root + 'day_off_requests.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM day_off WHERE tab_number = ?", (tab_number,))
        if cur:
            return len(cur.fetchall())
        else:
            return '0'


# print(get_counter_days('119221'))


def get_position(tab_number):
    """Извлекает должность бортпроводника из основной базы данных по табельному номеру"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        cur.execute(f"""SELECT position FROM users 
                        WHERE tab_number = ?""", (tab_number,))
        for position in cur.fetchone():
            return position


def print_all():
    """консольная служебная функция не для вызова из телеграма"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users")
        for i in cur.fetchall():
            print(i)


print_all()


def import_daysoff_to_excel():
    """импортирует таблицу заказанных выходных дней в эксель"""
    with sqlite3.connect(db_root + 'day_off_requests.db') as con:
        df = pd.read_sql("SELECT * FROM day_off", con)
        df = df[['id', 'date', 'tab_number', 'oke', 'surname', 'name', 'position',
                 'comment']]
        df.to_excel('ordered_days.xlsx', index=False)


def get_tab_number(user_id):
    """Извлекает табельный номер бортпроводника из основной базы данных по user_id - message.chat.id"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        cur.execute(f"""SELECT tab_number FROM users 
                        WHERE user_id = {user_id}""")
        for tab_number in cur.fetchone():
            return tab_number



def get_name_surname(user_id):
    """Извлекает имя фамилию  бортпроводника из основной базы данных по user_id"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        cur.execute(f"""SELECT name, surname FROM users 
                        WHERE user_id = {user_id}""")
        name = ''
        for i in cur.fetchone():
            name += f'{i} '
        return name


def to_create_general_db():
    """Создает базу данных и таблицы"""
    with sqlite3.connect(db_root + 'general.db') as con:
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
                position TEXT,
                date TEXT,
                comment TEXT);
            ''')


def add_new_column(table, name_column):
    """добавляет новый столбце в таблицу"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        data = f'ALTER TABLE {table} ADD {name_column} TEXT'
        cur.execute(data)


# add_new_column('users', 'oke')


def check_access(user_id):
    """РАБОТАЕТ!!!!!! Проверяет есть ли пользователь в базе для предоставления доступа
    Возвращает ноль или единицу"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        request = f"SELECT count(1) FROM users WHERE user_id={user_id};"
        cur.execute(request)
        for i in cur.fetchone():
            if int(i) == 0:
                return False
            else:
                return True


def update_oke(tab_number, oke):
    """Добавляет окэ по табельному номеру"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET oke = ? WHERE tab_number = ?"
        data_update = (oke, tab_number)
        cur.execute(sql_update_query, data_update)


def fetch_user_for_plan(user_id):
    """Используется внутри цикла проверки планов работ для внутренних переменных"""
    with sqlite3.connect(db_root + 'general.db') as con:
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
    with sqlite3.connect(db_root + 'general.db') as con:  # создаем подключение к базе
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
    with sqlite3.connect(db_root + 'general.db') as con:
        login = message[0]
        password = message[1]
        cur = con.cursor()

        sql_update_query = "UPDATE users SET tab_number = ?, password = ? WHERE user_id = ?"
        data = (login, password, user_id)
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.tab_number from users u where u.user_id = ?)", (user_id,))
        return result


def update_login_password_for_user(tab_number, password, user_id):
    """При помощи этой функции администратор может заменить пароль вместо пользователя удаленно."""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET tab_number = ?, password = ? WHERE user_id = ?"
        data = (tab_number, password, user_id)
        cur.execute(sql_update_query, data)
        return


def update_password_for_user(password, user_id):
    """При помощи этой функции администратор может заменить пароль вместо пользователя удаленно."""
    with sqlite3.connect(db_root + 'general.db') as con:
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
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET autoconfirm = ? WHERE user_id = ?"
        data = (confirm, user_id)
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.autoconfirm from users u where u.user_id = ?)", (user_id,))
        return result


def update_position(user_id, position):
    """РАБОТАЕТ!!!! Добавляет должность бортпроводника в таблицу users"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET position = ? WHERE user_id = ?"
        data = (position, user_id)  # f-строка тут не работает
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.position from users u where u.user_id = ?)", (user_id,))
        return result


def update_position_in_day_off(tab_number, position):
    """РАБОТАЕТ!!!! Добавляет должность бортпроводника в таблицу day_off"""
    with sqlite3.connect(db_root + 'day_off_requests.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE day_off SET position = ? WHERE tab_number = ?"
        data = (position, tab_number)  # f-строка тут не работает
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.position from day_off u where u.tab_number = ?)", (tab_number,))
        return result


def update_plan_notify(plan_notify, user_id):
    """РАБОТАЕТ!!!! Добавляет подтверждение плана работ в базу данных для самостоятельного добавления пользователем"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET plan_notify = ? WHERE user_id = ?"
        data = (plan_notify, user_id)
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.plan_notify from users u where u.user_id = ?)", (user_id,))
        return result


def update_messaging(messaging, user_id):
    """Обновляет True/False в поле messaging: меняет разрешение присылать сообщения и рассылку """
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET messaging = ? WHERE user_id = ?"
        data = (messaging, user_id)
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.messaging from users u where u.user_id = ?)", (user_id,))
        return result


def update_night_notify(night_notify, user_id):
    """РАБОТАЕТ!!!! Добавляет подтверждение плана работ в базу данных для самостоятельного добавления пользователем"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET night_notify = ? WHERE user_id = ?"
        data = (night_notify, user_id)
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.night_notify from users u where u.user_id = ?)", (user_id,))
        return result


def update_city(city, user_id):
    """Меняет город у пользователя в базе данных"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        sql_update_query = "UPDATE users SET city = ? WHERE user_id = ?"
        data = (city, user_id)
        cur.execute(sql_update_query, data)

        result = cur.execute("SELECT EXISTS(select u.city from users u where u.user_id = ?)", (user_id,))
        return result


def list_user_id():
    """РАБОТАЕТ!!!! Используется в цикле для извлечения списка user_id для дальнейшего переборка списка циклом по порядку для
    проверки планов работ в цикле."""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()  # обязательно должно быть с запятой # select exists возвращает true
        cur.execute("select * from users")
        list_id = []
        for row in cur:
            list_id.append(row[1])
        return list_id


def check_users_in_db_id(user_id):
    """ЕДИНСТВЕННАЯ РАБОТАЕТ!!!!!!!! Проверяет есть ли пользователь в базе по id"""
    with sqlite3.connect(db_root + 'general.db') as con:
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
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        cur.execute("DELETE from users where user_id = ?", (user_id,))
    # TODO работает, но провести проверку не удается, насколько успешно удалился, такак возвращает данные как будто объект есть в базе


def select_all_data_of_person(user_id):
    """РАБОТАЕТ!!! извлекает из бызы определенные параметры:
    user_id, surname, name, tab_number, password, messaging, check_permissions, autoconfirm"""
    with sqlite3.connect(db_root + 'general.db') as con:
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
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        cur.execute("""select * from users where user_id = ?""", (user_id,))
        if cur:
            for row in cur:
                return row[1]


def get_three_last():
    """РАБОТАЕТ!!!! Выдает три посление фамилии из базы"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()  # обязательно должно быть с запятой # select exists возвращает true
        cur.execute("select * from users")
        result = cur.fetchall()
        return result[-3:]


def add_new_user_to_db_users_from_day_order(user_id, surname, name, tab_number):
    """РАБОТАЕТ!!!! Добавляет нового пользователя в словарь"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (user_id, surname, name, tab_number) "
            "VALUES (?, ?, ?, ?)", (user_id, surname, name, tab_number,))


def add_new_user_to_db_users(user_id, surname, name, city, link, exp_date, tab_number, password, access, messaging,
                             check_permissions, night_notify, plan_notify, autoconfirm, time_depart, time_arrive):
    """РАБОТАЕТ!!!! Добавляет нового пользователя в словарь"""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (user_id, surname, name, city, link, exp_date, tab_number, password, access, messaging, check_permissions, night_notify, plan_notify, autoconfirm, time_depart, time_arrive) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                user_id, surname, name, city, link, exp_date, tab_number, password, access, messaging,
                check_permissions,
                night_notify, plan_notify, autoconfirm, time_depart, time_arrive,))


def count_users():
    """РАБОТАЕТ!!!! Считает размер таблицы Users (количество бортпроводников, которым предоставлен доступ)."""
    with sqlite3.connect(db_root + 'general.db') as con:
        cur = con.cursor()
        cur.execute("select count(*) from users")
        for i in cur.fetchone():
            return i


if "name" == __name__:
    pass

# add_new_column('users', 'position')

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

# ПОЛУЧИТЬ НАЗВАНИЯ СТОЛБЦОВ
# sql_update_query = "PRAGMA table_info(day_off);"


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
