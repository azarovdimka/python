import requests
import dict_users
import time
from bs4 import BeautifulSoup

import exception_logger


def parser(user_id):  # это надо было все обернуть в функцию чтобы потом при импорте вызвать модуль.функция()
    url = 'https://edu.rossiya-airlines.com/nalet/'

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
    }

    try:
        nalet = s.post(url, data=data, headers=dict(Referer=url))  # work_plan = response 200
    except Exception as exc:
        exception_logger.writer(exc=exc, request=url, user_id=dict_users.users[user_id])
        return

    month_year = time.strftime('%m.%Y')
    current_date = time.strftime('%d.%m.%Y')

    url = f'https://edu.rossiya-airlines.com/nalet/userNalet-7113/periodWith-01.{month_year}/periodToOn-{current_date}/ajax-1/'
    try:
        nalet = s.post(url, headers=dict(Referer=url))  # work_plan = response 200
    except Exception as exc:
        exception_logger.writer(exc=exc, request=url, user_id=dict_users.users[user_id])
        return

    soup = BeautifulSoup(nalet.content, 'html.parser')  # .find_all('div', {'class': ['dhx_cal_data']})

    # print(soup.prettify())

    tables = soup.select(
        '.table.table-bordered.table-hover.table-condensed.table-striped.my_print_content')  # получаем вообще все, что связано с тегом div
    # print(gotten_nalet)
    try:
        table = tables[0]  # bp дебага смотрим вложенную таблицу
    except Exception:
        return f"\t *Не удалось посчитать налёт.* \n\t {dict_users.users[user_id]['name']}, либо Вы еще никуда не летали в этом месяце, либо у Вас неверно указан логин {dict_users.users[user_id]['tab_number']} и пароль {dict_users.users[user_id]['password']}. Если Вы считаете, что проблема в другом - сообщите об этом разработчику @DeveloperAzarov"
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

    output_info = f'Фактический налёт: {fact_hours}\nНалёт по плану: {plan_hours}'
    return output_info
