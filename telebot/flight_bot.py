import telebot
# import config # для того чтобы потом токен спрятать в конфиг
import webbrowser
import baza as baza
from telebot import types
import requests
import datetime
from random import choice

bot = telebot.TeleBot('1366677314:AAFTpl-zPAFTRCcjuqG2Xc1EOvAAPjmeeVo')


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

    bot.send_message(message.chat.id,
                     'Привет, {0.first_name}!'  # имя пользователя и другие его учетные данные извлекаются только при помощи 0.first_name}. и format(message.from_user, bot.get_me())
                     '\nЯ - робот, призванный отвечать на вопросы бортпроводников: '
                     'подготовиться к МКК и КПК, узнать номер телефона супервазера, '
                     'подсказать как настроить корпоративную почту, явка на те или иные меропрития в '
                     'штаб по форме или нет? и т.д.\n'
                     'Задавай свой первый вопрос, знак вопроса и вопросительные слова не нужны.'
                     .format(message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=["text"])  # эта функция будет вызываться каждый раз, когда боту напишут текст
def lalala(message):
    """Модуль для общения и взаимодействия с пользователем."""

    def details_button(action):
        """Кнопка "подробнее", при нажатии которой будет выводиться более подробная информация по уже полученному ответу."""
        global keyboard
        keyboard = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text=action,
                                                url="https://ya.ru")  # адрес, по которому будет открываться более подробная информация
        keyboard.add(url_button)

    def text(text):
        """Видоизменяет текст поступающего запроса от пользователя и искомого текста в базе для успешного поиска:
        переводит регистр всех букв в нижний, у каждого слова убирает окончание."""
        lower_text_without_ends = [word[:-2].lower() for word in text.split()]
        return ' '.join(lower_text_without_ends)

    def find_exception(message):
        """все запросы от пользователя (принятые слова) сначала прогоняет через словарь исключений, если функция находит его там, то присваивает ему
        соответсвующее значение, которое следует использовать при дальнейшем поиске."""
        for id in baza.exceptions:
            if message == baza.exceptions[id]['word']:  # ищет слова для преобразования чтобы обойти минимально допустимое разрешение на длину слова
                message = baza.exceptions[id]['changed_word']
                return message #TODO-вопрос почему возращает None??? при том что первое значение в словаре пропускает, остальные слова нет, если не писать дальше else
            else:
                return message



    # TODO-ПРОБЛЕМА: если к искомому слово добавляется какая-то буква в качестве оконочания (телефон - телефона), то он не может это найти
    # TODO-ПРОБЛЕМА №2: выводит много ненужных ответов если написать слишком простой запрос:

    found_result = False  # результат поиска - стоит значение по умолчанию, что ничего не найдено
    # чтобы потом при False выводил сообщение что он не смог ничего найти и написать разработчику

    # now = datetime.datetime.now() # на случай использования в дальнейшем текущей даты и времени пользователя
    # today = now.day
    # hour = now.hour

    message.text = find_exception(message.text)
    print(message)
    if message.chat.type == 'private':

        if message.text == 'Перейти в OpenSky':
            bot.send_message(message.chat.id, webbrowser.open('https://edu.rossiya-airlines.com/docs/'))
            found_result = True
        if message.text == 'Написать разработчику':
            bot.send_message(message.chat.id, webbrowser.open('https://t.me/letchikazarov'))
            found_result = True
        if message.text.lower() in baza.greetings:
            bot.send_message(message.chat.id, 'Привет! Буду рад тебе помочь, задавай свой вопрос.')
            return
        if message.text.lower() in baza.good_bye:
            bot.send_message(message.chat.id, choice(baza.best_wishes))
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

    if len(text(message.text)) <= 2:
        bot.send_message(message.chat.id, 'Слишком короткий запрос. Пожалуйста, чуть подробнее.')
        return

    for id in baza.dictionary:
        # TODO условие на поиск в строгом соответсвии не работает
        if message.text == baza.dictionary[id]['question']:  # выдает ответ, если найдено в строгом соответсвии
            bot.send_message(message.chat.id, baza.dictionary[id]['answer'])
            return
        if text(message.text) in text(baza.dictionary[id]['question']):  # выдает ответ если найдено не в строгом соответсвии
            if 'Открыть подробную информацию?' not in baza.dictionary[id]['answer']:
                bot.send_message(message.chat.id, baza.dictionary[id]['answer'])
            if 'Открыть подробную информацию?' in baza.dictionary[id]['answer']:
                details_button('Да, рассказать подробнее...')
                bot.send_message(message.chat.id, baza.dictionary[id]['answer'],
                                 reply_markup=keyboard)
            found_result = True
            # написать обратное условие, что если не будет найдено по вопросам то поискать по ответам

    if not found_result:
        message.text = "Пользователь {0.first_name} @{0.username} не смог найти запрос:\n ".format(message.from_user, message.from_user) + message.text
        bot.send_message(157758328, message.text) # если запрос ненайден - бот об этом сообщит разрабочтику дублированием сообщения напрямую
        bot.send_message(message.chat.id, 'Я не знаю что на это ответить. Информация о том, что Вы не смогли найти ответ на свой вопрос уже направлена разработчику.\n'
                                          'Вскоре он внесет ответ на Ваш вопрос в базу и оповестит по возможности, либо попробуйте '
                                          'упростить свой запрос: не следует использовать вопросительные слова '
                                          '(как, где, кто, что...), вопросительные знаки и др.  \n'
                                          'Кроме того, если вы заметите ошибки, устаревшую информцию '
                                          'или обнаружите факты некорректной работы бота - просьба, ткаже написать об этом '
                                          'разработчику для скорейшего исправления.')


#   # bot.reply_to(message, message.text) - ответить переслав сообщение обратно
# print(message) # распечатывает всю информацию о написавшем человеке и историю сообщений в виде словаря
# print(message.text) # message.text - введенное сообщение


bot.polling(none_stop=True)  # запускает бота
