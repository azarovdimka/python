# -*- coding: utf8 -*-

import \
    telebot  # чтобы работал telebot - нужно удалить telebot, и установить Pytelegrambotapi но при этом написанным оставить telebot
from telebot.types import InlineKeyboardMarkup
import baza as baza
from telebot import types
from random import choice
import config

bot = telebot.TeleBot(config.api)


# в пин закрепить слоган
# TODO написать новые 4 команды в каждом новом хендлере


def general_menu():
    general_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton('План работ')
    btn2 = types.KeyboardButton('Мой налет')
    btn3 = types.KeyboardButton('Расчётный лист')
    btn4 = types.KeyboardButton('Исправить ответ')
    btn5 = types.KeyboardButton('Добавить  информацию')  # InlineKeyBoard (callback_data='Внести информацию')
    general_menu.add(btn1, btn2, btn3, btn4, btn5)
    return general_menu


@bot.message_handler(commands=['start'])
def welcome(message):
    """При первом подключении пользователя к боту - выводит приветсвенный стикер, приветсвенную речь. Также в этой
    функции обозначены кнопки, которые будут всегда отображаться под полем ввода запроса."""
    sti = open('static/AnimatedSticker.tgs', 'rb')
    bot.send_sticker(message.chat.id, sti)

    bot.send_message(message.chat.id,
                     'Привет, {0.first_name}!'  # имя пользователя и другие его учетные данные извлекаются только при помощи 0.first_name}. и format(message.from_user, bot.get_me())
                     '\nЯ робот, призванный отвечать на вопросы бортпроводников: '
                     'вопросы к МКК и КПК, часы работы и номера телефонов отделов и супрервайзеров, '
                     'настройки почты, аббревиатуры, инструктажи... '
                     'Задавай свой первый вопрос. Лучше коротко.'
                     .format(message.from_user, bot.get_me()), reply_markup=general_menu())


def find(question, user_request):
    """Выявляет степень максимального соответсвия искомых слов запросу в каждом результате: считает количество совпавших
    слов и возвращает счетчик."""
    count = 0
    for word in user_request:
        if word in question:
            count += 1
    return count


