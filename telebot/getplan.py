import requests
import dict_users
import time
from bs4 import BeautifulSoup
import pytz
from datetime import datetime, timedelta, timezone

current_datetime = time.strftime('%d.%m %H:%M')  # %H:%M
cities = {
    'Внуково-а': 'Внуково ',  # 'Внуково    ',
    'Анталья-2': 'Анталья    ',
    'Минводы': 'Минводы  ',
    'Уфа-1': 'Уфа         ',
    'Анапа': 'Анапа        ',
    'Гумрак /': 'Гумрак     ',
    'Платов': 'Платов     ',
    'Сургут /': 'Сургут     ',
    'Гелендж': 'Геленджк',
    'Грозный': 'Грозный ',
    'Барселон-1': 'Барселона ',
    'Краснодар-1': 'Краснодр  ',
    'Сочи': 'Сочи         ',
    'Казань': 'Казань     ',  # 'Казань     ',
    'Бургас': 'Бургас     ',
    'Пермь': 'Пермь        ',
    'Оренбург': 'Оренбург '

}


def change_cities(bad_city):
    bad_city = bad_city.strip()
    for c in cities.keys():
        if bad_city[:3] in c:
            new_city = cities[c]
            return new_city
        else:
            return bad_city


def extract_city(s):
    pos = s.index('[')
    cities = s[:pos].split('/')
    return cities[1].strip().capitalize()


def extract_arrive(s):
    # TODO добавить проверку если может не быть прилета
    arrive = s[-21:-5]
    # print(arrive)
    dt_utc_arrive = datetime.strptime(arrive, '%d.%m.%Y %H:%M').replace(tzinfo=pytz.utc)
    dt_msk = str(dt_utc_arrive.astimezone(pytz.utc) + timedelta(hours=3))
    day = dt_msk[8:10]
    month = dt_msk[5:7]
    year = dt_msk[0:4]
    msk_arrive_time = dt_msk[11:16]
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
        'username': dict_users.users[user_id]['tab_number'],  # '119229', #  '119221', #
        'userpass': dict_users.users[user_id]['password'],  # 'Parshina15', #  '2DH64rf2', #
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

    work_plan = s.post(url, data=data, headers=dict(Referer=url))  # work_plan = response 200
    soup = BeautifulSoup(work_plan.content, 'html.parser')  # .find_all('div', {'class': ['dhx_cal_event_line_start']})

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
        sick_status = False
        cells = tr.contents
        day_month_start = cells[1].text[:5]
        msk_start = cells[2].text
        utc = cells[3].text
        flight_number = cells[4].text
        aircraft = cells[5].text
        route_arrive_time = cells[6].text

        if 'ВХД' in cells[4].text:
            date_end, msk_end = extract_arrive(route_arrive_time)
            string = f'{date_end} Заказанный выходной\n'
        if 'резерв' in cells[4].text:
            day_month_arr, msk_time = extract_arrive(route_arrive_time)
            reserve = 'Резерв'
            string = f'{day_month_start} {msk_start} мск {reserve:8.8} {msk_time}\n'
        if 'ВЛЭК' in cells[4].text:
            string = f'{day_month_start} {msk_start} мск ВЛЭК \n'
        if 'Больничный' in cells[4].text:
            sick_status = True
            sick_end_date = route_arrive_time[4:-6]
            sick_string = f"{day_month_start} Больничный лист по {sick_end_date}\n"
        if 'Англ' in cells[4].text:
            string = f'{day_month_start} {msk_start} мск Английский\n'
        if 'Отпуск' in cells[4].text:
            string = f'{day_month_start} Отпуск до        {route_arrive_time[1:-6]}\n'
        if 'ШТБ' in cells[4].text:
            string = f'{day_month_start} {msk_start} мск Вызов в Штаб\n'
        if 'КПК' in cells[4].text:
            string = f'{day_month_start} {msk_start} мск КПК\n'
        if 'САН.МИН' in cells[4].text:
            string = f'{day_month_start} {msk_start} мск Санминимум\n'
        if 'АСП' in cells[4].text:
            string = f'{day_month_start} {msk_start} мск АСП\n'
        if cells[6].text.count('/') == 2:
            day_mont_arr, msk_time = extract_arrive(cells[6].text)
            city = extract_city(route_arrive_time)
            city = change_cities(city)
            if (int(day_mont_arr[:2]) - int(day_month_start[:2])) <= 1:
                string = f'{day_month_start} {utc} utc {city:8.8} {msk_time}\n'
            if (int(day_mont_arr[:2]) - int(day_month_start[:2])) > 1:
                string = f'{day_month_start} {utc} utc {city} прил: {day_mont_arr} {msk_time}\n'
        if cells[6].text.count('/') > 2:
            day_mont_arr, msk_time = extract_arrive(cells[6].text)
            string = f'{day_month_start} {utc} utc {route_arrive_time[12:-29].title()} прил: {day_mont_arr} {msk_time} мск\n'

        if sick_status:
            if current_datetime < sick_end_date:
                output_info += sick_string
                continue
            else:
                continue

        current_month = current_datetime[3:5]
        plan_month = string[3:5]
        plan_day = string
        today = current_datetime

        if current_month <= plan_month:  # (главное, чтобы плановый месяц был не меньше текущего) сравниваем сначала месяц чтобы не получилось 31.07 больше чем 20.08 (чтобы не вылезала дата из из прошлого старого месяца)
            # если текущий месяц меньше или такой же как в плане
            if today <= string:  # сравниваем день
                output_info += string
                continue
            if current_month < plan_month and plan_day < today:
                output_info += string

    if output_info == 'Ваш ближайший план работ:\n':
        return 'Рейсов на ближайшее время не найдено.'

    # print(output_info)

    return "<pre>" + output_info + "</pre>"

# TODO ПРОВЕРЬ ПРИНТЫ ЛОГИН И ПАРОЛЬ!!!!!!!!!!!!!!!!!!!!!!!!!
# parser(304247011)
