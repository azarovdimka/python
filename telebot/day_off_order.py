import telebot  # чтобы работал telebot - удалить telebot, и установить Pytelegrambotapi, написанным оставить telebot
from telebot.types import InlineKeyboardMarkup
from telebot import types
import settings
import handler_db
from datetime import datetime, timedelta
import time
import pytz
import random

bot = telebot.TeleBot(settings.TOKEN)


def select_action():
    """Основаня клавиатура внизу экрана: выбор первичного дейсвтия заказать выходной, просмотреть свободные дни, отменить"""
    select_action = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Заказать\nвыходной')
    btn2 = types.KeyboardButton('Свободные\nдаты')
    btn3 = types.KeyboardButton('Отменить\nзаказ')
    btn4 = types.KeyboardButton('Выйти')

    select_action.add(btn1, btn2, btn3, btn4)
    return select_action


def yes_no(one_time_param):
    yes_no = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time_param)
    yes = types.KeyboardButton('Да')
    no = types.KeyboardButton('Нет')
    yes_no.add(yes, no)
    return yes_no


def position():
    position = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    sb = types.KeyboardButton('СБ')
    bs = types.KeyboardButton('BS')
    simple = types.KeyboardButton('БП')

    position.add(sb, bs, simple)
    return position


ask_order_or_cancel = "Вы хотите заказать выходной или отменить ранее заказанный выходной?"
ask_position = 'Укажите Вашу должность'
ask_date = 'На какую дату Вы бы хотели заказать выходной?'
ask_comment = 'Оставьте комментарий, для чего Вам нужен выходной?'


@bot.message_handler(content_types=["text"])
def order_day_procedure(message):
    def check_true_date(message):
        """Проверяет насколько корректно ввдена дата. Возвращает False Либо дату"""
        days = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31, }

        current_datetime = time.strftime('%d.%m.%Y %H:%M')
        dt_utc = datetime.strptime(current_datetime, '%d.%m.%Y %H:%M').replace(tzinfo=pytz.utc)
        dt = dt_utc.astimezone(pytz.utc) + timedelta(days=60)
        future_month = int(dt.month)
        future_year = str(dt.year)[2:]
        day = message.text

        if '.' in message.text:
            day = message.text.split('.')[0]
            requested_month = message.text.split('.')[1]
            if requested_month == '' or int(requested_month) != future_month:
                return False
        if '/' in message.text:
            day = message.text.split('/')[0]
        if ',' in message.text:
            day = message.text.split(',')[0]
        if len(day) < 2:
            day = '0' + day
        if not day.isdigit():
            return False
        if len(day) > 2 or 0 <= int(day) > 31:
            return False
        if int(day) > days[future_month]:
            return False
        else:
            if len(str(future_month)) < 2:
                future_month = '0' + str(future_month)
            return f'{day}.{future_month}.{future_year}'

    def check_true_position(message):
        """Проверяет правильность введеной позиции"""
        if message.text.lower() in "бортпроводник бп рядовой провод проводник":
            return "БП"
        if message.text.lower() in "бизнес класс бизнес-класс bs":
            return "BS"
        if message.text.lower() in "сб старший бортпроводник":
            return "СБ"

    def write_date(message):
        date = check_true_date(message)
        tab_number = handler_db.get_tab_number(message.chat.id)
        position = handler_db.get_position(tab_number)
        if position is None:
            return
        bot.send_message(157758328, "добрались сюда")
        # handler_db.update_date(date, tab_number, position)
        # TODO сообщать результат:
        #  - если на эту дату и должность есть свободные места, то внести заказ на эту дату
        #  - если на эту дату нет мест, то предложить свободные даты и снова вызывать функцию write_date с возможностью отмены кнопку отмена прикрепить
        # bot.register_next_step_handler(переменная_отправки_сообщения, след_функция)

    def finish(message):
        order_dict[message.chat.id]["Comment_4"] = f'{message.text} '.replace(';', '. ')
        bot.send_message(message.chat.id, '--')

        bp = f'--'
        feedback = f'{str(bp)};'
        for user_key, values in order_dict[message.chat.id].items():
            ch = "\n"
            feedback += f'{values.replace(ch, " ")};'

            return

    def start_31(message):
        pass

    def start_05(message):
        pass

    def start_20(message):
        """удаляет заказанные ранее выходные"""
        pass

    def start_04(message):
        """Проверяет дату на корректность, заносит дату в словарь, спрашивает комментарий ...."""
        date = check_true_position(message)
        tab_number = handler_db.get_tab_number(message.chat.id)
        position = order_dict[message.chat.id][ask_position]
        if date:
            order_dict[message.chat.id][ask_date] = date
            available = handler_db.check_free_place(date, tab_number, position)
            bot.send_message(message.chat.id, available)
            return
            # if available:
            #     pass
            # msg5 = bot.send_message(message.chat.id, ask_comment)
            # bot.register_next_step_handler(msg5, start_05)
        else:
            bot.send_message(message.chat.id, f'Введенная дата некорректна. Начните процедуру заново.')
            return

    def start_03(message):
        """Проверяет должность на корректность, заносит должность в две базы данных
        спрашивает желаемую дату"""
        message.text = check_true_position(message)
        order_dict[message.chat.id][ask_position] = message.text
        handler_db.update_position(message.chat.id, message.text)
        msg4 = bot.send_message(message.chat.id, ask_date, parse_mode='Markdown')
        bot.register_next_step_handler(msg4, start_04)

    def start_02(message):
        '''Выполняет соответсвующее от выбранного действия: либо спрашивает должность, либо выдает заранее заказанные выходные'''
        order_dict[message.chat.id][ask_order_or_cancel] = message.text
        if message.text.lower() in "заказать выходной заказать\nвыходной":
            msg2 = bot.send_message(message.chat.id, ask_position, reply_markup=position(), parse_mode='Markdown')
            bot.register_next_step_handler(msg2, start_03)
        if message.text.lower() in "отменить\nвыходной отменить выходной":
            order_dict[message.chat.id][ask_order_or_cancel] = message.text
            tab_number = handler_db.get_tab_number(message.chat.id)
            ordered_days = handler_db.get_ordered_days(tab_number)
            msg20 = bot.send_message(message.chat.id, f'Вот Ваши выходные, заказанные Вами ранее:\n {ordered_days}')
            bot.register_next_step_handler(msg20, start_20)
        if message.text.lower() in "выйти":
            return

    order_dict = {message.chat.id: {}}
    msg1 = bot.send_message(message.chat.id, ask_order_or_cancel, reply_markup=select_action())
    bot.register_next_step_handler(msg1, start_02)
