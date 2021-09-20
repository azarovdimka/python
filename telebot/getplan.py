import requests
import dict_users
import time
from bs4 import BeautifulSoup
import pytz
from datetime import datetime, timedelta

current_datetime = time.strftime('%d.%m.%Y %H:%M')
dt_utc_arrive = datetime.strptime(current_datetime, '%d.%m.%Y %H:%M').replace(tzinfo=pytz.utc)
dt_minus_4h = dt_utc_arrive.astimezone(pytz.utc) - timedelta(hours=4)

day = dt_minus_4h.strftime('%d')
month = dt_minus_4h.strftime('%m')
year = dt_minus_4h.strftime('%Y')
hour = dt_minus_4h.strftime('%H')
minute = dt_minus_4h.strftime('%M')

current_dt_minus_4h = f'{day}.{month} {hour}:{minute}'

cities = {
    'Внуково-a': 'Внуково',  # 'Внуково    ',
    'Анталья-2': 'Анталья    ',
    'Минводы': 'Минводы  ',
    'Уфа-1': 'Уфа         ',
    'Анапа': 'Анапа        ',
    'Гумрак /': 'Гумрак     ',
    'Платов': 'Платов     ',
    'Сургут /': 'Сургут     ',
    'Гелендж': 'Геленджик',
    'Грозный': 'Грозный ',
    'Барселон-1': 'Барселона ',
    'Красндар-1': 'Краснодар  ',
    'Калингрд': 'Калининград  ',
    'Сочи': 'Сочи         ',
    'Казань': 'Казань     ',  # 'Казань     ',
    'Бургас': 'Бургас     ',
    'Пермь': 'Пермь        ',
    'Оренбург': 'Оренбург ',
    'Самаракр': 'Самара ',
    'Симфероп': 'Симферополь',
    'Екатерин': 'Екатернбург',
    'Минск2': 'Минск',
    'Челябинс': 'Челябинск',
    'Дюселдрф': 'Дюсельдорф',
    'Новосибт': 'Новосибирск',
    'Махачкал': 'Махачкала',
    'Краснярс-1': 'Краснярск',
}

cities_code = {'Внуково-а': 'VKO',  # 'Внуково    ',
               'Анталья-2': 'AYT',
               'Минводы': 'MRV',
               'Ларнака': 'LCA',
               'Уфа-1[Пас]': 'UFAп',
               'Уфа-1': 'UFA',
               'Уфа-2': 'UFA',
               'Пулково-1[Пас]': 'LEDп',
               'Пулково[Пас]': 'LEDп',
               'Пулково-1': 'LED',
               'Пулково-2': 'LED',
               'Анапа': 'AAQ',
               'Гумрак': 'VOG',
               'Платов': 'ROV',
               'Сургут': 'SGS',
               'Гелендж': 'GDZ',
               'Грозный': 'GRV',
               'Барселон-1': 'BCN',
               'Красндар-2': 'KRR',
               'Калингрд': 'KGD',
               'Сочи': 'AER',
               'Казань[Пас]': 'KZNп',  # 'Казань     ',
               'Бургас': 'BOJ',
               'Пермь': 'PEE',
               'Оренбург': 'REN',
               'Самаракр': 'KUF',
               'Самаракр[Пас]': 'KUFп',
               'Симфероп': 'SIP',
               'Екатерин': 'SVX',
               'Минск2': 'MSQ',
               'Челябинс': 'CEK',
               'Шеремет-D': 'SVO',
               'Шеремет[Пас]': 'SVOп',
               'Шарджа': 'SHJ',
               'Череповц': 'CEE',
               'Ярославт': 'IAR',
               'Новосибт': 'OVB',
               'Новосибт[Пас]': 'OVBп',
               'Нижновгр': 'GOJ',
               'Челябинск[Пас]': 'CEKп',
               'Челябинс[Пас]': 'CEKп',
               'Шармшейх-1': 'SSH',
               'Казань': 'KZN',
               'Тюмень': 'TJM',
               'Платов[Пас]': 'ROVп',
               'Хургада-2': 'HRG'
               }


def change_cities(bad_city):
    bad_city = bad_city.strip()
    for c in cities.keys():
        if bad_city in c:
            new_city = cities[c]
            return new_city
    return bad_city


def change_to_code(rus_city):
    if rus_city in cities_code.keys():
        new_city = cities_code[rus_city]
        return new_city + '-'
    return rus_city + '-'


