# -*- coding: utf8 -*-

import telebot
# import config # для того чтобы потом токен спрятать в конфиг
import webbrowser
import baza as baza
from telebot import types
# import requests
# import datetime
from random import choice

bot = telebot.TeleBot('1366677314:AAFTpl-zPAFTRCcjuqG2Xc1EOvAAPjmeeVo')

# user_id = message.from_user.id - извлечение id пользователя
# в пин закрепить слоган
# TODO написать новые 4 команды в каждом новом хендлере


@bot.message_handler(commands=['start'])  # приветсвенный стикер и приветственный текст при вступлении в группу
def welcome(message):
    """При первом подключении пользователя к боту - выводит приветсвенный стикер, приветсвенную речь. Также в этой
    функции обозначены кнопки, которые будут всегда отображаться под полем ввода запроса."""
    sti = open('static/AnimatedSticker.tgs', 'rb')
    bot.send_sticker(message.chat.id, sti)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)


    bot.send_message(message.chat.id,
                     'Привет, {0.first_name}!'  # имя пользователя и другие его учетные данные извлекаются только при помощи 0.first_name}. и format(message.from_user, bot.get_me())
                     '\nЯ робот, призванный отвечать на вопросы бортпроводников: '
                     'подготовиться к МКК и КПК, часы работы и номера телефонов отделов и супрервайзеров, '
                     'подсказать как настроить корпоративную почту, явка по форме или нет? и т.д.\n'
                     'Задавай свой первый вопрос.'
                     .format(message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)
    # keyboard

    # ReplyKeyboardMarkup - не привязывается к сообщению # InlineKeyboardMarkup — Она привязывается к сообщению, с которым была отправлена.
    btn1 = types.KeyboardButton('Перейти в OpenSky')
    btn2 = types.KeyboardButton('План работ')
    btn3 = types.KeyboardButton('Мой налет')
    btn4 = types.KeyboardButton('Написать разработчику')
    markup.add(btn1, btn2, btn3, btn4)


def find(question, user_request):
    """Выявляет степень максимального соответсвия искомых слов запросу в каждом результате. Возвращает счетчик: количество совпавших слов."""
    count = 0
    for word in user_request:
        if word in question:
            count += 1
    return count


@bot.message_handler(content_types=["text"])  # эта функция будет вызываться каждый раз, когда боту напишут текст
def conversation(message):
    """Модуль для общения и взаимодействия с пользователем."""

    def details_button(action):
        """Кнопка "подробнее", при нажатии которой будет выводиться более подробная информация по уже полученному ответу."""
        global keyboard
        keyboard = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text=action, url="https://ya.ru")  # адрес, по которому будет открываться более подробная информация
        keyboard.add(url_button)

    def changed(text):
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
                return message
            # else:
            #     return message
        return message

    def find_garbage(message):
        """Ищет лишние слова-сорняки, которые вешают программу: как, кто, где и меняет их на пустую строку"""
        for word in baza.garbage:
            if word in message:
                return message.replace(word, '')
        return message

    def correcting_button(): # две кнопки прикрепляемые к выдаваемому ответу
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(types.InlineKeyboardButton("Отредактировать", callback_data="Отредактировать ответ"),
                   types.InlineKeyboardButton("Всё верно", callback_data="thanks"))
        return markup

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        if call.data == "Отредактировать ответ":
            bot.answer_callback_query(call.id,
                                      bot.send_message(message.chat.id, '   В следующем сообщении напишите еще раз свой вопрос коротко '
                                                                        'и свой вариант ответа в '
                                                                        'произвольной форме, но начинаться ваше сообщение '
                                                                        'должно со слова "правка", например:\n\n'
                                                                        'Правка: Кто желает знать где сидит фазан? Правильный ответ: охотник.'))
        elif call.data == "thanks":
            report = "Пользователь {0.first_name} {0.last_name} @{0.username} id{0.id} поблагодарил за ответ на запрос."\
                .format(message.from_user, message.from_user, message.from_user, message.from_user) # + message.text - почему-то message.text не обновляется
            bot.answer_callback_query(call.id, (bot.send_message(message.chat.id, choice(baza.best_wishes))), bot.send_message(157758328, report))


    def checking_answer(check_answer=None):  # выводит эти кнопки только еслив строгом соответсвии было выдано, потому что там return

        bot.send_message(message.chat.id, check_answer, reply_markup=correcting_button())


    found_result = False  # результат поиска - стоит значение по умолчанию, что ничего не найдено чтобы выводил сообщение что он не смог ничего найти и написать разработчику

    message.text = find_exception(message.text.lower())
    # print(message) # распечатка для полоучения информации оо пользователе написавшем и др.
    message.text = find_garbage(message.text)
    if message.chat.type == 'private':
        if message.text.lower() in baza.greetings:
            bot.send_message(message.chat.id, 'Привет! Буду рад тебе помочь, задавай свой вопрос.')
            return
        if message.text.lower() in baza.good_bye:
            bot.send_message(message.chat.id, choice(baza.best_wishes))
            return

    if 'правка' in message.text.lower() or 'предложить информацию' in message.text.lower():
        answer = "пользователь предложил правку:\n" + message.text
        bot.send_message(message.chat.id, 'Ваша информация успешно отправлена. После ее рассмотрения будут внесены соответсвующие изменения. \n'
                                          'Спасибо за Ваше участие в улучшении Телеграм-Бота!\n'
                                          'В будущем Вы можете предлагать любую свою информацию для внесения в базу данных, просто начав свое сообщение со слов "предложение информации" или "правка".')
        bot.send_message(157758328, answer)
        return

    if len(changed(message.text)) <= 2:
        bot.send_message(message.chat.id, 'Слишком короткий запрос. Пожалуйста, чуть подробнее.')
        return

    if not found_result:
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            if message.text.lower() in question:  # СТРОГОЕ СООТВЕТСТВИЕ  # == заменил на in чтобы учитывать другие формулировки в вопросе, а не рассматривать целиком запрос == целиком вопрос
                bot.send_message(message.chat.id, baza.dictionary[id]['answer'])
                bot.send_message(157758328, "Информация выдана успешно в строгом соответствии")
                found_result = True     # вопрос checking_answer() для строго соответсвия вынесен в конец скрипта

    if not found_result:
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            if changed(message.text) in changed(question): # not found_result and # НЕ СТРОГОЕ СООТВЕТСВИЕ
                if 'Открыть подробную информацию?' not in baza.dictionary[id]['answer']:
                    bot.send_message(message.chat.id, baza.dictionary[id]['answer'])
                    bot.send_message(157758328, "какая-то информация выдана не в строгом соответсвии")
                    checking_answer("Предоставлена корректная информация?")
                    return
                if 'Перейди по ссылке:' in baza.dictionary[id]['answer']:
                    webbrowser.open_new_tab(baza.dictionary[id]['answer'])  # TODO как свделать чтобы браузером сразу открывал ссылку
                    bot.send_message(157758328, "информация выдана не в строгом соответствии")
                    return
                if 'Открыть подробную информацию?' in baza.dictionary[id]['answer']:
                    details_button('Да, рассказать подробнее...')
                    bot.send_message(message.chat.id, baza.dictionary[id]['answer'], reply_markup=keyboard)
                    bot.send_message(157758328, "информация выдана не в строгом соответствии")
                    return
                found_result = True

    if not found_result:                # ЕСЛИ УСЕЧЕННЫЕ СЛОВА НЕ НАЙДЕНЫ - ИЩЕТ В ЛЮБОМ ПОРЯДКЕ В РАМКАХ ВОПРОСА
        changed_user_request = changed(message.text).split()
        max_of_found_words = 0  # в max <- записывается matches <- записывается find(вычисляется количество совпадений слов)
        results = []
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            matches = find(question, changed_user_request)      # для каждого id мы проверяем кол-во соотв-х слов
            if matches == max_of_found_words and matches != 0:   # если количество соответсвий равно максимуму
                results.append(baza.dictionary[id]['answer'])   # ответ заносим в результы
            if matches > max_of_found_words:                    # если соответсвий  больше счетчика максимума
                results.clear()                                 # очищаем список результатов
                max_of_found_words = matches                    # в максимум записываем новую цифру соответсвия
                results.append(baza.dictionary[id]['answer'])   # в результаты добавляем answer
                                                                    # написать обратное условие, что если не будет найдено по вопросам то поискать по ответам

        if len(results) > 0:    # выдает ответы при оптимальном количстве результатов
            found_result = True
            for each_answer in results:
                bot.send_message(message.chat.id, each_answer)
                bot.send_message(157758328, message.text)
                bot.send_message(157758328, "^^^^ по этому запросу выдана информация из слов в случайном порядке")
            checking_answer("Это то, что Вы искали? Информация корректна?")
            return

        if len(results) >= 8:   # не выдает ответы если их 8, крайне редко когда достигается, по другим методам поиска все равно сипит кучу ответов
            bot.send_message(message.chat.id, 'Найдено слишком много ответов. Пожалуйста, уточните свой вопрос или '
                                          'спросите по-другому.')
            return

    if not found_result:    # если ничего не найдено
        message.text = "Пользователь {0.first_name} {0.last_name} @{0.username}  id {0.id} не смог найти запрос:\n "\
                           .format(message.from_user, message.from_user, message.from_user, message.from_user) + message.text
        bot.send_message(157758328, message.text)  # если запрос ненайден - бот об этом сообщит разрабочтику дублированием сообщения напрямую
        bot.send_message(message.chat.id,
                         'Я не знаю, что на это ответить. Попробуйте изменить свой запрос.  \n'
                         'Если вы заметите ошибки, устаревшую информцию '
                         'или обнаружите факты некорректной работы бота - просьба написать об этом '
                         'разработчику @letchikazarov.')

    if found_result:        # две кнопки для списка ответов строгого соответствия
        checking_answer("Всё верно? Есть ошибки?")

#   # bot.reply_to(message, message.text) - ответить переслав сообщение обратно
# print(message) # распечатывает всю информацию о написавшем человеке и историю сообщений в виде словаря
# print(message.text) # message.text - введенное сообщение

bot.polling(none_stop=True)  # запускает бота
