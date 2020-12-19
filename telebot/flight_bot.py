# -*- coding: utf8 -*-

import telebot
from telebot.types import InlineKeyboardMarkup

import baza as baza
from telebot import types
# import requests
# import datetime
from random import choice

bot = telebot.TeleBot('1366677314:AAFTpl-zPAFTRCcjuqG2Xc1EOvAAPjmeeVo')

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

    btn1 = types.KeyboardButton('OpenSky')
    btn2 = types.KeyboardButton('План работ')
    btn3 = types.KeyboardButton('Мой налет')
    btn4 = types.KeyboardButton('Расчётный лист')
    btn5 = types.KeyboardButton('Написать разработчику')     # TODO перестала появляться клавиатура
    markup.add(btn1, btn2, btn3, btn4, btn5)


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

    def open():
        """Предлагает открыть сайт"""
        download_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="ОТКРЫТЬ", url=baza.dictionary[id]['link'])
        download_btn.add(btn)
        bot.send_message(message.chat.id, baza.dictionary[id]['answer'], reply_markup=download_btn)
        bot.send_message(157758328, "Предложили ОТКРЫТЬ сайт или страницу по запросу: " + message.text)
        found_result = True

    def download():
        """Предлагает скачать файл"""
        download_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="СКАЧАТЬ", url=baza.dictionary[id]['link'])
        download_btn.add(btn)
        bot.send_message(message.chat.id, baza.dictionary[id]['answer'], reply_markup=download_btn)
        bot.send_message(157758328, "Предложили скачать файл по запросу: " + message.text)
        found_result = True

    def changed(text):
        """Видоизменяет текст поступающего запроса от пользователя и искомого текста в базе для успешного поиска:
        переводит регистр всех букв в нижний, у каждого слова убирает окончание."""
        lower_text_without_ends = [word[:-2].lower() for word in text.split()]
        return ' '.join(lower_text_without_ends)

    def find_exception(message):
        """все запросы от пользователя (принятые слова) сначала прогоняет через словарь исключений, если функция находит
        его там, то заменяет его на такое же развернутое значение, которое следует использовать при дальнейшем поиске."""
        for id in baza.exceptions:
            if message == baza.exceptions[id]['word']:  # ищет слова для преобразования чтобы обойти минимально допустимое разрешение на длину слова
                message = baza.exceptions[id]['changed_word']
                return message
        return message

    def find_garbage(message):
        """Ищет лишние слова-сорняки, которые вешают программу (как, кто, где) и меняет их на пустую строку"""
        for word in baza.garbage:                       # для каждого слова в кортеже
            if word.lower() in message.lower():                         # если это каждое слово есть в запросе
                return message.replace(word, '')        # нам нужно удалить часть строки
        return message

    def correcting_button():                            # две кнопки прикрепляемые к выдаваемому ответу
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(types.InlineKeyboardButton("Отредактировать", callback_data="Отредактировать ответ"),
                   types.InlineKeyboardButton("Всё верно", callback_data="Всё верно"))
        return markup

    @bot.callback_query_handler(func=lambda call: True)  # Хендлер для работы с существующими сообщениями????
    def callback_query(call):
        answer = ''
        if call.data == "Отредактировать ответ":
            answer = 'В следующем сообщении еще раз коротко напишите свой вопрос и свой вариант ответа в произвольной форме, но начинаться Ваше сообщение должно со слова "правка", например:\n\n Правка: Кто желает знать где сидит фазан? Правильный ответ: охотник.\n\n Пожалуйста, не забывайте пояснять к какому вопросу правка. Присланное Вами сообщение пока не привязывается к ранее выданному ответу)'
        elif call.data == "Всё верно":
            bot.send_message(157758328, "Пользователь сообщил, что всё верно")
            answer = choice(baza.best_wishes)   # TODO вытащить id сообщения до кнопок
        bot.send_message(call.message.chat.id, answer)  # может только одну функцию вызывать # если взаимодействуем с инлайном и нужно отправить текстовое сообщение в ответ, то используем не chat.id, а call.message.chat.id, если хотим отправить короткое уведомление, то bot.answer_callback_query(call.id, "Answer is Yes")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)     # убирает клаиватуру после нажатия кнопок
        bot.delete_message(call.message.chat.id, call.message.message_id)

    def checking_answer(check_answer=None):  # выводит эти кнопки только еслив строгом соответсвии было выдано, потому что там return
        bot.send_message(message.chat.id, check_answer, reply_markup=correcting_button())

    found_result = False  # результат поиска - стоит значение по умолчанию, что ничего не найдено чтобы выводил сообщение что он не смог ничего найти и написать разработчику

    message.text = find_exception(message.text.lower())
    message.text = find_garbage(message.text)

    if message.chat.type == 'private':
        if message.text.lower() in baza.greetings:
            bot.send_message(message.chat.id, 'Привет! Буду рад тебе помочь, задавай свой вопрос.')
            return
        if "спасибо" in message.text.lower() or message.text.lower() in baza.good_bye:   # "спасибо in" помогает избежать кучи разных ответов если пишут "спасибо за информацию" и подобное...
            bot.send_message(message.chat.id, choice(baza.best_wishes))
            bot.send_message(157758328, "Пользователь id{0.id} @{0.username} {0.last_name} {0.first_name} поблагодарил." \
                .format(message.from_user, message.from_user, message.from_user, message.from_user))
            return

    if 'правка' in message.text.lower() or 'предложить информацию' in message.text.lower():
        correct = "Пользователь id{0.id} @{0.username} {0.last_name} {0.first_name} предлоджил правку:\n" \
            .format(message.from_user, message.from_user, message.from_user, message.from_user) + message.text[7:]
        bot.send_message(message.chat.id, 'Ваша информация успешно отправлена. После ее рассмотрения будут внесены соответсвующие изменения. \n'
                                          'Спасибо за Ваше участие в улучшении Телеграм-Бота!\n'
                                          'В будущем Вы можете предлагать любую свою информацию для внесения в базу данных, просто начав свое сообщение со слов "предложение информации" или "правка".')
        bot.send_message(157758328, correct)
        return

    if "отчёт пользователю" in message.text.lower():
        bot.send_message(111, "Юрий, добавчоный номер бухгалтерии успешно изменен на 1017.")
        bot.send_message(157758328, "Отчет пользователю отправлен успешно")
        found_result = True  # вопрос checking_answer() для строго соответсвия вынесен в конец скрипта

    if len(changed(message.text)) <= 2:
        bot.send_message(message.chat.id, 'Слишком короткий запрос. Пожалуйста, чуть подробнее.')
        return

    if not found_result:            # СТРОГОЕ СООТВЕТСТВИЕ
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            if message.text.lower() in question:
                if 'скачать' in question:   # так надо 2 раза
                    download()
                    found_result = True
                elif 'просмотреть' in question:   # так надо 2 раза
                    open()
                    found_result = True
                else:   # так надо 2 раза
                    bot.send_message(message.chat.id, baza.dictionary[id]['answer'])
                    bot.send_message(157758328,
                                     "1 - Информация выдана успешно в строгом соответствии по запросу: " + message.text)
                    found_result = True  # вопрос checking_answer() для строго соответсвия вынесен в конец скрипта

    if not found_result:            # НЕ СТРОГОЕ СООТВЕТСВИЕ
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            if changed(message.text) in changed(question):
                if 'скачать' in question:
                    download()
                    found_result = True
                elif 'просмотреть' in question:
                    open()
                    found_result = True
                else:
                    bot.send_message(message.chat.id, baza.dictionary[id]['answer'])
                    bot.send_message(157758328, "2 - какая-то информация выдана не в строгом соответсвии по запросу: " + message.text)
                    found_result = True

    if not found_result:            # ИЩЕТ В ЛЮБОМ ПОРЯДКЕ В РАМКАХ ВОПРОСА
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

        if len(results) < 8:    # выдает ответы при оптимальном количстве результатов
            for each_answer in results:
                bot.send_message(message.chat.id, each_answer)
                bot.send_message(157758328, "3 - выдана информация из слов в случайном порядке по запросу: " + message.text)
                found_result = True

        if len(results) >= 8:   # не выдает ответы если их 8, крайне редко когда достигается, по другим методам поиска все равно сипит кучу ответов
            bot.send_message(message.chat.id, 'Найдено слишком много ответов. Пожалуйста, уточните свой вопрос или '
                          'спросите по-другому.')
    # TODO написать обратное условие, что если не будет найдено по вопросам то поискать по ответам
    if not found_result:    # если ничего не найдено
        message.text = "Пользователь {0.first_name} {0.last_name} @{0.username} id{0.id} не смог найти запрос:\n" \
            .format(message.from_user, message.from_user, message.from_user, message.from_user) + message.text

        bot.send_message(157758328, message.text)  # если запрос ненайден - бот об этом сообщит разрабочтику дублированием сообщения напрямую
        bot.send_message(message.chat.id,
                         'Я не знаю, что на это ответить. Попробуйте изменить свой запрос.  \n'
                         'Ваш неудачный запрос уже направлен разработчику на рассмотрение.\n'
                         'Если вы заметите ошибки, устаревшую информцию '
                         'или обнаружите факты некорректной работы бота - просьба написать об этом также  '
                         'разработчику @letchikazarov.\n\n'
                         'Либо вы можете самостоятельно внести информацию в базу данных, начав свое сообщение со слов "предложить информацию:". Информация бдует внесена через некоторое время после предварительной модерации.')

    if found_result:  # две кнопки для списка ответов строгого соответствия
        checking_answer("Всё верно? Есть ошибки?")

# ReplyKeyboardMarkup - не привязывается к сообщению
# InlineKeyboardMarkup — Она привязывается к сообщению, с которым была отправлена.
# user_id = message.from_user.id - извлечение id пользователя
# bot.reply_to(message, message.text) - ответить переслав сообщение обратно
# print(message) # распечатывает всю информацию о написавшем человеке и историю сообщений в виде словаря
# print(message.text) # message.text - введенное сообщение

bot.polling(none_stop=True)  # запускает бота
