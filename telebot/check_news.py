import requests
import dict_users
from bs4 import BeautifulSoup
import os


def document_analyze(new_document):
    """Анализирует название документа на наличие ненужных слов"""
    new_document = new_document[:-23]
    if "Объявление" in new_document:
        new_document = new_document[29:]
    if "Т-" in new_document:
        words_list = new_document.split()
        new_document = ' '.join(words_list[1:-1])
    if "Бюллетень" in new_document:
        words_list = new_document.split()
        new_document = ' '.join(words_list[2:])
    if "Инструкция" in new_document:
        if '_' in new_document:
            words_list = new_document.split('_')
            new_document = ' '.join(words_list[1:-1])
        else:
            words_list = new_document.split()
            new_document = ' '.join(words_list[1:-1])
    if "(изм." in new_document:
        new_document = new_document[:-10]
    if "изд." in new_document:
        new_document = new_document[:-10]
    if "ГД" in new_document:
        if '_' in new_document:
            words_list_ = new_document.split('_')
            new_document = ' '.join(words_list_[1:])
        else:
            words_list_space = new_document.split()
            new_document = ' '.join(words_list_space[1:-1])
    return new_document


def parser(tab_number, password,
           user_id):  # это надо было все обернуть в функцию чтобы потом при импорте вызвать модуль.функция()
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
        return "Чтобы узнать какие новые документы выложили в OpenSky для ознакомления, Вам необходимо сообщить свой логин и пароль через пробел 4 слова в следующем формате: логин .... пароль .....", None

    soup = BeautifulSoup(main_page.content, 'html.parser')  # .find_all('div', {'class': ['dhx_cal_event_line_start']})
    events = soup.select('.table.table-striped.table-condensed.table-hover')

    doc_list = []
    report = ''
    old_file = None

    try:
        table = events[0]
    except Exception:
        return None, None
    tbody = table.contents[1]
    rows = tbody.contents

    doc_path = "/usr/local/bin/bot/documents/doc" + str(
        user_id) + ".txt"  # "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\telebot\\documents\\doc" + str(user_id) + ".txt" # #
    if os.path.exists(doc_path):
        with open(doc_path, 'r', encoding='utf-8') as original:  # если ошибка: такой директории нет
            old_file = original.read()

    for tr in rows:
        cells = tr.contents
        if len(cells) == 0:
            a = str(rows[1]).split('>')[5][:-3]
            return f"Необходимо ознакомиться с документом: \n- {a}", a
        name_document = cells[1].text
        date_exp = cells[2].text
        name_button = cells[3].text  # Скачать или Подтвердить
        if name_button == "Скачать":
            name_document = document_analyze(name_document)
            doc_list.append(name_document)

    if len(doc_list) != 0:
        report += f"Появились новые документы в OpenSky: \n- "
        #
        if old_file is not None:
            for doc in doc_list:
                if doc not in old_file:
                    report += doc + '\n- '
        if old_file is None:
            for doc in doc_list:
                report += doc + '\n- '

        report_for_user = report[:-2]
        report_for_file_temp_list = report_for_user.split('\n')[1:]
        report_for_file = '\n'.join(report_for_file_temp_list)

        return report_for_user, report_for_file
    else:
        return None, None

# parser('119221', '2DH64rf2', 157758328)
