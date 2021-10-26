import requests
import dict_users
import time
from bs4 import BeautifulSoup
import pytz
from datetime import datetime, timedelta, timezone

current_datetime = time.strftime('%d.%m.%y')  # %H:%M


def parser(user_id, name,
           surname):  # это надо было все обернуть в функцию чтобы потом при импорте вызвать модуль.функция()
    url = 'https://edu.rossiya-airlines.com/ready/userReady-1/'

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

    if dict_users.users[user_id]['password'] == '':
        return

    permissions = s.post(url, data=data, headers=dict(Referer=url))  # work_plan = response 200
    soup = BeautifulSoup(permissions.content,
                         'html.parser')  # .find_all('div', {'class': ['dhx_cal_event_line_start']})

    events = soup.select(
        '.my_print_content.sorting_dop.EventTable.table.table-striped.table-bordered.table-hover.table-condensed')
    try:
        table = events[0]
    except Exception:
        error = f"Проблема с проверкой допусков. Вероятно, в базе указан неверный логин {dict_users.users[user_id]['tab_number']} и пароль {dict_users.users[user_id]['password']}"
        return error

    off_directory = "/usr/local/bin/bot/permissions/perm" + str(user_id) + "_" + surname + "/off" + str(
        user_id) + "_" + surname + ".txt"
    exp_directory = "/usr/local/bin/bot/permissions/perm" + str(user_id) + "_" + surname + "/exp" + str(
        user_id) + "_" + surname + ".txt"

    output_info = f'{name}, вот результат проверки сроков действия Ваших документов:\n'
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

        # if now > deadline and document_name not in off_directory:
        #     string += f"Документ {document_name} {aircraft_type} просрочен {day_str}.{month_str}.{year_str}.\n"
        #     output_info += string
        if now.day == deadline.day and now.month == deadline.month and now.year == deadline.year:
            string += f"Сегодня истекает {document_name}\n"
            output_info += string
            found_result = True
        else:
            period = deadline - now
            days_left = str(period).split()[0]

            if 30 < int(
                    days_left) <= 60:  # and (document_name == 'Crew Member Certificate ID' or document_name == 'Заграничный паспорт')\
                # and document_name not in off_directory:
                string += f"- заканчивается {document_name}{aircraft_type}. \n\t Действует до {day_str}.{month_str}.{year_str} \n\t Осталось {period.days} дн.\n"
                output_info += string  # TODO сделать нормальные окончания склонения числительнеых
                found_result = True
            if 0 < int(days_left) <= 30:
                string += f"- заканчивается {document_name}{aircraft_type}. \n\t Действует до {day_str}.{month_str}.{year_str} \n\t Осталось {period.days} дн.\n"
                output_info += string
                found_result = True

    if found_result is None:
        return
    else:
        return output_info
        # print(output_info)

# parser(157758328, "Дмитрий", "Азаров")
