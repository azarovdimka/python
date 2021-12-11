import requests
import dict_users
import time
from bs4 import BeautifulSoup
import pytz
from datetime import datetime, timedelta, timezone

# time.perf_counter()
current_date = time.strftime('%d.%m')  # %H:%M
current_month = int(time.strftime('%m'))


def parser(user_id, tab_number,
           password):  # это надо было все обернуть в функцию чтобы потом при импорте вызвать модуль.функция()
    url = 'https://edu.rossiya-airlines.com/workplan/'
    s = requests.Session()

    month = str(int(time.strftime('%m')) - 1)  # отнимаем 1 от текущего месяца потому что нам надо посчитать два месяца
    year = time.strftime('%Y')

    data = {
        'refer': 'https://edu.rossiya-airlines.com//',
        'login': '1',
        'user_id': '',
        'backend_url': 'https://sup.rossiya-airlines.com:8080',
        'username': tab_number,
        'userpass': password,
        'domain': 'stc.local',
        'submit': 'войти',
    }  # TODO ПРОВЕРЬ ПРИНТЫ ЛОГИН И ПАРОЛЬ!!!!!!!!!!!!!!!!!!!!!!!!!

    s.post(url, data=data, headers=dict(Referer=url))  # work_plan = response 200

    if password == '' or password == '0' or password is False:
        return "Посчитать рейсы невозможно, так как неизвестен ваш пароль от OpenSky."

    if month == '01':
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
        error = f"Проблема с подсчетом количества рейсов. Вероятно, в базе указан неверный пароль {password}"
        return error
    tbody = table.contents[1]
    rows = tbody.contents

    general_types_counter_till_18_prev = 0
    sukhoj_till_18_prev = 0
    counter_shoulders_sukhoj_prev = 0
    general_counter_prev = 0

    general_types_counter_till_18 = 0
    sukhoj_till_18 = 0
    counter_shoulders_sukhoj = 0
    general_counter = 0

    for tr in rows:

        cells = tr.contents
        day_month_year_start = cells[1].text.strip()
        departure_dt = f'{day_month_year_start}'  # + {hm_msk_start}
        dt_utc_arrive = datetime.strptime(departure_dt, '%d.%m.%Y').replace(tzinfo=pytz.utc)
        dt_msk = dt_utc_arrive.astimezone(pytz.utc) + timedelta(hours=3)
        month_site = int(dt_msk.month)

        if current_month < month_site:
            break

        flight_number = cells[4].text
        aircraft = cells[5].text
        last_date = cells[6].text

        if current_month > month_site:  # для парсинга предыдущего месяца

            if '/' in flight_number:
                flights_list = flight_number.split('/')
                for flight in flights_list:
                    if 'п' in flight:
                        flights_list.remove(flight)
                general_counter_prev += len(flights_list)
                if 'СУ' in aircraft or 'С9Н' in aircraft:
                    counter_shoulders_sukhoj_prev += flight_number.count('/') + 1  # TODO уточнить систему расчетов
                # if general_counter_prev <= 18 and '/' in flight_number:
                # sukhoj_till_18_prev = general_counter_prev  # TODO эту строку удалить и счетчики тоже?

        if current_month == month_site:  # для парсинга текущего месяца
            last_date = cells[6].text[-21:-16]
            if '/' in flight_number:
                flights_list = flight_number.split('/')
                for flight in flights_list:
                    if 'п' in flight:
                        flights_list.remove(flight)
                general_counter += len(flights_list)
                if 'СУ' in aircraft or 'С9Н' in aircraft:
                    counter_shoulders_sukhoj += flight_number.count('/') + 1  # TODO уточнить систему расчетов
                # if general_counter <= 18:
                # sukhoj_till_18 = general_counter

    shoulder_counter_prev = general_counter_prev
    shoulder_counter = general_counter

    if shoulder_counter_prev > counter_shoulders_sukhoj_prev:
        other_types_shoulders_prev = shoulder_counter_prev - counter_shoulders_sukhoj_prev
    else:
        other_types_shoulders_prev = 0
    if shoulder_counter > counter_shoulders_sukhoj:
        other_types_shoulders = shoulder_counter - counter_shoulders_sukhoj
    else:
        other_types_shoulders = 0

    def get_end(number):
        if str(number)[-1] == '1' and number != 11:
            return ''
        if 5 <= int(str(number)[-1]) <= 9 or int(str(number)[-1]) == 0 or number == 11 or number > 11:
            return 'ов'
        else:
            return 'а'

    if shoulder_counter_prev % 2 == 0:
        general_counter_prev = shoulder_counter_prev // 2
    else:
        general_counter_prev = shoulder_counter_prev / 2
    if shoulder_counter % 2 == 0:
        general_counter = shoulder_counter // 2
    else:
        general_counter = shoulder_counter / 2

    if counter_shoulders_sukhoj_prev % 2 == 0:
        flight_counter_sukhoi_prev = counter_shoulders_sukhoj_prev // 2
    else:
        flight_counter_sukhoi_prev = counter_shoulders_sukhoj_prev / 2
    if counter_shoulders_sukhoj % 2 == 0:
        flight_counter_sukhoi = counter_shoulders_sukhoj // 2
    else:
        flight_counter_sukhoi = counter_shoulders_sukhoj / 2

    if other_types_shoulders_prev % 2 == 0:
        other_types_prev = other_types_shoulders_prev // 2
    else:
        other_types_prev = other_types_shoulders_prev / 2

    if other_types_shoulders % 2 == 0:
        other_types = other_types_shoulders // 2
    else:
        other_types = other_types_shoulders / 2

    if last_date == '':
        last_date = current_date

    output_info = f'За прошлый месяц у вас всего {general_counter_prev} рейс{get_end(general_counter_prev)}:\n ' \
                  f'- {flight_counter_sukhoi_prev} рейс{get_end(flight_counter_sukhoi_prev)} на Сухом;\n ' \
                  f'- {other_types_prev} рейс{get_end(other_types_prev)} на других типах.\n\n' \
                  f'За этот месяц c 1 по {last_date} у вас всего {general_counter} рейс{get_end(general_counter)}:\n ' \
                  f'- {flight_counter_sukhoi} рейс{get_end(flight_counter_sukhoi)} на Сухом;\n ' \
                  f'- {other_types} рейс{get_end(other_types)} на других типах.\n\n' \
                  f'Если у Вас есть закрутки, переходящие на следующий месяц - пока такие случаи расчленять и считать не умею.'

    # print(output_info)
    return output_info
    # return "<pre>" + output_info + "</pre>"

# parser(816830262, '119182', 'Airbus339!')
