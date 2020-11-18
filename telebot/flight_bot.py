import telebot
# import config # для того чтобы потом токен спрятать в конфиг
import webbrowser
import baza as baza
from telebot import types
import requests
import datetime
from random import choice

bot = telebot.TeleBot('1366677314:AAH3AlfnwN_mo2M8pWcFCK6rHORKu3A4BK4')


# в пин закрепить слоган

@bot.message_handler(commands=['start'])  # приветсвенный стикер и приветственный текст при вступлении в группу
def welcome(message):
    """При первом подключении пользователя к боту - выводит приветсвенный стикер, приветсвенную речь. Также в этой
    функции обозначены кнопки, которые будут всегда отображаться под полем ввода запроса."""
    sti = open('static/AnimatedSticker.tgs', 'rb')
    bot.send_sticker(message.chat.id, sti)

    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Перейти в OpenSky')
    item2 = types.KeyboardButton('Написать разработчику')

    markup.add(item1, item2)

    bot.send_message(message.chat.id, 'Привет, {0.first_name}!' # имя пользователя и другие его учетные данные извлекаются только при помощи 0.first_name}. и format(message.from_user, bot.get_me())
                                      '\nЯ - робот, призванный отвечать на вопросы бортпроводников: '
                                      'подготовиться к МКК и КПК, узнать номер телефона супервазера, '
                                      'подсказать как настроить корпоративную почту, явка на те или иные меропрития в '
                                      'штаб по форме штаб или нет? и т.д.\n'
                                      'Задавай свой первый вопрос.'
                     .format(message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=["text"])  # эта функция будет вызываться каждый раз, когда боту напишут текст
def lalala(message):
    """Модуль для общения и взаимодействия с пользователем."""

    def details_button(action):
        """Кнопка "подробнее", при нажатии которой будет выводиться более подробная информация по уже полученному ответу."""
        global keyboard
        keyboard = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text=action, url="https://ya.ru") # адрес, по которому будет открываться более подробная информация
        keyboard.add(url_button)

    def text(text):
        """Видоизменяет текст поступающего запроса от пользователя и искомого текста в базе для успешного поиска:
        переводит регистр всех букв в нижний, у каждого слова убирает окончание."""
        lower_text_without_ends = [word[:-2].lower() for word in text.split()]
        return ' '.join(lower_text_without_ends)

    # ПРОБЛЕМА: если к искомому слово добавляется какая-то буква в качестве оконочания (телефон - телефона), то он не может это найти
    # ПРОБЛЕМА №2: выводит много ненужных ответов если написать слишком простой запрос:

    found_result = False  # результат поиска - стоит значение по умолчанию, что ничего не найдено
                        # чтобы потом при False выводил сообщение что он не смог ничего найти и написать разработчику

    # now = datetime.datetime.now() # на случай использования в дальнейшем текущей даты и времени пользователя
    # today = now.day
    # hour = now.hour

    greetings = ('привет', 'хай', 'здарова', "добрый день", "добрый вечер", "доброе утро", "здравствуйте", "здравствуй")
    good_bye = ("пока", "удачи", "спасибо", "большое спасибо", "круто", "супер", "огонь")
    best_wishes = ('Буду вопросы - пиши! Успехов!', 'Рад был помочь! Я всегда на связи.')

    if message.chat.type == 'private':

        if message.text == 'Перейти в OpenSky':
            bot.send_message(message.chat.id, webbrowser.open('https://edu.rossiya-airlines.com/docs/'))
            found_result = True
        if message.text == 'Написать разработчику':
            bot.send_message(message.chat.id, webbrowser.open('https://t.me/letchikazarov'))
            found_result = True
        if message.text.lower() in greetings:
            bot.send_message(message.chat.id, 'Привет! Буду рад тебе помочь, задавай свой вопрос.')
            return
        if message.text.lower() in good_bye:
            bot.send_message(message.chat.id, choice(best_wishes))
            return

        # if message.text.lower() in greetings and today == now.day and 6 <= hour < 12:
        #     bot.send_message(message.chat.id, 'Доброе утро!')
        #
        # elif message.text.lower() in greetings and today == now.day and 12 <= hour < 17:
        #     bot.send_message(message.chat.id, 'Добрый день!}')
        #
        #
        # elif message.text.lower() in greetings and today == now.day and 17 <= hour < 23:
        #     bot.send_message(message.chat.id, 'Добрый вечер!')

    if len(text(message.text)) <= 3:
        bot.send_message(message.chat.id, 'Слишком короткий запрос. Пожалуйста, чуть подробнее.')
        return

    for id in baza.dictionary:

        if message.text in baza.dictionary[id]['question']:     # выдает ответ, если найдено в строгом соответсвии
            bot.send_message(message.chat.id, baza.dictionary[id]['answer'])
            return
        if text(message.text) in text(baza.dictionary[id]['question']):
            if 'Открыть подробную информацию?' not in baza.dictionary[id]['answer']:
                bot.send_message(message.chat.id, baza.dictionary[id]['answer'])    # выдает ответ если найдено не в строгом соответсвии
            if 'Открыть подробную информацию?' in baza.dictionary[id]['answer']:
                details_button('Да, рассказать подробнее...')
                bot.send_message(message.chat.id, baza.dictionary[id]['answer'],
                                 reply_markup=keyboard)
            found_result = True
            # написать обратное условие, что если не будет найдено по вопросам то поискать по ответам

    if not found_result:
        bot.send_message(message.chat.id, 'Я не знаю что на это ответить. Напишите свой вопрос разработчику'
                                          ' @letchikazarov, он внесет ответ на данный вопрос в базу, либо попробуйте '
                                          'упростить свой запрос. Кроме того, если вы заметите ошибки, устаревшую информцию '
                                          'или обнаружите факты некорректной работы бота - просьба, ткаже написать об этом '
                                          'разработчику для скорейшего исправления.')


#   # bot.reply_to(message, message.text) - ответить переслав сообщение обратно
# print(message) # распечатывает всю информацию о написавшем человеке и историю сообщений в виде словаря
# print(message.text) # message.text - введенное сообщение


bot.polling(none_stop=True)  # запускает бота
