import requests
import dict_users
import time
from bs4 import BeautifulSoup
import pytz
from datetime import datetime, timedelta, timezone

current_datetime = time.strftime('%d.%m.%y')  # %H:%M


def parser(user_id, tab_number, password, name):
    url = 'https://edu.rossiya-airlines.com/ready/userReady-1/'

    s = requests.Session()

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

    if not password or password == '0':  # TODO сделать в базе всем одинаково
        return

    permissions = s.post(url, data=data, headers=dict(Referer=url))  # work_plan = response 200
    soup = BeautifulSoup(permissions.content,
                         'html.parser')  # .find_all('div', {'class': ['dhx_cal_event_line_start']})

    events = soup.select(
        '.my_print_content.sorting_dop.EventTable.table.table-striped.table-bordered.table-hover.table-condensed')
    try:
        table = events[0]
    except Exception:
        return
        # error = f"Не удалось проверить сроки действия ваших допусков и документов. Вероятно, в базе указан неверный пароль {password} Если пароль указан устаревший, Вы можете сообщить новый пароль в следующем формате (4 слова через пробел): логин ...... пароль ......."
        # return error

    output_info = f'{name}, истекают сроки действия Ваших документов и допусков. Заканчивается:\n'
    found_result = None

    tbody = table.contents[1]
    rows = tbody.contents

    for tr in rows:
        cells = tr.contents
        document_name = cells[1].text
        document_number = cells[2].text
        aircraft_type = cells[3].text
        if len(aircraft_type) == 1:
            aircraft_type = ''

        start_name = document_name.index('[') + 1
        end_name = document_name.index(']')
        document_name = document_name[start_name:end_name]
        document_name = document_name.replace('Аварийно-спасательная подготовка', 'АСП')
        document_name = document_name.replace('квалификационная проверка навыков работы на ВС', 'КПП')
        document_name = document_name.replace('Получение допуска', 'Допуск')
        document_name = document_name.replace('Служебный пропуск', 'Crew Member Certificate ID')
        document_name = document_name.replace('Пропуск АКР', 'Штабной пропуск')
        document_name = document_name.replace('Ограничение по типу ВС', '')
        document_name = document_name.replace('Санитарный минимум', 'Санминимум')
        document_name = document_name.replace('Кадровый резерв Старший бортпроводник',
                                              '')  # TODO необходимо найтирешение лучше

        date_off = cells[6].text
        year_str = date_off[6:]
        month_str = date_off[3:5]
        day_str = date_off[:2]

        now = datetime.now()
        if document_name == '':
            continue
        if date_off == '':
            continue
        else:
            year = int(f'20{date_off[6:]}')
            month = int(date_off[3:5])
            day = int(date_off[:2])

        deadline = datetime(year, month, day)
        string = ''

        if now.day == deadline.day and now.month == deadline.month and now.year == deadline.year:
            string += f"- !Сегодня *{document_name}*\n"
            output_info += string
            found_result = True
        else:
            period = deadline - now
            days_left = str(period).split()[0]
            try:
                if int(days_left) < 0:  # ЕСЛИ ЧТО-ТО ПРОСРОЧЕНО
                    continue
                if 0 < int(days_left) < 60:
                    string += f"- *{document_name}{aircraft_type}*. \n\t Действует до {day_str}.{month_str}.{year_str} \n\t Осталось {period.days} дн.\n"
                    output_info += string  # TODO сделать нормальные окончания склонения числительнеых
                    found_result = True
            except Exception as exc:
                string += f"- *{document_name}{aircraft_type}*. \n\t Действует до {day_str}.{month_str}.{year_str} \n\t Остался 1 день\n"
                output_info += string  # TODO сделать нормальные окончания склонения числительнеых
                found_result = True

    if found_result is None:
        return
    else:
        return output_info
        # print(output_info)

# parser(157758328, "119221", "2DH64rf2", "Дмитрий")
