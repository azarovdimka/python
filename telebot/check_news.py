import requests
import dict_users
from bs4 import BeautifulSoup


def parser(user_id):  # это надо было все обернуть в функцию чтобы потом при импорте вызвать модуль.функция()
    url = 'https://edu.rossiya-airlines.com/'

    s = requests.Session()

    data = {
        'refer': 'https://edu.rossiya-airlines.com//',
        'login': '1',
        'user_id': '',
        'backend_url': 'https://sup.rossiya-airlines.com:8080',
        'username': dict_users.users[user_id]['tab_number'],  # '119229',
        'userpass': dict_users.users[user_id]['password'],  # 'Parshina15',
        'domain': 'stc.local',
        'submit': 'войти'
    }

    try:
        main_page = s.post(url, data=data, headers=dict(Referer=url))  # main_page = response 200
    except:
        return
    soup = BeautifulSoup(main_page.content, 'html.parser')  # .find_all('div', {'class': ['dhx_cal_event_line_start']})

    events = soup.select('.table.table-striped.table-condensed.table-hover')

    doc_list = []
    report = ''

    try:
        table = events[0]
    except Exception:
        return
    tbody = table.contents[1]
    rows = tbody.contents

    for tr in rows:
        cells = tr.contents
        name_document = cells[1].text
        date_exp = cells[2].text
        name_button = cells[3].text  # Скачать или Подтвердить

        if name_button == "Скачать":
            doc_list.append(name_document)
    if len(doc_list) != 0:
        unpacked_list = '\n- '.join('{}' for _ in range(len(doc_list))).format()
        report += f"Появились новые документы в OpenSky: \n" \
                  f"{unpacked_list}"
        return report
    else:
        return None
