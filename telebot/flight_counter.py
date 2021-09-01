import requests
import dict_users
import time
from bs4 import BeautifulSoup
import pytz
from datetime import datetime, timedelta, timezone

# time.perf_counter()
current_date = time.strftime('%d.%m')  # %H:%M
current_month = int(time.strftime('%m'))


def parser(user_id):  # это надо было все обернуть в функцию чтобы потом при импорте вызвать модуль.функция()
    url = 'https://edu.rossiya-airlines.com/workplan/'
    s = requests.Session()

    month = str(int(time.strftime('%m')) - 1)  # отнимаем 1 от текущего месяца потому что нам надо посчитать два месяца
    year = time.strftime('%Y')

    data = {
        'refer': 'https://edu.rossiya-airlines.com//',
        'login': '1',
        'user_id': '',
        'backend_url': 'https://sup.rossiya-airlines.com:8080',
        'username': dict_users.users[user_id]['tab_number'],  # '119229', #  '119221', # '119182', #'122411',  #
        'userpass': dict_users.users[user_id]['password'],
        # 'Parshina15', #  '2DH64rf2', # 'Airbus338!', #'Rabota5!',  #
        'domain': 'stc.local',
        'submit': 'войти',
    }  # TODO ПРОВЕРЬ ПРИНТЫ ЛОГИН И ПАРОЛЬ!!!!!!!!!!!!!!!!!!!!!!!!!

    s.post(url, data=data, headers=dict(Referer=url))  # work_plan = response 200

    if dict_users.users[user_id]['password'] == '':
        return f"{dict_users.users[user_id]['name']} мы не можем подсчитать за вас рейсы, так как нам неимзвестен ваш пароль от OpenSky"

    if month == '12':
        year = str(int(time.strftime('%Y')) - 1)

    url = 'https://edu.rossiya-airlines.com/workplan/'
    data = {
        'domain': 'stc.local',
        'dateFrom': f'01.{month}.{year}',
        'time_type': 'UTC',
        'accept': '1',
    }

    work_plan = s.post(url, data=data, headers=dict(Referer=url))  # work_plan = response 200
    soup = BeautifulSoup(work_plan.content, 'html.parser')  # .find_all('div', {'class': ['dhx_cal_event_line_start']})

    events = soup.select('.table.table-striped.table-hover.table-condensed')

    try:
        table = events[0]
    except Exception:
        error = f"Проблема с подсчетом количества рейсов. Вероятно, в базе указан неверный логин {dict_users.users[user_id]['tab_number']} и пароль {dict_users.users[user_id]['password']}"
        return error
    tbody = table.contents[1]
    rows = tbody.contents

    flight_list_prev = []
    general_types_counter_till_18_prev = 0
    sukhoj_till_18_prev = 0
    counter_sukhoj_prev = 0
    general_counter_prev = 0

    flight_list = []
    general_types_counter_till_18 = 0
    sukhoj_till_18 = 0
    counter_sukhoj = 0
    general_counter = 0

    for tr in rows:

        cells = tr.contents
        # print(str(tr)[257:])
        # print('')
        day_month_year_start = cells[1].text.strip()  # 03.09.2021
        # hm_msk_start = cells[2].text
        departure_dt = f'{day_month_year_start}'  # + {hm_msk_start}
        dt_utc_arrive = datetime.strptime(departure_dt, '%d.%m.%Y').replace(tzinfo=pytz.utc)
        dt_msk = dt_utc_arrive.astimezone(pytz.utc) + timedelta(days=1)
        month_site = int(dt_msk.month)

        flight_number = cells[4].text
        aircraft = cells[5].text
        last_date = cells[6].text

        if current_month > month_site:  # для парсинга предыдущего месяца

            if general_counter_prev <= 18:
                general_types_counter_till_18_prev += 1
                sukhoj_till_18_prev = counter_sukhoj_prev
            if '/' in flight_number:
                pair_flights_list = flight_number.split('/')
                for flight in pair_flights_list:
                    flight_list_prev.append(flight)
                    general_counter_prev += 1
                if 'СУ' in aircraft:
                    counter_sukhoj_prev += flight_number.count('/') + 1  # TODO уточнить систему расчетов

        if current_month == month_site:  # для парсинга текущего месяца
            last_date = cells[6].text[-21:-16]
            if general_counter <= 18:
                general_types_counter_till_18 += 1
                sukhoj_till_18 = counter_sukhoj
            if '/' in flight_number:
                pair_flights_list = flight_number.split('/')
                for flight in pair_flights_list:
                    flight_list.append(flight)
                    general_counter += 1
                if 'п' in flight_number:
                    number_p = flight_number.count('п')
                    general_counter -= number_p
                if 'СУ' in aircraft:
                    counter_sukhoj += flight_number.count('/') + 1  # TODO уточнить систему расчетов

    flight_counter_prev = len(flight_list_prev)
    flight_counter = len(flight_list)

    other_types_prev = flight_counter_prev - counter_sukhoj_prev
    other_types = flight_counter - counter_sukhoj

    def get_end(number):
        if str(number)[-1] == '1' and number != 11:
            return ''
        if 5 <= int(str(number)[-1]) <= 9 or int(str(number)[-1]) == 0:
            return 'ов'
        else:
            return 'а'

    output_info = f'За прошлый месяц у вас всего {flight_counter_prev} рейс{get_end(flight_counter_prev)}:\n ' \
                  f'- {counter_sukhoj_prev} рейс{get_end(counter_sukhoj_prev)} на Сухом;\n ' \
                  f'- {other_types_prev} рейс{get_end(other_types_prev)} на других типах.\n' \
                  f'C 1 по 18 рейс выполнено {sukhoj_till_18_prev} рейсов на Cухом (доплата +440 руб.) за каждый рейс до 31.12.21 г.\n\n' \
                  f'За этот месяц c 1 по {last_date} у вас всего {flight_counter} рейс{get_end(flight_counter)}:\n ' \
                  f'- {counter_sukhoj} рейс{get_end(counter_sukhoj)} на Сухом;\n ' \
                  f'- {other_types} рейс{get_end(other_types)} на других типах.\n' \
                  f'C 1 по 18 рейс выполнено {sukhoj_till_18} рейсов на Cухом (доплата +440 руб.) за каждый рейс до 31.12.21 г.\n\n' \
                  f'Если у Вас есть закрутки, переходящие на следующий месяц - пока такие случаи расчленять и считать не умею.'

    # print(output_info)
    return output_info
    # return "<pre>" + output_info + "</pre>"
# TODO ПРОВЕРЬ ПРИНТЫ ЛОГИН И ПАРОЛЬ!!!!!!!!!!!!!!!!!!!!!!!!!

# parser(512766466)
