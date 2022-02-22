import requests
import dict_users
import time
from bs4 import BeautifulSoup
import pytz
from datetime import datetime, timedelta
import exception_logger


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
    'Краснярс-1': 'Красноярск',
    'Сыктывкр': 'Сыктывкар',
    'Нвартовс-1': 'Нижневартовск',
    'Хомутово': 'Южно-Сахалинск',
    'Ницца-2': 'Ницца',
    'Нижновгр': 'Н.Новгород',
    'Архангск': 'Архангельск',
    'Дубай-2': 'Дубай',
    'Вена-3': 'Вена',
    'Бранденб-1': 'Бранденбург',
    'Владсток': 'Владивосток',
    'Астрахан': 'Астрахань',
    'Тельавив-3': 'Тель-Авив',
    'Дубай-1': 'Дубай',
    'Самаркан': 'Самарканд'

}

cities_code = {'Внуково-A': 'VKO',  # 'Внуково    ',
               'Воронеж': 'VOZ',
               'Ижевск': 'IJK',
               'Сыктывкр': 'SCW',
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
               'Красндар-1[Пас]': 'KRRп',
               'Бургас': 'BOJ',
               'Пермь': 'PEE',
               'Пермь[Пас]': 'PEEп',
               'Оренбург': 'REN',
               'Самаракр': 'KUF',
               'Самаракр[Пас]': 'KUFп',
               'Саранск': 'SKX',
               'Симфероп': 'SIP',
               'Екатерин': 'SVX',
               'Екатерин[Пас]': 'SVXп',
               'Дубай-2': 'DXB',
               'Минск2': 'MSQ',
               'Челябинс': 'CEK',
               'Шеремет-D': 'SVO',
               'Шеремет-D[Пас]': 'SVOп',
               'Шеремет-B': 'SVO',
               'Шеремет[Пас]': 'SVOп',
               'Шарджа': 'SHJ',
               'Череповц': 'CEE',
               'Ярославт': 'IAR',
               'Новосибт': 'OVB',
               'Новосибт[Пас]': 'OVBп',
               'Нижновгр': 'GOJ',
               'Нижновгр[Пас]': 'GOJп',
               'Челябинск[Пас]': 'CEKп',
               'Челябинс[Пас]': 'CEKп',
               'Шармшейх-1': 'SSH',
               'Казань': 'KZN',
               'Тюмень': 'TJM',
               'Платов[Пас]': 'ROVп',
               'Хургада-2': 'HRG',
               'Нурсулта-1': 'NQZ',
               'Красндар-1': 'KRR',
               'Архангск': 'ARH',
               'Дубай-1': 'DXB',
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


def extract_destination(s):
    destination = s[-21:-5]


def parser(user_id, tab_number, password, autoconfirm, time_depart):
    # start_processing_time = time.time()
    url = 'https://edu.rossiya-airlines.com/workplan/'
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

    if password == '' or not password or password == '0':  # TODO сделать в базе всем одинаково
        return

    if autoconfirm:
        # start_autoconf_signup_time = time.time()
        try:
            s.post(url, data=data, headers=dict(Referer=url))  # work_plan = response 200
        except Exception:
            time.sleep(50)
        # finish_autoconf_signup_time = time.time()
        month_year = time.strftime('%m.%Y')
        url = 'https://edu.rossiya-airlines.com/workplan/'
        data = {
            'domain': 'stc.local',
            'dateFrom': f'01.{month_year}',
            'time_type': 'UTC',
            'accept': '1',  # подтверждение плана работ
        }
    try:
        # start_without_autoconf_signup_time = time.time()
        work_plan = s.post(url, data=data, headers=dict(Referer=url))
        # finish_without_autoconf_signup_time = time.time()
    except Exception as exc:  # ConnectionResetError(10054, 'Удаленный хост принудительно разорвал существующее подключение'
        exception_logger.writer(exc=exc, request=url, fio=user_id)
        return

    soup = BeautifulSoup(work_plan.content, 'html.parser')

    work_plan.close()  # TODO проверить помогает ли это устртанить ошибку

    events = soup.select('.table.table-striped.table-hover.table-condensed')
    try:
        table = events[0]
    except Exception as exc:
        error = f"\t    Проблема с получением плана работ. Причин может быть три: \n" \
                f"- либо сервер перегружен количеством обращений, и нужно немного подождать;\n" \
                f"- либо у Вас еще нет допуска к рейсам; \n" \
                f"- либо в базе указан неверный логин {tab_number} и пароль {password} \n" \
                f"    Если это действиетльно так, то Вы можете сообщить " \
                f"новый логин и пароль в ответном сообщении в следующем формате: логин ....... пароль ....... \n " \
                f"(4 слова через пробел) \n" \
                f"    Менять старый пароль каждый раз не нужно, достаточно ввести старый пароль в графу нового " \
                f"пароля по ссылке pwd.rossiya-airlines.com"
        exception_logger.writer(exc=exc, request='парсинг плана', fio=user_id,
                                answer='неверный логин и пароль')
        return error

    tbody = table.contents[1]
    rows = tbody.contents
    output_info = 'Ваш ближайший план работ:\n'
    string_copy = None

    start_cycle_plan_time = time.time()

    for tr in rows:
        event_detected = False
        string1 = False
        cells = tr.contents
        day_month_start = cells[1].text[:5]
        msk_start = cells[2].text
        utc_start = cells[3].text
        flight_number = cells[4].text
        aircraft = cells[5].text
        route_arrive_time = cells[6].text
        destination = cells[6].text.split(' ')[0].title()
        # print(tr)
        if utc_start == '':
            time_start = '00:00'
        else:
            time_start = utc_start  # eval(dict_users.users[user_id]['time_depart'])
        time_zona = time_depart[:3]

        depart_utc_dt = f"{day_month_start} {time_start}"

        if time_depart == 'msk_start':
            dt_object = datetime.strptime(depart_utc_dt, '%d.%m %H:%M').replace(tzinfo=pytz.utc)
            start_dt = dt_object.astimezone(pytz.utc) + timedelta(hours=3)
            day = start_dt.strftime('%d')
            month = start_dt.strftime('%m')
            hour = start_dt.strftime('%H')
            minute = start_dt.strftime('%M')
            start_dt = f'{day}.{month} {hour}:{minute}'
        # if time_depart == 'ekb_start':
        #     dt_object = datetime.strptime(depart_utc_dt, '%d.%m %H:%M').replace(tzinfo=pytz.utc)
        #     start_dt = dt_object.astimezone(pytz.utc) + timedelta(hours=5)
        #     day = start_dt.strftime('%d')
        #     month = start_dt.strftime('%m')
        #     hour = start_dt.strftime('%H')
        #     minute = start_dt.strftime('%M')
        #     start_dt = f'{day}.{month} {hour}:{minute}'
        else:
            start_dt = depart_utc_dt

        if 'ВХД' in cells[4].text:
            date_end, msk_end = extract_arrive(route_arrive_time)
            string = f'{date_end} Заказанный выходной\n'
            start_dt = ''
            event_detected = True
        if 'резерв' in cells[4].text:
            day_month_arr, msk_time = extract_arrive(route_arrive_time)
            reserve = 'Резерв'
            string = f'{start_dt} {reserve:11.11} {msk_time}\n'
            event_detected = True
        if 'ВЛЭК' in cells[4].text:
            string = f'{start_dt} ВЛЭК \n'
            event_detected = True
        if 'Больничный' in cells[4].text:
            sick_end_date = route_arrive_time[4:-6]
            string = f"{day_month_start} Больничный лст по {sick_end_date}\n"
            start_dt = ''
            event_detected = True
        if 'Англ' in cells[4].text:
            string = f'{start_dt} Английский\n'
            event_detected = True
        if 'отпуск' in cells[4].text.lower():
            string = f'{day_month_start}       Отпуск   по {route_arrive_time[4:-6]}\n'
            if string_copy == string:
                string = ''
            event_detected = True
        if 'ШТБ' in cells[4].text:
            string = f'{start_dt} Вызов в Штаб\n'
            event_detected = True
        if 'КПК' in cells[4].text:
            string = f'{start_dt} КПК\n'
            event_detected = True
        if 'КМД...[КОМАНДИРОВКА]...КПК' in cells[4].text:
            string = f'{start_dt} КПК Командировка\n'
            event_detected = True
        if 'САН.МИН' in cells[4].text:
            string = f'{start_dt} Санминимум\n'
            event_detected = True
        if 'АСП' in cells[4].text:
            string = f'{start_dt} АСП\n'
            event_detected = True
        if 'МКК' in cells[4].text:
            string = f'{start_dt} МКК\n'
            event_detected = True
        if 'Переподготовка' in cells[4].text:
            string = f'{start_dt} Переподготовка {destination.upper():2.2}\n'
            event_detected = True
        if 'Учеба СБЭ' in cells[4].text:
            string = f'{start_dt} Учёба на СБ\n'
            event_detected = True
        if 'Тест' in cells[4].text:
            string = f'{start_dt} Тест\n'
            event_detected = True
        if 'Бизнес' in cells[4].text:
            string = f'{start_dt} Учеба на бизнес\n'
            event_detected = True

        if cells[6].text.count('/') == 2:
            day_mont_arr, msk_time = extract_arrive(cells[6].text)
            city = extract_city(route_arrive_time)
            city = change_cities(city)
            if (int(day_mont_arr[:2]) - int(day_month_start[:2])) <= 1:
                string = f'{start_dt} {city:11.11} {msk_time}\n'
            if (int(day_mont_arr[:2]) - int(day_month_start[:2])) > 1:
                # string = f'{start_dt} {city} {day_mont_arr} {msk_time}\n'
                string = f'{start_dt} {city[:12]}..\n' \
                         f'{day_mont_arr}       ..{destination} {msk_time}\n'
            event_detected = True

        if cells[6].text.count('/') > 2:
            day_mont_arr, msk_time = extract_arrive(cells[6].text)
            route = route_arrive_time.title().replace(" ", "")[:-25]
            route = route.split('/')[1:]  #
            city = ''
            for i in route:
                city += change_to_code(i)
            city = city[:-1]
            if 'LED--LED' in city:
                city = city.replace('LED--LED', 'LED')
            if len(city) == 12:
                string = f'{start_dt} {city[:12]}{msk_time}\n'
            else:
                string = f'{start_dt} {city[:11]}..\n' \
                         f'{day_mont_arr}        ..{city[-8:]:8.8} {msk_time}\n'  # первая цифра добавляет пробела после строки - определеяет размер поля, вторая цифра определяет начало строки - пробелы перед строкой
            event_detected = True
        if not event_detected:
            string = f'{start_dt} {cells[4].text}\n'

        if 'plan_del' in str(tr):
            string = ''
        if string_copy == string:
            string = ''

        current_month = current_dt_minus_4h[3:5]
        plan_month = string[3:5]
        plan_day = string[:2]
        string_copy = string

        if current_month == '01' and plan_month == '12':
            continue

        if current_month == '12' and plan_month == '01':
            output_info += string
            continue

        if current_month <= plan_month:
            if current_dt_minus_4h <= string:  # сравниваем день
                output_info += string
                continue
            if current_month < plan_month and plan_day < current_dt_minus_4h:
                output_info += string

    # finish_cycle_plan_time = time.time()

    if output_info == 'Ваш ближайший план работ:\n':
        return 'Рейсов на ближайшее время не найдено.'
    if len(start_dt) == 11:
        if output_info != 'Ваш ближайший план работ:\n':
            output_info += f'        {time_zona.upper()}               MSK\n'

    # print(output_info)
    # finish_processing_time = time.time()
    # print(f"время общее на человека: {finish_processing_time - start_processing_time}")
    # print(f"подключение, авторизация: {finish_autoconf_signup_time - start_autoconf_signup_time}")
    # print(f"подключение, авторизация: {finish_without_autoconf_signup_time - start_without_autoconf_signup_time}")
    # print(f"обработка плана: {finish_cycle_plan_time - start_cycle_plan_time}")
    return "<pre>" + output_info + "</pre>"

# # TODO РАСКОМЕНТИЛ ЛИ ТЫ RETURN!!!!!!!!!!!!!!!!!!!!!!!!!

# TODO ПРОВЕРЬ ПРИНТЫ ЛОГИН И ПАРОЛЬ!!!!!!!!!!!!!!!!!!!!!!!!!


# parser(512766466, '122411', 'Rabota6!', False, 'msk_start')  # шемякин
# parser(157758328, '119221', '2DH64rf2', True, 'msk_start')  # азаров
# parser(801093934, '5930', 'Voronova090879', False, 'msk_start')
