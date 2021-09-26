import requests

cities = ['москва', 'шереметьево', "внуково", "пулково", "махачкала", "ростов-на-дону", "сургут", "новосибирск",
          "тюмень", "екатеринбург", "ларнака", "анталия", "барселона", "пермь", "грозный", "мурманск", "архангельск",
          "ташкент", "екатеринбург", "челябинск", "новосибирск", "сочи", "анапа", "геленджик", "париж", "ереван",
          "лондон", "рим", "милан", "берлин", "мюнхен", "калининград", "уфа", "ницца", "нижний новгород", "казань",
          "красноярск"]


def make_parameters():
    params = {
        'format': 1,  # погода одной строкой
        'M': '',  # скорость ветра в "м/с"

    }
    return params


def what_weather(city):
    params = {'format': 2,  # погода одной строкой
              'M': ''  # скорость ветра в "м/с"
              }
    url = f'http://wttr.in/{city}'

    try:
        weather = requests.get(url, params=params)
        return f'Сейчас в г. {city.capitalize()} {weather.text}'
    except requests.ConnectionError:
        return False
    if response.status_code != 200:
        return False
