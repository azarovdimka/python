# <table class="userInfo"><tbody><tr><td>ФИО:</td><td><strong>Азаров Дмитрий Викторович</strong></td></tr><tr><td>Пол:</td><td><strong>муж</strong></td></tr><tr><td>Дата рождения:</td><td><strong>03/05/1986</strong></td></tr><tr><td>Место рождения:</td><td><strong>с.Яр-Сале Ямальского р-на Тюменьской области</strong></td></tr><tr><td>Табельный номер:</td><td><strong>119221</strong></td></tr></tbody></table>

import requests
import dict_users
import time
from bs4 import BeautifulSoup


def parser(user_id):  # это надо было все обернуть в функцию чтобы потом при импорте вызвать модуль.функция()
    url = 'https://edu.rossiya-airlines.com/nalet/'

    s = requests.Session()

    data = {
        'refer': 'https://edu.rossiya-airlines.com//',
        'login': '1',
        'user_id': '',
        'backend_url': 'https://sup.rossiya-airlines.com:8080',
        'username': '119221',  # dict_users.users[user_id]['tab_number'],  # '119229',
        'userpass': '2DH64rf2',  # dict_users.users[user_id]['password'],  # 'Parshina15',
        'domain': 'stc.local',
        'submit': 'войти'
    }

    response = s.post(url, data=data, headers=dict(Referer=url))  # work_plan = response 200
    soup_html = BeautifulSoup(response.content, 'html.parser')  # .find_all('div', {'class': ['dhx_cal_data']})

    user_info = soup_html.select('.userInfo')[0]
    for tr in user_info:
        for td in tr:
            print(td.text)
            # for i in td:
            #     print(i.text)

    menu = soup_html.select('.dropdown-menu.dropdown-user')[1]
    for tr in menu:
        for td in tr:
            for i in td:
                for t in i:
                    if str(t).isalpha():
                        print(t)
                        continue
                    for m in t:
                        if 'src' in str(m):
                            continue
                        else:
                            print(m)
                    # if not str(t).isalpha():
                    #     continue
                    # else:
                    #     print(t)


parser(157758328)
