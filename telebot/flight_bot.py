import telebot
# import config # для того чтобы потом токен спрятать в конфиг
import webbrowser
import baza as baza
from telebot import types

bot = telebot.TeleBot('1366677314:AAH3AlfnwN_mo2M8pWcFCK6rHORKu3A4BK4')


# в пин закрепить слоган

@bot.message_handler(commands=['start'])  # приветсвенный стикер и приветственный текст при вступлении в группу
def welcome(message):
    sti = open('static/AnimatedSticker.tgs', 'rb')
    bot.send_sticker(message.chat.id, sti)

    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Перейти в OpenSky')
    item2 = types.KeyboardButton('Написать разработчику')

    markup.add(item1, item2)

    bot.send_message(message.chat.id, 'Привет, {0.first_name}!'
                                      '\nЯ  - <b>{1.first_name}</b>, бот созданный отвечать на вопросы бортпроводников: '
                                      'подготовиться к МКК, КПК? узнать номер телефона, явка по форме или нет? и т.д.\n'
                                      'Задавай свой первый вопрос.'
                     .format(message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=["text"])  # эта функция будет вызываться каждый раз, когда боту напишут текст
def lalala(message):

    def button(action):
        global keyboard
        keyboard = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text=action, url="https://ya.ru")
        keyboard.add(url_button)

    def text(text):
        """Видоизменяет текст поступающего запроса от пользователя и искомого текста в базе для успешного поиска:
        переводит регистр всех букв в нижний, у каждого слова убирает окончание."""
        lower_text_without_ends = [item[:-2].lower() for item in text.split()]
        return ' '.join(lower_text_without_ends)

    found_result = False  # результат поиска - стоит значение по умолчанию, что ничего не найдено
    if message.chat.type == 'private':
        if message.text == 'Перейти в OpenSky':
            bot.send_message(message.chat.id, webbrowser.open('https://edu.rossiya-airlines.com/docs/'))
            found_result = True
        if message.text == 'Написать разработчику':
            bot.send_message(message.chat.id, webbrowser.open('https://t.me/letchikazarov'))
            found_result = True

    for id in baza.dictionary:  # для каждой связки ключ-значение
        if text(message.text) in text(baza.dictionary[id]['question']):  # если в каждом вложенном словаре, а конкретно ключ name равна запросу
            if 'Открыть подробную информацию?' not in baza.dictionary[id]['answer']:  # то распечать мне надо из из вложенного словаря другой соответсвующий ключ
                bot.send_message(message.chat.id, baza.dictionary[id]['answer'])
            if 'Открыть подробную информацию?' in baza.dictionary[id]['answer']:
                button('Да, рассказать подробнее...')
                bot.send_message(message.chat.id, baza.dictionary[id]['answer'],
                                 reply_markup=keyboard)
            found_result = True
            # написать обратное условие, что если не будет найдено по вопросам то поискать по ответам

    if not found_result:
        bot.send_message(message.chat.id, 'Я не знаю что на это ответить. Напишите свой вопрос разработчику'
                                          ' @letchikazarov, он внесет ответ на вопрос в базу данных.')


#   # bot.reply_to(message, message.text) - ответить переслав сообщение обратно
# print(message) # распечатывает всю информацию о написавшем человеке и историю сообщений в виде словаря
# print(message.text) # message.text - введенное сообщение


bot.polling(none_stop=True)  # запускает бота