@bot.message_handler(content_types=["text"])  #
def conversation(message):
    """Модуль для общения и взаимодействия с пользователем. Декоратор будет вызываться когда боту напишут текст."""

    def open():
        """Предлагает открыть сайт"""
        download_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()  # что такое двоеточие и что оно дает??? reformat сам так сделал
        btn = types.InlineKeyboardButton(text="ОТКРЫТЬ", url=baza.dictionary[id]['link'])
        download_btn.add(btn)
        bot.send_message(message.chat.id, baza.dictionary[id]['answer'], reply_markup=download_btn,
                         parse_mode='Markdown')
        bot.send_message(157758328, "Предложили ОТКРЫТЬ: " + message.text)

    def download():
        """Предлагает скачать файл"""
        download_btn: InlineKeyboardMarkup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="СКАЧАТЬ", url=baza.dictionary[id]['link'])
        download_btn.add(btn)
        bot.send_message(message.chat.id, baza.dictionary[id]['answer'], parse_mode='Markdown',
                         reply_markup=download_btn)
        bot.send_message(157758328, "Предложили скачать: " + message.text)

    def changed(text):
        """Видоизменяет текст поступающего запроса от пользователя и искомого текста в базе для успешного поиска:
        переводит регистр всех букв в нижний, у каждого слова убирает окончание."""
        lower_text_without_ends = [word[:-2].lower() for word in text.split()]
        return ' '.join(lower_text_without_ends)

    def find_exception(message):
        """все запросы от пользователя сначала прогоняет через словарь исключений, если функция находит его там, то
        заменяет его на такое же развернутое значение, которое следует использовать при дальнейшем поиске. ищет слова
        для преобразования чтобы обойти минимально допустимое разрешение на длину слова"""
        for id in baza.exceptions:
            for word in message.split(' '):
                if word == baza.exceptions[id]['word']:
                    changed_word = baza.exceptions[id]['changed_word']
                    message = message.replace(word, changed_word)
                    return message
        return message

    # def find_abbreviation(message):
    #     """проверяет по спику аббревиатур, чтобы выдать развернутое значение аббревиатуры"""
    #     for id in baza.abbreviations:
    #         if message == baza.abbreviations[id]['abbr']:
    #             # answer = baza.abbreviations[id]['deployed']
    #             bot.send_message(message.chat.id, baza.abbreviations[id]['deployed'], parse_mode='Markdown')
    #     bot.send_message(157758328, "аббревиатуры не найдено: " + message)
    #     return message

    def find_garbage(message):
        """Ищет лишние слова-сорняки, которые вешают программу (как, кто, где) и меняет их на пустую строку"""
        for word in baza.garbage:  # для каждого слова в кортеже
            if word.lower() in message.lower():  # если это каждое слово есть в запросе
                return message.replace(word, '')  # нам нужно удалить часть строки
        return message

    def find_non_strict_accordance(message):
        """Ищет не в строгом соответсвии."""
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            if changed(message.text) in changed(question):
                if 'скачать' in question:  # так надо 2 раза
                    download()
                elif 'просмотреть' in question:  # так надо 2 раза
                    open()
                else:  # так надо 2 раза
                    bot.send_message(message.chat.id, baza.dictionary[id]['answer'], reply_markup=general_menu(),
                                     parse_mode='Markdown')
                    bot.send_message(157758328, "2 - информация выдана не в строгом соответсвии по запросу: " + message.text)
                found_result = True
                return found_result

    def find_in_random_order(message):
        """Ищет в случайном соответсвии."""
        changed_user_request = changed(message.text).split()
        max_of_found_words = 0  # в max <- записывается matches <- записывается find(вычисляется количество совпадений слов)
        results = []
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            matches = find(question,
                           changed_user_request)  # matches Принимает число соответсвий слов запроса вопросу в базе для каждого id мы проверяем кол-во соотв-х слов
            if matches == max_of_found_words and matches != 0:  # если количество соответсвий равно максимум
                results.append(baza.dictionary[id].get(
                    'answer'))  # #TODO возникает ошибка здесь key error answer ответ заносим в результы
            if matches > max_of_found_words:  # если соответсвий нашли еще больше итогого счетчика максимума
                results.clear()  # очищаем список результатов
                max_of_found_words = matches  # в максимум записываем новую цифру соответсвия
                results.append(baza.dictionary[id].get('answer'))  # в результаты добавляем answer

        if len(results) < 8:  # выдает ответы при оптимальном количстве результатов
            for each_answer in results:
                if 'скачать' in results:  # так надо 2 раза
                    download()
                    found_result = True
                elif 'просмотреть' in results:  # так надо 2 раза
                    open()
                    found_result = True
                else:  # так надо 2 раза
                    bot.send_message(message.chat.id, each_answer, reply_markup=general_menu(),
                                     parse_mode='Markdown')
                    found_result = True
                bot.send_message(157758328, "3 - выдана информация в случайном порядке по запросу: " + message.text)
                return found_result

        if len(results) >= 8:  # не выдает ответы если их 8, крайне редко когда достигается
            bot.send_message(message.chat.id, 'Найдено слишком много ответов. Пожалуйста, уточните свой вопрос или '
                                              'спросите по-другому.', reply_markup=general_menu(),
                             parse_mode='Markdown')


    # def adding_information():
    #     """Вносит информацию пользователя в бащу данных и перезаписывает файл с базой данных."""
    #     bot.send_message(message.chat.id, 'Для начала добавьте вопрос. Начните свое сообщение со слова "внести вопрос:". Например:\n\n внести вопрос: номер телефона представителя в Москве')

    # def correcting_button():  # две кнопки прикрепляемые к выдаваемому ответу
    #     markup = types.InlineKeyboardMarkup()
    #     markup.row_width = 2
    #     markup.add(types.InlineKeyboardButton("Исправить", callback_data="Исправить ответ"),
    #                types.InlineKeyboardButton("Всё верно", callback_data="Всё верно"))
    #     return markup

    # @bot.callback_query_handler(func=lambda call: True)  # Хендлер для работы с существующими сообщениями????
    # def callback_query(call):
    #     answer = ''
    #     if call.data == "Исправить ответ":
    #         answer = 'В следующем сообщении еще раз коротко напишите свой вопрос и свой вариант ответа в произвольной ' \
    #                  'форме, но начинаться Ваше сообщение должно со слова "правка", например:\n\n Правка: добавочный ' \
    #                  'номер бухгалетрии 1017.\n\n Пожалуйста, не забывайте пояснять к какому вопросу правка ' \
    #                  '(не просто 1017). Присланное Вами сообщение пока не привязывается к ранее выданному ответу.'
    #     elif call.data == "Всё верно":
    #         bot.send_message(157758328, "Пользователь сообщил, что всё верно")
    #         answer = choice(baza.best_wishes)   # TODO вытащить id сообщения до кнопок
    #     bot.send_message(call.message.chat.id, answer)  # может только одну функцию вызывать # если взаимодействуем с инлайном и нужно отправить текстовое сообщение в ответ, то используем не chat.id, а call.message.chat.id, если хотим отправить короткое уведомление, то bot.answer_callback_query(call.id, "Answer is Yes")
    #     bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)     # убирает клаиватуру после нажатия кнопок
    #     bot.delete_message(call.message.chat.id, call.message.message_id)
    # if call.data == "Внести информацию":
    #     send = bot.send_message(message.chat.id, 'Введи город')
    #     bot.register_next_step_handler(send, call)
    #     # log(message)
    #     # answer = "Следующее сообщение начните со слова: внести"

    # def checking_answer(check_answer=None):  # выводит эти кнопки только если в строгом соответсвии было выдано
    #     bot.send_message(message.chat.id, check_answer, reply_markup=correcting_button())

    found_result = False
    global user_id
    # message.text = find_abbreviation(message.text.upper())
    message.text = find_exception(message.text.lower())
    message.text = find_garbage(message.text)

    if message.chat.type == 'private':
        if message.text.lower() in baza.greetings:
            bot.send_message(message.chat.id, 'Привет! Буду рад тебе помочь, задавай свой вопрос.',
                             reply_markup=general_menu())
            return
        if "спасибо" in message.text.lower() or message.text.lower() in baza.good_bye:
            bot.send_message(message.chat.id, choice(baza.best_wishes))
            bot.send_message(157758328, "Пользователь {0.first_name} @{0.username} id{0.id} поблагодарил." \
                             .format(message.from_user, message.from_user, message.from_user),
                             reply_markup=general_menu())
            return

    if "исправить ответ" in message.text.lower():
        bot.send_message(message.chat.id,
                         'В следующем сообщении еще раз коротко напишите свой вопрос и свой вариант ответа в произвольной '
                         'форме, но начинаться Ваше сообщение должно со слова "исправить", например:\n\n '
                         'Исправить: добавочный номер бухгалтерии 1017.\n\n '
                         'Пожалуйста, не забывайте пояснять к какому вопросу правка (не просто 1017).')
        return

    if 'исправить' in message.text.lower():
        correct = "Пользователь {0.first_name} @{0.username} id{0.id} предлоджил правку:\n" \
                      .format(message.from_user, message.from_user, message.from_user) + message.text[10:]
        bot.send_message(message.chat.id, 'Ваша информация успешно отправлена. После ее рассмотрения будут внесены '
                                          'соответсвующие изменения. \n'
                                          'Большое спасибо за Ваше участие в улучшении Телеграм-Бота!',
                         reply_markup=general_menu())
        bot.send_message(157758328, correct)
        return

    if "добавить  информацию" in message.text.lower():  # TODO идея использовать метод словаря .setdefault() который будет добавлять ключ со значением в словарь при его отсутствии
        bot.send_message(message.chat.id,
                         # TODO либо создавать новый словарь и методом в питон 3.9  а|b сливать его с существующим
                         'Для добавления своей информации в телеграм-бот, начните свое сообщение со слова "предложить:". Например:\n\nПредложить: '
                         'номер телефона представителя в Москве 8(495)123-45-67', reply_markup=general_menu())
        return

    if 'предложить' in message.text.lower():
        correct = "Пользователь {0.first_name} @{0.username} id{0.id} предлоджил информацию:\n" \
                      .format(message.from_user, message.from_user, message.from_user) + message.text[11:]
        bot.send_message(message.chat.id, 'Ваша информация успешно отправлена. После ее рассмотрения будут внесены '
                                          'соответсвующие изменения. \n'
                                          'Большое спасибо за Ваше участие в улучшении Телеграм-Бота!',
                         reply_markup=general_menu())
        bot.send_message(157758328, correct)
        return

    if "ответ пользователю" in message.text.lower():
        # todo ОБНОВИ СЕРВЕР
        bot.send_message(user_id, message.text[18:], reply_markup=general_menu())
        bot.send_message(157758328, "Ответ пользователю отправлен успешно")
        found_result = True  # вопрос checking_answer() для строго соответсвия вынесен в конец скрипта

    if len(changed(message.text)) <= 2:
        bot.send_message(message.chat.id, 'Слишком короткий запрос. Пожалуйста, чуть подробнее, или измените запрос.',
                         reply_markup=general_menu())
        return

    if not found_result:  # СТРОГОЕ СООТВЕТСТВИЕ        # if можно заменить на while и засунуть всё в один try except
        for id in baza.dictionary:
            question = baza.dictionary[id]['question'].lower()
            if message.text.lower() in question:
                if 'скачать' in question:  # так надо 2 раза
                    download()  # TODO кнопки скачать и просмотреть не передаются через try except
                    found_result = True
                elif 'просмотреть' in question:  # так надо 2 раза
                    open()
                    found_result = True
                else:  # так надо 2 раза
                    try:
                        bot.send_message(message.chat.id, baza.dictionary[id]['answer'], reply_markup=general_menu(), # TODO если вешается бот то ругается на ключ answer в 260 строке
                                     parse_mode='Markdown')
                        bot.send_message(157758328,
                                     "1 - Информация выдана в строгом соответствии по запросу: " + message.text)
                    except Exception as exc:
                        bot.send_message(157758328,
                                         f"при запросе '{message.text}' при поиске в строгом соответствии возникала ошибка {type(exc).__name__} {exc} ")
                    found_result = True

    if not found_result:  # НЕСТРОГОЕ СООТВЕТСВИЕ
        try:
            found_result = find_non_strict_accordance(message)
        except Exception as exc:
            bot.send_message(157758328,
                             f"при запросе '{message.text}' в нестрогом соответсвии возникала ошибка {type(exc).__name__} {exc}")

    if not found_result:  # ИЩЕТ В ЛЮБОМ ПОРЯДКЕ В РАМКАХ ВОПРОСА
        try:
            found_result = find_in_random_order(message)
        except Exception as exc:
            # TODO придумать как изменить запрос (персетавить местами слова??) чтобы обойти ошибку
            bot.send_message(message.chat.id,
                             'Не удалось найти ответ. Попробуйте упростить свой запрос.',
                             reply_markup=general_menu(),
                             parse_mode='Markdown')
            bot.send_message(157758328, f"при запросе '{message.text}' при поиске в случайном порядке возникала ошибка {type(exc).__name__} {exc} ")
        # !!!!!! ЕСЛИ ВОЗНИКАЕТ ОШИБКА KEY ERROR то вместо квадратных скобок ключа словаря, лучше использовать .get('key')

    if not found_result:  # если ничего не найдено
        user_id = message.from_user.id
        message.text = "Пользователь {0.first_name} {0.last_name} @{0.username} id{0.id} не смог найти запрос:\n" \
                           .format(message.from_user, message.from_user, message.from_user,
                                   message.from_user) + message.text
        bot.send_message(157758328, message.text)
        bot.send_message(message.chat.id,
                         '{0.first_name}, я не знаю, что на это ответить. Попробуйте изменить или упростить свой запрос.\n\n'
                         'Ваш неудачный запрос уже направлен разработчику на рассмотрение, в ближайшее время он внесёт ответ на него.\n'
                         'Если у Вас появится какая-то информация на этот счёт - сообщите.\n'
                         '\n Если Вы заметите ошибки, устаревшую информцию '
                         'или обнаружите факты некорректной работы бота - просьба написать об этом также  '
                         'разработчику @DeveloperAzarov.\n'
                         'Либо Вы можете самостоятельно внести информацию в базу данных, нажав кнопку "Добавить информацию".'.format(
                             message.from_user, bot.get_me()), reply_markup=general_menu())
    # if found_result:  # две кнопки для списка ответов строгого соответствия
    #     checking_answer("Всё верно? Есть ошибки?")


# ReplyKeyboardMarkup - не привязывается к сообщению
# InlineKeyboardMarkup — Она привязывается к сообщению, с которым была отправлена.
# user_id = message.from_user.id - извлечение id пользователя
# bot.reply_to(message, message.text) - ответить переслав сообщение обратно
# print(message) # распечатывает всю информацию о написавшем человеке и историю сообщений в виде словаря
# print(message.text) # message.text - введенное сообщение
bot.polling(none_stop=True)  # запускает бота
