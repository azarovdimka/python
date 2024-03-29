import requests
import dict_users
import time
from bs4 import BeautifulSoup
import crypt

import exception_logger


def parser(user_id, tab_number,
           password):  # это надо было все обернуть в функцию чтобы потом при импорте вызвать модуль.функция()
    url = 'https://edu.rossiya-airlines.com/nalet/'

    s = requests.Session()
    password = crypt.decrypt_text(password)

    data = {
        'refer': 'https://edu.rossiya-airlines.com//',
        'login': '1',
        'user_id': '',
        'backend_url': 'https://sup.rossiya-airlines.com:8080',
        'username': tab_number,
        'userpass': password,
        'domain': 'stc.local',
        'submit': 'войти'
    }

    if password == '' or not password or password == '0':  # TODO сделать в базе всем одинаково
        return "Не удалось просмотреть Ваш налёт, так неизвестен Ваш пароль от OpenSky."

    try:
        nalet = s.post(url, data=data, headers=dict(Referer=url))  # work_plan = response 200
    except Exception as exc:
        exception_logger.writer(exc=exc, request=url, fio=user_id, answer=None)
        return

    month_year = time.strftime('%m.%Y')
    current_date = time.strftime('%d.%m.%Y')

    url = f'https://edu.rossiya-airlines.com/nalet/userNalet-7113/periodWith-01.{month_year}/periodToOn-{current_date}/ajax-1/'
    try:
        nalet = s.post(url, headers=dict(Referer=url))  # work_plan = response 200
    except Exception as exc:
        exception_logger.writer(exc=exc, request=url, fio=user_id, answer=None)
        return

    soup = BeautifulSoup(nalet.content, 'html.parser')  # .find_all('div', {'class': ['dhx_cal_data']})

    # print(soup.prettify())

    tables = soup.select(
        '.table.table-bordered.table-hover.table-condensed.table-striped.my_print_content')  # получаем вообще все, что связано с тегом div
    # print(gotten_nalet)
    try:
        table = tables[0]  # bp дебага смотрим вложенную таблицу
    except Exception:
        return f"\t Не удалось посчитать налёт.* \n\t либо Вы еще никуда не летали в этом месяце, либо у Вас неверно " \
               f"указан логин {tab_number} и пароль {password}."
    thead = table.contents[2]
    rows = thead.contents
    tr = rows[0]
    columns = tr.contents
    td = columns[1]
    nalet = td.contents[0]
    fact_hours = nalet.contents[2]

    td = columns[5]
    nalet = td.contents[0]
    plan_hours = nalet.contents[2]
    if plan_hours == '00,00':
        return
    else:
        output_info = f'Фактический налёт: {fact_hours}\nНалёт по плану: {plan_hours}'
        return output_info
