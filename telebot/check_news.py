import requests
import dict_users
from bs4 import BeautifulSoup


def document_analyze(new_document):
    """Анализирует название документа на наличие ненужных слов"""
    new_document = new_document[:-23]
    if "Объявление" in new_document:
        new_document = new_document[29:]
    if "Инструкция" in new_document:
        new_document = new_document[13:]
    if "(изм." in new_document:
        new_document = new_document[:-10]
    if "изд." in new_document:
        new_document = new_document[:-10]
    return new_document


def parser(tab_number,
           password):  # это надо было все обернуть в функцию чтобы потом при импорте вызвать модуль.функция()
    url = 'https://edu.rossiya-airlines.com/'

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

    try:
        main_page = s.post(url, data=data, headers=dict(Referer=url))  # main_page = response 200
    except:
        return "Чтобы узнать какие новые документы выложили в OpenSky для ознакомления, Вам необходимо сообщить свой логин и пароль через пробел 4 слова в следующем формате: логин .... пароль ....."
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
            name_document = document_analyze(name_document)
            doc_list.append(name_document)
    if len(doc_list) != 0:
        report += f"Появились новые документы в OpenSky: \n- "
        for doc in doc_list:
            report += doc + '\n- '
        # print(report[:-2])
        return report[:-2]
    else:
        return None

# parser(157758328)
