# !/usr/bin/env python3
import time
import telebot  # чтобы работал telebot - удалить telebot, и установить Pytelegrambotapi, написанным оставить telebot
from random import choice
import settings
import writer_user_to_txt

bot = telebot.TeleBot(settings.TOKEN)
bot.send_message(157758328, f"бот перезапущен")


file_path = "/usr/local/bin/roulette/users.txt"  # "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\roulette\\users.txt"  # "/usr/local/bin/roulette/users.txt"  # "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\roulette\\users.txt"  #
surnames_path = "/usr/local/bin/roulette/chosen_surnames.txt" # "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\roulette\\chosen_surnames.txt"  #   # "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\roulette\\chosen_surnames.txt"

## -*- coding: utf8 -*-

def check_chosen_surnames(chosen_surname):
    """Если фамилия есть в проверяемом списке - Выдаст True"""
    with open(surnames_path, 'r', encoding='utf-8') as checked_file:
        surnames_file = checked_file.read()
        if str(chosen_surname) in surnames_file:
            return True
        else:
            return False


def check_user(user_id):
    with open(file_path, 'r', encoding='utf-8') as old_file:
        users = old_file.read()
        if str(user_id) in users:
            return False
        else:
            return True


@bot.message_handler(commands=['start'])
def welcome(message):

    if check_user(message.chat.id):
        with open('static/AnimatedSticker.tgs', 'rb') as sti:
            bot.send_sticker(message.chat.id, sti)

        bot.send_message(message.chat.id, 'Добрый день! Близится Новый год! Так хочется порадовать друзей '
                                          'приятными подарками! Давайте устроим акцию «Тайный Дед Мороз»? И подарим друг '
                                          'другу новогоднее настроение. Пожалуйста, напишите свою фамилию.')
        return
    else:
        bot.send_message(message.chat.id, f'Вы уже ранее принимали участие в рулетке, и Вы уже спешите за подарком!..\n *** С наступающим Новым годом! **')
        return


@bot.message_handler(content_types=["text"])  #
def conversation(message):
    """Модуль для общения и взаимодействия с пользователем. Декоратор будет вызываться когда боту напишут текст."""

    list_participants = ['Артанина Ольга', 'Большакова Татьяна', 'Белогурова Ирина', 'Волошин Анатолий', 'Григурко Марина',
                         'Кириченко Ксения', 'Казанцев Евгений', 'Калугина Людмила', 'Иванова Татьяна', 'Артеменко Татьяна',
                         'Муштайкина Ольга', 'Парфенова Наталья', 'Волкова Лариса', 'Емец Роман', 'Галкова Елена',
                         'Сныткина Татьяна', 'Волчек Эдуард', 'Алексеев Руслан']
    participated_status = False

    if check_user(message.chat.id):
        for instr in list_participants:
            if message.text.capitalize() == instr.split()[0]:
                surname_from = message.text.capitalize()
                name_from = instr.split()[1]

                with open('static/giftSticker.tgs', 'rb') as sti:
                    bot.send_sticker(message.chat.id, sti)
                bot.send_message(message.chat.id, f"{name_from}, сейчас мы запустим рулетку и посмотрим, кто же от Вас получит подарок?")
                time.sleep(3.5)
                time_counter = 5
                while True:
                    if time_counter == 5:
                        a = bot.send_message(message.chat.id, f"{time_counter}")
                    if time_counter > 1:
                        time.sleep(1)
                        time_counter -= 1
                        bot.edit_message_text(chat_id=message.chat.id, message_id=a.message_id, text=str(time_counter))
                    else:
                        time.sleep(1)
                        bot.edit_message_text(chat_id=message.chat.id, message_id=a.message_id, text="Итак...")
                        time.sleep(1)
                        break

                counter = 30
                copy_chosen = None
                while True:
                    try:
                        chosen = choice(list_participants)
                        if chosen == copy_chosen:
                            continue
                        if counter == 35:
                            a = bot.send_message(message.chat.id, f"{chosen}")
                            time.sleep(1.6)
                            counter -= 1 # иначе он не зайдет в следующее условие
                        if 30 < counter < 35:
                            time.sleep(0.5)
                            counter -= 1
                            chosen = choice(list_participants)
                            bot.edit_message_text(chat_id=message.chat.id, message_id=a.message_id, text=chosen)
                        if 5 < counter <= 30:
                            time.sleep(0.3)
                            counter -= 1
                            chosen = choice(list_participants)
                            bot.edit_message_text(chat_id=message.chat.id, message_id=a.message_id, text=chosen)
                        if 3 < counter <= 5:
                            time.sleep(0.4)
                            counter -= 1
                            chosen = choice(list_participants)
                            bot.edit_message_text(chat_id=message.chat.id, message_id=a.message_id, text=chosen)
                        if 1 < counter <= 3:
                            time.sleep(0.5)
                            counter -= 1
                            chosen = choice(list_participants)
                            bot.edit_message_text(chat_id=message.chat.id, message_id=a.message_id, text=chosen)
                            time.sleep(1)

                        if counter == 1 and surname_from != chosen.split()[0] and not check_chosen_surnames(chosen):
                            bot.edit_message_text(chat_id=message.chat.id, message_id=a.message_id, text=f'{chosen}')
                            time.sleep(1)
                            bot.edit_message_text(chat_id=message.chat.id, message_id=a.message_id, text=f'*{chosen} ждет от Вас подарка с нетерпением!*', parse_mode='Markdown')
                            break
                        while counter == 1 and (surname_from == chosen.split()[0]) and not check_chosen_surnames(chosen):
                            chosen = choice(list_participants)
                            continue

                        copy_chosen = chosen
                    except Exception:
                        continue
                writer_user_to_txt.writer_user_id(message.chat.id, surname_from, chosen)
                participated_status = True
            else:
                continue
        if not participated_status:
            bot.send_message(message.chat.id,
                             f'К сожалению, у вас нет прав на игру в эту рулетку. С наступающим Новым годом!')
            return

    else:
        bot.send_message(message.chat.id, f'Вы уже ранее принимали участие в рулетке, и Вы уже спешите за подарком!..\n '
                                          f'*******************************\n'
                                          f'С наступающим Новым годом!')
        return
    return


bot.polling(none_stop=True)