def extract_city(s):
    pos = s.index('[')
    cities = s[:pos].split('/')
    return cities[1].strip().capitalize()


def extract_arrive(s):
    # TODO добавить проверку если может не быть прилета
    arrive = s[-21:-5]
    # print(arrive)
    dt_utc_arrive = datetime.strptime(arrive, '%d.%m.%Y %H:%M').replace(tzinfo=pytz.utc)
    dt_msk = dt_utc_arrive.astimezone(pytz.utc) + timedelta(hours=3)
    day = dt_msk.strftime('%d')
    month = dt_msk.strftime('%m')
    year = dt_msk.strftime('%Y')
    msk_arrive_time = dt_msk.strftime('%H:%M')
    day_month_arr = f'{day}.{month}'
    return day_month_arr, msk_arrive_time


def parser(user_id):  # это надо было все обернуть в функцию чтобы потом при импорте вызвать модуль.функция()
    url = 'https://edu.rossiya-airlines.com/workplan/'

    s = requests.Session()

    data = {
        'refer': 'https://edu.rossiya-airlines.com//',
        'login': '1',
        'user_id': '',
        'backend_url': 'https://sup.rossiya-airlines.com:8080',
        'username': dict_users.users[user_id]['tab_number'],
        'userpass': dict_users.users[user_id]['password'],
        'domain': 'stc.local',
        'submit': 'войти'
    }  # TODO ПРОВЕРЬ ПРИНТЫ ЛОГИН И ПАРОЛЬ!!!!!!!!!!!!!!!!!!!!!!!!!

    if dict_users.users[user_id]['password'] == '':
        return
    if dict_users.users[user_id]['autoconfirm']:
        work_plan = s.post(url, data=data, headers=dict(Referer=url))  # work_plan = response 200
        month_year = time.strftime('%m.%Y')
        url = 'https://edu.rossiya-airlines.com/workplan/'
        data = {
            'domain': 'stc.local',
            'dateFrom': f'01.{month_year}',
            'time_type': 'UTC',
            'accept': '1',  # подтверждение плана работ
        }
    try:
        work_plan = s.post(url, data=data, headers=dict(Referer=url))
    except Exception as exc:  # ConnectionResetError(10054, 'Удаленный хост принудительно разорвал существующее подключение'
        print(f'{type(exc).__name__} {exc}')
        return

    soup = BeautifulSoup(work_plan.content, 'html.parser')

    work_plan.close()  # TODO проверить помогает ли это устртанить ошибку
    # ConnectionResetError(10054, 'Удаленный хост принудительно разорвал существующее подключение',
    #                      # # как результата открытия более одного клиентского соединения, что провоцирует данную ошибку

    events = soup.select('.table.table-striped.table-hover.table-condensed')
    try:
        table = events[0]
    except Exception:
        error = f"Проблема с получением плана работ. Вероятно, в базе указан неверный логин {dict_users.users[user_id]['tab_number']} и пароль {dict_users.users[user_id]['password']}"
        return error
    tbody = table.contents[1]
    rows = tbody.contents
    output_info = 'Ваш ближайший план работ:\n'

    for tr in rows:
        string1 = False
        cells = tr.contents
        day_month_start = cells[1].text[:5]
        msk_start = cells[2].text
        utc_start = cells[3].text
        flight_number = cells[4].text
        aircraft = cells[5].text
        route_arrive_time = cells[6].text

        if utc_start == '':
            time_start = '00:00'
        else:
            time_start = utc_start  # eval(dict_users.users[user_id]['time_depart'])
        time_zona = dict_users.users[user_id]['time_depart'][:3]

        depart_utc_dt = f"{day_month_start} {time_start}"

        if dict_users.users[user_id]['time_depart'] == 'msk_start':
            dt_object = datetime.strptime(depart_utc_dt, '%d.%m %H:%M').replace(tzinfo=pytz.utc)
            start_dt = dt_object.astimezone(pytz.utc) + timedelta(hours=3)
            day = start_dt.strftime('%d')
            month = start_dt.strftime('%m')
            hour = start_dt.strftime('%H')
            minute = start_dt.strftime('%M')
            start_dt = f'{day}.{month} {hour}:{minute}'
        else:
            start_dt = depart_utc_dt

        if 'ВХД' in cells[4].text:
            date_end, msk_end = extract_arrive(route_arrive_time)
            string = f'{date_end} Заказанный выходной\n'
            start_dt = ''
        if 'резерв' in cells[4].text:
            day_month_arr, msk_time = extract_arrive(route_arrive_time)
            reserve = 'Резерв'
            string = f'{start_dt} {reserve:11.11} {msk_time}\n'
        if 'ВЛЭК' in cells[4].text:
            string = f'{start_dt} ВЛЭК \n'
        if 'Больничный' in cells[4].text:
            sick_end_date = route_arrive_time[4:-6]
            string = f"{day_month_start} Больничный л.  по {sick_end_date}\n"
            start_dt = ''
        if 'Англ' in cells[4].text:
            string = f'{start_dt} Английский\n'
        if 'Отпуск' in cells[4].text:
            string = f'{day_month_start} Отпуск         по {route_arrive_time[4:-6]}\n'
        if 'ШТБ' in cells[4].text:
            string = f'{start_dt} Вызов в Штаб\n'
        if 'КПК' in cells[4].text:
            string = f'{start_dt} КПК\n'
        if 'КМД...[КОМАНДИРОВКА]...КПК' in cells[4].text:
            string = f'{start_dt} КПК Командировка\n'
        if 'САН.МИН' in cells[4].text:
            string = f'{start_dt} Санминимум\n'
        if 'АСП' in cells[4].text:
            string = f'{start_dt} АСП\n'
        if 'МКК' in cells[4].text:
            string = f'{start_dt} МКК\n'
        if cells[6].text.count('/') == 2:
            day_mont_arr, msk_time = extract_arrive(cells[6].text)
            city = extract_city(route_arrive_time)
            city = change_cities(city)
            if (int(day_mont_arr[:2]) - int(day_month_start[:2])) <= 1:
                string = f'{start_dt} {city:11.11} {msk_time}\n'
            if (int(day_mont_arr[:2]) - int(day_month_start[:2])) > 1:
                string = f'{start_dt} {city} прил: {day_mont_arr} {msk_time}\n'
        if cells[6].text.count('/') > 2:
            day_mont_arr, msk_time = extract_arrive(cells[6].text)

            route = route_arrive_time.title().replace(" ", "")[:-25]
            route = route.split('/')[1:]  #
            city = ''
            for i in route:
                city += change_to_code(i)
            string = f'{start_dt} {city[:12]}..\n' \
                     f'{day_mont_arr}       ..{city[-9:-1]:9.9} {msk_time}\n'

        if 'plan_del' in str(tr):
            string = ''

        current_month = current_dt_minus_4h[3:5]
        plan_month = string[3:5]
        plan_day = string

        if current_month <= plan_month:  # (главное, чтобы плановый месяц был не меньше текущего) сравниваем сначала месяц чтобы не получилось 31.07 больше чем 20.08 (чтобы не вылезала дата из из прошлого старого месяца)
            # если текущий месяц меньше или такой же как в плане
            if current_dt_minus_4h <= string:  # сравниваем день
                output_info += string
                continue
            if current_month < plan_month and plan_day < current_dt_minus_4h:
                output_info += string

    if output_info == 'Ваш ближайший план работ:\n':
        return 'Рейсов на ближайшее время не найдено.'
    if len(start_dt) == 11:
        if output_info != 'Ваш ближайший план работ:\n':
            output_info += f'        {time_zona.upper()}               MSK\n'

    # log_out_url = 'https://edu.rossiya-airlines.com/?logout'
    # TODO Правильно ли сделатн выход из клиентского соединения

    # попытка избежать ошибки ConnectionResetError(10054, 'Удаленный хост принудительно разорвал существующее подключение',
    # # как результата открытия более одного клиентского соединения, что провоцирует данную ошибку
    # try:
    #     s.post(log_out_url, headers=dict(Referer=log_out_url))
    # except Exception as exc:
    #     print(f'{type(exc).__name__} {exc}')
    #     return
    # print(output_info)

    return "<pre>" + output_info + "</pre>"

# # TODO РАСКОМЕНТИЛ ЛИ ТЫ RETURN!!!!!!!!!!!!!!!!!!!!!!!!!

# TODO ПРОВЕРЬ ПРИНТЫ ЛОГИН И ПАРОЛЬ!!!!!!!!!!!!!!!!!!!!!!!!!
# parser(716423609)
