import requests
import dict_users
import time
from bs4 import BeautifulSoup
import pytz
from datetime import datetime, timedelta
import exception_logger

current_datetime = time.strftime('%d.%m.%Y %H:%M')
dt_utc_arrive = datetime.strptime(current_datetime, '%d.%m.%Y %H:%M').replace(tzinfo=pytz.utc)
dt_minus_4h = dt_utc_arrive.astimezone(pytz.utc) - timedelta(hours=4)

day = dt_minus_4h.strftime('%d')
month = dt_minus_4h.strftime('%m')
year = dt_minus_4h.strftime('%Y')
hour = dt_minus_4h.strftime('%H')
minute = dt_minus_4h.strftime('%M')

current_dt_minus_4h = f'{day}.{month} {hour}:{minute}'


def parser():  # это надо было все обернуть в функцию чтобы потом при импорте вызвать модуль.функция()
    url = 'https://edu.rossiya-airlines.com/ops/viewLineOps-1/'

    s = requests.Session()

    data = {
        'refer': 'https://edu.rossiya-airlines.com//',
        'login': '1',
        'user_id': '',
        'backend_url': 'https://sup.rossiya-airlines.com:8080',
        'username': dict_users.users[157758328]['tab_number'],
        'userpass': dict_users.users[157758328]['password'],
        'domain': 'stc.local',
        'submit': 'войти'
    }  # TODO ПРОВЕРЬ ПРИНТЫ ЛОГИН И ПАРОЛЬ!!!!!!!!!!!!!!!!!!!!!!!!!

    try:
        radar = s.post(url, data=data, headers=dict(Referer=url))
        print(radar)
    except Exception as exc:  # ConnectionResetError(10054, 'Удаленный хост принудительно разорвал существующее подключение'
        exception_logger.writer(exc=exc, request=url, user_id=dict_users.users[user_id])
        return

    soup = BeautifulSoup(radar.content, 'html.parser')
    print(soup.text)

    radar.close()  # TODO проверить помогает ли это устртанить ошибку

    events = soup.select('.table.table-striped.table-hover.table-bordered.sorting3.dataTable.no-footer')
    print(events.text)
    try:
        table = events[0]
    except Exception as exc:
        error = f"Проблема с получением "
        exception_logger.writer(exc=exc, request='парсинг плана', user_id=dict_users.users[user_id],
                                answer='неверный логин и пароль')
        return error

    tbody = table.contents[1]
    rows = tbody.contents
    output_info = 'Ваш ближайший план работ:\n'
    string_copy = None

    # for tr in rows:
    #     string1 = False
    #     cells = tr.contents
    #     day_month_start = cells[1].text[:5]
    #     msk_start = cells[2].text
    #     utc_start = cells[3].text
    #     flight_number = cells[4].text
    #     aircraft = cells[5].text
    #     route_arrive_time = cells[6].text
    #     destination = cells[6].text.split(' ')[0].title()
    #     # print(tr)
    #     if utc_start == '':
    #         time_start = '00:00'
    #     else:
    #         time_start = utc_start  # eval(dict_users.users[user_id]['time_depart'])
    #     time_zona = dict_users.users[user_id]['time_depart'][:3]
    #
    #     depart_utc_dt = f"{day_month_start} {time_start}"
    #
    #     if dict_users.users[user_id]['time_depart'] == 'msk_start':
    #         dt_object = datetime.strptime(depart_utc_dt, '%d.%m %H:%M').replace(tzinfo=pytz.utc)
    #         start_dt = dt_object.astimezone(pytz.utc) + timedelta(hours=3)
    #         day = start_dt.strftime('%d')
    #         month = start_dt.strftime('%m')
    #         hour = start_dt.strftime('%H')
    #         minute = start_dt.strftime('%M')
    #         start_dt = f'{day}.{month} {hour}:{minute}'
    #     else:
    #         start_dt = depart_utc_dt
    #
    #
    #
    #
    # if output_info == 'Ваш ближайший план работ:\n':
    #     return 'Рейсов на ближайшее время не найдено.'
    # if len(start_dt) == 11:
    #     if output_info != 'Ваш ближайший план работ:\n':
    #         output_info += f'        {time_zona.upper()}               MSK\n'
    #
    # # print(output_info)
    # return "<pre>" + output_info + "</pre>"


parser()
