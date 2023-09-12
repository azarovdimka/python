import sqlite3
import pandas as pd


def to_create_users_db():
    """Создает базу данных users.db для хранения списка пользователей."""
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users(
                id INT,
                tab_number TEXT PRIMARY KEY,
                surname TEXT,
                name TEXT);
                ''')
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        user_id = "157758328"
        surname = "Азаров"
        name = "Дмитрий"
        tab_number = "119221"
        cur.execute(
            "INSERT OR IGNORE INTO users (id, surname, name, tab_number) "
            "VALUES (?, ?, ?, ?)", (user_id, surname, name, tab_number,))
        return "Создана пустая база данных пользователей. Азаров добавлен в базу"


def to_create_vacations_db():
    """Создает базу данных vacations.db для заказа каникул на январь"""
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS vacations(
                        id INT,
                        tab_number TEXT PRIMARY KEY,
                        surname TEXT,
                        name TEXT,
                        from_date TEXT,
                        till TEXT,
                        duration TEXT);
                        ''')

        cur.execute('''CREATE TABLE IF NOT EXISTS temp(
                id INT,
                tab_number TEXT PRIMARY KEY,
                from_ask TEXT,
                from_date TEXT,
                till TEXT,
                duration TEXT);
                ''')

        return "Создана пустая база данных vacations.db для сбора каникул"


def add_from_ask_to_temp(tab_number, from_ask):
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        try:
            cur.execute("INSERT OR IGNORE INTO temp (tab_number, from_ask) "  # OR IGNORE 
                        "VALUES (?, ?)", (tab_number, from_ask,))
        except Exception:
            cur.execute(f"""UPDATE temp SET from_ask = {from_ask}
                                    WHERE tab_number = {tab_number}""")


def add_from_date_to_temp(tab_number, from_date):
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE temp SET from_date = {from_date}
                        WHERE tab_number = {tab_number}""")

        cur.execute(f"""UPDATE vacations SET from_date = {from_date}
                        WHERE tab_number = {tab_number}""")


def add_till(tab_number, till):
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE vacations SET till = {till}
                        WHERE tab_number = {tab_number}""")


def add_duration_to_temp(tab_number, duration):
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE temp SET duration = {duration}
                        WHERE tab_number = {tab_number}""")

        cur.execute(f"""UPDATE vacations SET duration = {duration}
                        WHERE tab_number = {tab_number}""")


def get_duration(tab_number):
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        cur.execute(f"""SELECT duration 
                        FROM temp
                        WHERE tab_number = {tab_number}""")
        for duration in cur.fetchone():
            return duration[0]


def get_from_date(tab_number):
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        cur.execute(f"SELECT from_date FROM temp WHERE tab_number={tab_number}")
        return cur.fetchone()[0]


def get_till(tab_number):
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        cur.execute(f"SELECT till FROM temp WHERE tab_number={tab_number}")
        return cur.fetchone()[0]


# def get_from_ask(tab_number):
#     with sqlite3.connect('vacations.db') as con:
#         cur = con.cursor()
#         try:
#             cur.execute(f"SELECT from_ask FROM temp WHERE tab_number = {tab_number}")
#         except Exception:
#             return False
#         return cur.fetchone()[0]


def get_from_ask(tab_number):
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        try:
            cur.execute(f"SELECT from_ask FROM temp WHERE tab_number = {tab_number}")
            return cur.fetchone()[0]
        except Exception:
            add_from_ask_to_temp(tab_number, False)
            get_from_ask(tab_number)


def get_string(tab_number):
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        cur.execute(f"""SELECT * 
                        FROM temp
                        WHERE tab_number = {tab_number}""")
        return cur.fetchall()


def check_access(user_id):
    """РАБОТАЕТ!!!!!! Проверяет есть ли пользователь в базе. Возвращает ноль или единицу"""
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        request = f"SELECT count(1) FROM users WHERE id={user_id};"
        cur.execute(request)
        for i in cur.fetchone():
            if int(i) == 0:
                return False
            else:
                return True


def add_new_user_to_users_db(user_id, surname, name, tab_number):
    """РАБОТАЕТ!!!! Добавляет нового пользователя в словарь. Функция для бота для заказа выходных."""
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (id, surname, name, tab_number) "
            "VALUES (?, ?, ?, ?)", (user_id, surname, name, tab_number,))


def add_new_user_to_temp_db(user_id, tab_number):
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO temp (id, tab_number, from_ask, from_date, till, duration) "
            "VALUES (?, ?, ?, ?, ?, ?)", (user_id, tab_number, False, False, False, False))


def get_tab_number_name_surname(user_id):
    """Извлекает табельный, фамилию, имя бортпроводника из основной базы данных по user_id"""
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        cur.execute(f"""SELECT tab_number, surname, name FROM users 
                        WHERE id = {user_id}""")
        user = ''
        try:
            for i in cur.fetchone():
                user += f'{i} '
            return user
        except Exception:
            return False


def get_vacations(tab_number):
    """Извлекает каникулы из базы данных по tab_number"""
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        vacations = 'с '
        cur.execute(f"""SELECT from_date FROM vacations 
                        WHERE tab_number = {tab_number}""")
        try:
            for i in cur.fetchone():
                vacations += f'{i} по '
        except Exception:
            return False

        cur.execute(f"""SELECT till FROM vacations 
                                WHERE tab_number = {tab_number}""")
        try:
            for i in cur.fetchone():
                vacations += f'{i}'
        except Exception:
            return False
        return vacations


def delete_from_temp(tab_number):
    """Удаляет заказанный выходной из базы по tab_number"""
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        select = f"""DELETE FROM temp WHERE tab_number = ?"""
        data = (tab_number,)
        cur.execute(select, data)

    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        cur.execute(f"""SELECT * FROM temp 
                        WHERE tab_number = {tab_number}""")
        vacations = ''
        try:
            for i in cur.fetchone():
                vacations += f'{i}'
            if vacations == "":
                return True
            if vacations:
                return False
            else:
                return True
        except Exception:
            return True


def delete_date(tab_number, vacations):
    """Удаляет заказанный выходной из базы по tab_number"""
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        select = """DELETE FROM vacations WHERE tab_number = ?"""
        data = (tab_number, )
        cur.execute(select, data)

    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        cur.execute(f"""SELECT * FROM vacations 
                        WHERE tab_number = {tab_number}""")
        vacations = ''
        try:
            for i in cur.fetchone():
                vacations += f'{i}'
            if vacations == "":
                return True
            if vacations:
                return False
            else:
                return True
        except Exception:
            return True


def add_vacations_to_vacations_db(user_id, tab_number, surname, name, from_date, till, duration):
    """РАБОТАЕТ!!!! Добавляет пожелание на каникулы в базу данных."""
    with sqlite3.connect('vacations.db') as con:
        cur = con.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO vacations (id, tab_number, surname, name, from_date, till, duration) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)", (user_id, tab_number, surname, name, from_date, till, duration,))
        return True


def import_vacations_to_excel():
    """импортирует таблицу заказанных выходных дней в эксель"""
    with sqlite3.connect('vacations.db') as con:
        df = pd.read_sql("SELECT * FROM vacations", con)
        df = df[['tab_number', 'surname', 'name', 'from_date', 'till', 'duration']]
        df.rename(columns={'tab_number': 'Табельный №',
                           'surname': 'Фамилия',
                           'name': "Имя",
                           'from_date': 'Начало',
                           'till': 'Окончание',
                           'duration': 'Продолжительность'}, inplace=True)
        df.to_excel(f'vacations.xlsx', index=False)


def import_users_to_excel():
    """Создает в папке эксель файл с пользователями на основе обще базы данных бортпроводников general.db"""
    with sqlite3.connect('users.db') as con:
        df = pd.read_sql("SELECT * FROM users", con)
        df = df[['id', 'tab_number', 'surname', 'name']]
        df.to_excel('users.xlsx', index=False)


# to_create_vacations_db()
# to_create_users_db()