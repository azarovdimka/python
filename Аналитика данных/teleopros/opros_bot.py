# -*- coding: utf8 -*-
# !/usr/bin/env python3
import threading
import time
import traceback

import telebot  # чтобы работал telebot - удалить telebot, и установить Pytelegrambotapi, написанным оставить telebot
import random
from telebot import types
import settings
import writer
import writer_users

bot = telebot.TeleBot(settings.TOKEN)
bot.send_message(157758328, f"бот перезапущен")


def general_menu(one_time_param):
    general_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time_param)
    btn1 = types.KeyboardButton('Совершенно \nсогласен')
    btn2 = types.KeyboardButton('Согласен')
    btn3 = types.KeyboardButton('Скорее, \nсогласен')
    btn4 = types.KeyboardButton('Скорее, \nне согласен')
    btn5 = types.KeyboardButton('Не согласен')
    btn6 = types.KeyboardButton('Совершенно \nне согласен')  # InlineKeyBoard (callback_data='Внести информацию')
    general_menu.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return general_menu


def yes_no(one_time_param):
    yes_no = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time_param)
    yes = types.KeyboardButton('Да')
    no = types.KeyboardButton('Нет')
    yes_no.add(yes, no)
    return yes_no


def position():
    position = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    stinst = types.KeyboardButton('СИПБ')
    inst = types.KeyboardButton('ИПБ')
    sb = types.KeyboardButton('СБ')
    bs = types.KeyboardButton('BS')
    simple = types.KeyboardButton('БП')

    position.add(stinst, inst, sb, bs, simple)
    return position


def otdelenie():
    otdelenie = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    oke1 = types.KeyboardButton('1')
    oke2 = types.KeyboardButton('2')
    oke3 = types.KeyboardButton('3')
    oke4 = types.KeyboardButton('4')
    oke5 = types.KeyboardButton('5')
    ekb = types.KeyboardButton('ЕКБ')
    olsit = types.KeyboardButton('ОЛСиТ')
    okk = types.KeyboardButton('ОКК')
    otdelenie.add(oke1, oke2, oke3, oke4, oke5, ekb, olsit, okk)
    return otdelenie


answer01 = "*Укажите Ваш возраст*\n(двузначное число цифрами)"
answer02 = "*Сколько лет Вы работаете в компании?*\nУкажите стаж работы цифрами без слов. Если Вы работаете меньше года - укажите 0."
answer03 = "*Укажите Ваше отделение*"
answer04 = "*Укажите Вашу должность в компании*"

answer1 = '1. Думаю, что я получаю неплохую оплату за ту работу, которую я выполняю.'
answer2 = '2. В этой организации у меня практически нет шансов получить повышение.'
answer31 = '3.1 У меня исключительно толковый и грамотный руководитель (руководство ОКЭ в целом).'
make_sure = 'Хотели бы Вы пояснить свой ответ?'
answer32 = '3.2.Мой инструктор обладает профессиональными знаниями, всегда готов прийти на помощь.'
answer4 = '4. Меня не удовлетворяет система дополнительных выплат, существующая в этой организации.'
answer5 = '5. Когда я хорошо выполняю свою работу, я ощущаю признание и благодарность.'
answer6 = '6. Многие из наших правил и инструкций необходимо упростить для нормальной работы.'
answer7 = '7. Мне нравятся люди, с которыми я работаю.'
answer8 = '8. Иногда мне кажется, что моя работа не имеет никакого смысла, я нахожусь не на своем месте.'
answer9 = '9. В этой организации хорошо налажено информирование своих работников.'
answer10 = '10. Прибавки к зарплате очень незначительны и происходят редко.',
answer11 = '11. Те, кто хорошо справляются со своей работой, имеют реальные шансы на повышение.',
answer121 = '12.1 Мне не нравится то, как ко мне относится мой руководитель (руководство ОКЭ).',
answer122 = '12.2.Мне не нравится то, как ко мне относится мой инструктор.',
answer13 = '13. Дополнительные льготы и выплаты, которые мы здесь получаем, не хуже, чем в большинстве других организаций',
answer14 = '14. Я не вижу, чтобы то, что я делаю, хоть как-то ценилось.',
answer15 = '15. Мои попытки улучшить процесс работы не натыкаются на бюрократизм и проволочки.',
answer16 = '16. Многие из моих коллег грешат некомпетентностью.',
answer17 = '17. Мне интересно решать задачи, возникающие в моей работе.',
answer18 = '18. Мне неясны цели, которые перед собой ставит эта организация.',
answer19 = '19. Думаю, что меня недостаточно ценят в этой организации, судя по тому, сколько мне платят.',
answer20 = '20. Шансы продвинуться по карьерной лестнице здесь не хуже, чем в других местах.',
answer21 = '21. Мой руководитель проявляет мало интереса к чувствам своих подчиненных.',
answer22 = '22. Наша организация обеспечивает хороший социальный пакет.',
answer23 = '23. У нас почти не получают материальных вознаграждений за хорошую работу.',
answer24 = '24. Мне приходится выполнять массу формальных и ненужных вещей.',
answer25 = '25. Я получаю удовольствие от работы со своими коллегами.',
answer26 = '26. Мне часто кажется, что я не знаю, что происходит в нашей организации',
answer27 = '27. Я горжусь работой, которую выполняю.',
answer28 = '28. Я удовлетворен возможностями на повышение зарплаты.',
answer29 = '29. Мы не имеем того социального пакета, который должны были бы иметь.',
answer301 = '30.1 Мне очень нравится мой руководитель (руководство ОКЭ).',
answer302 = '30.2 Мне очень нравится мой инструктор.',
answer310 = '31. Моя работа перегружена писаниной.',
answer320 = '32. Я не чувствую, чтобы мои усилия оценивались так, как они того заслуживают.',
answer33 = '33. Если я захочу, у меня есть реальные возможности продвинуться по службе.',
answer34 = '34. Мне очень нравится атмосфера нашего коллектива.',
answer35 = '35. Я получаю удовольствие от этой работы.',
answer36 = '36. Меня не удовлетворяет уровень информирования работников в нашей компании.',
answer37 = '37. У меня есть ярковыраженное желание уволиться хоть завтра.'
answer38 = '38. Я настолько конкурентоспособен, что смогу хорошо зарабатывать в другой компании или в другой отрасли.'
answer39 = '39. Я бы предпочел больше летать по ночам.'
answer40 = '40. Я уже так от всего устал, что часов 40 в месяц мне достаточно.'
answer41 = '41. Я хочу летать чем больше, тем лучше.'
answer42 = '42. Я считаю, что нужно обязательно учитывать знание иностранных языков при планировании рейсов за границу.'
answer43 = '43. Я настолько доверяю руководству, что готов с ними делиться своими проблемами и чаяниями.'
answer44 = '44. Руководству не нужно прислушиваться к мнению работников, иначе оно потеряет авторитет.'
answer45 = '45. Испытываете ли Вы проблемы с планированием и налётом?'
answer46 = "46. Мое семейное положение не позволяет летать в командировки / эстафеты. Я бы отказался от командировок, пусть и налет будет меньше."
answer47 = 'Есть ли у Вас предложения по работе, жалобы на кого-либо, важная информация, которую Вы считаете необходимо анонимно довести до руководства?'


def check_user_participation(message):
    """Проверяет, участвоал ли пользователь в опросе ранее."""
    file_path = "/usr/local/bin/teleopros/users.txt"  # "/usr/local/bin/teleopros/users.txt"
    with open(file_path, 'r', encoding='utf-8') as original:
        users = original.read()
        if message.chat.id != 157758328 and str(message.chat.id) in users:
            bot.send_message(message.chat.id,
                             f'Уважаемый бортпроводник! Вы уже проходили этот опрос ранее. Повторное прохождение вопроса невозможно.')
            return True
        else:
            return False


@bot.message_handler(commands=['start'])
def welcome(message):
    """При первом подключении пользователя к боту - выводит приветсвенный текст."""
    bot.send_message(message.chat.id, f'Проведение исследования уже завершено. \n\n '
                                      f'Участие приняло 619 человек. \n Из них 189 человек оставили жалобы и предложения\n '
                                      f'Информации получено очень много.'
                                      f'Все результаты переданы руководству. \n\n')
    return

    # if check_user_participation(message):
    #     return

    # if not check_user_participation(message):
    # bot.send_message(message.chat.id, "Прохождение опроса будет доступно с 7:00 утра.", parse_mode='Markdown')
    # return

    answer_dict = {}
    answer_dict[message.chat.id] = {}

    # bot.send_message(message.chat.id, f'\t    *Уважаемый коллега!*\n'
    #                                   f'\t    Мы очень хотим узнать Ваше мнение о работе в компании. Этот опрос очень '
    #                                   f'важен, он абсолютно анонимный, займет до 30 минут Вашего времени. Нам важно '
    #                                   f'получить искренние ответы на 46 вопросов. \n'
    #                                   f'\t    Ваши персональные данные (ФИО, табельный номер) не будут запрашиваться. '
    #                                   f'Опрос устроен таким образом, что и данные Вашего аккаунта не будут сохраняться '
    #                                   f'на сервере. Но кое-что все же нужно будет указать, например: возраст, отделение, '
    #                                   f'стаж работы, должность в экипаже и т.д. Но это нужно только для анализа полученных '
    #                                   f'ответов.\n'
    #                                   f'\t    Руководству компании будут переданы итоговые обезличенные результаты аналитического '
    #                                   f'исследования по всем сотрудникам для дальнейшего принятия решений, чтобы сделать '
    #                                   f'нашу работу в компании максимально интересной, комфортной, способствующей '
    #                                   f'личностному и профессиональному развитию. Давайте вместе меняться к лучшему!', parse_mode='Markdown')

    def replace_first_order(message):
        """Преобразовывает слова в баллы для правильного подсчета результатов.
        Функция применяется ко всем нечетным вопросам"""
        if "Совершенно \nсогласен" in message.text or "Совершенно согласен" in message.text:
            return "6"
        if "Согласен" in message.text:
            return "5"
        if "Скорее, \nсогласен" in message.text or "Скорее всего, согласен" in message.text or "Наверно" in message.text:
            return "4"
        if "Скорее, \nне согласен" in message.text:
            return "3"
        if "Не согласен" in message.text:
            return "2"
        if "Совершенно \nне согласен" in message.text:
            return "1"
        if "нет" in message.text.lower():
            bot.send_message(message.chat.id,
                             'В следующий раз Вам необходимо нажать на один из предложенных вариантов ниже.',
                             reply_markup=general_menu(one_time_param=True))
            return "2"
        if "да" in message.text.lower():
            bot.send_message(message.chat.id,
                             'В следующий раз Вам необходимо нажать на один из предложенных вариантов ниже.',
                             reply_markup=general_menu(one_time_param=True))
            return "5"
        if "start" in message.text:
            return "3"
        if "не знаю" in message.text.lower():
            bot.send_message(message.chat.id,
                             'В следующий раз Вам необходимо нажать на один из предложенных вариантов ниже.',
                             reply_markup=general_menu(one_time_param=True))
            return "3"
        else:
            bot.send_message(message.chat.id,
                             'В следующий раз Вам необходимо нажать на один из предложенных вариантов ниже.',
                             reply_markup=general_menu(one_time_param=True))
            return '3'

    def replace_reverse_order(message):
        """Преобразовывает слова в баллы в обратном порядке для правильного подсчета результатов
        Ответы на вопросы 2, 4, 6, 8, 10, 12, 14, 16, 18, 19, 21, 23, 24, 26, 29, 31, 32 и 36-й следует перевести в обратные,"""
        if "Совершенно \nсогласен" in message.text or "Совершенно согласен" in message.text:
            return "1"
        if "Согласен" in message.text:
            return "2"
        if "Скорее, \nсогласен" in message.text or "Скорее,согласен" in message.text or "Скорее всего, согласен" in message.text or "Наверно" in message.text:
            return "3"
        if "Скорее, \nне согласен" in message.text:
            return "4"
        if "Не согласен" in message.text:
            return "5"
        if "Совершенно \nне согласен" in message.text:
            return "6"
        if "да" in message.text.lower():
            bot.send_message(message.chat.id,
                             'В следующий раз Вам необходимо нажать на один из предложенных вариантов ниже.',
                             reply_markup=general_menu(one_time_param=True))
            return "2"
        if "start" in message.text:
            return "3"
        if "нет" in message.text.lower():
            bot.send_message(message.chat.id,
                             'В следующий раз Вам необходимо нажать на один из предложенных вариантов ниже.',
                             reply_markup=general_menu(one_time_param=True))
            return "5"
        if "не знаю" in message.text.lower():
            return "3"
        else:
            bot.send_message(message.chat.id,
                             'В следующий раз Вам необходимо нажать на один из предложенных вариантов ниже.',
                             reply_markup=general_menu(one_time_param=True))
            return '3'

    def filter_position(message):
        if "старший бортпроводник" in message.text.lower():
            return "СБ"
        if "бортпроводник" in message.text.lower():
            return "БП"
        if "инструктор" in message.text.lower():
            return "ИПБ"
        if "бизнес" in message.text.lower():
            return "BS"
        else:
            return message.text

    def binary_answer(message):
        """Преобразовывает полученные отыветы да / нет в 0 и 1"""
        if "да" in message.text.lower() or "Наверно" in message.text or "Согласен" in message.text or "Согласна" in message.text:
            return "1"
        if "нет" in message.text.lower() or "Не согласен" in message.text or "." in message.text:
            return "0"
        if "Не согласен" in message.text:
            return "0"
        if "Не знаю" in message.text:
            return "0"
        if "start" in message.text:
            return "0"
        else:
            return message.text

    def any_coma(message):
        """если возраст указали дробным числом - возмет только целую часть"""
        if "," in message.text:
            return message.text.split()[0]
        else:
            return message.text

    def finish(message):
        message.text = binary_answer(message)
        answer_dict[message.chat.id]["Comment_4"] = f'{message.text} '.replace(';', '. ')
        bot.send_message(message.chat.id,
                         'Уважаемый бортпроводник, опрос завершён! Спасибо Вам за уделенное время. Желаем Вам хорошего дня!')

        bp = f'{random.randint(1, 5000000)}'
        feedback = f'{str(bp)};'
        for user_key, values in answer_dict[message.chat.id].items():
            ch = "\n"
            feedback += f'{values.replace(ch, " ")};'

        feedback = feedback[:-1]
        writer.writer(feedback)

        writer_users.writer(message.chat.id)
        bot.send_message(157758328, f'Бортпроводник # {bp} \n оставил обратную связь: \n{feedback}')
        return

    def complains_handler(message):
        if "нет" in message.text.lower():
            answer_dict[message.chat.id]["жалоба"] = '0'
            answer_dict[message.chat.id]["Comment_4"] = '0'
            bot.send_message(message.chat.id, 'Все Ваши ответы бережно записаны и будут переданы в добрые руки.')
            finish(message)
            return
        if "да" in message.text.lower():
            answer_dict[message.chat.id]["жалоба"] = '1'
            msg88 = bot.send_message(message.chat.id,
                                     "Пожалуйста, поделитесь информацией коротко, но обоснованно и конструктивно.")
            bot.register_next_step_handler(msg88, finish)
            return
        else:
            answer_dict[message.chat.id]["жалоба"] = '1'
            answer_dict[message.chat.id]["Comment_4"] = f'{message.text} '.replace(';', '. ')
            bot.send_message(message.chat.id, 'Все Ваши ответы бережно записаны и будут переданы в добрые руки.')
            finish(message)
            return

    def start_47(message):
        message.text = binary_answer(message)
        answer_dict[message.chat.id][answer46] = message.text.replace(';', '. ')
        msga47 = bot.send_message(message.chat.id, answer47, reply_markup=yes_no(True))
        bot.register_next_step_handler(msga47, complains_handler)

    def comment_nalet_45(message):
        answer_dict[message.chat.id]["com_nal"] = f'{message.text} '.replace(';', '. ')
        msga46 = bot.send_message(message.chat.id, answer46, reply_markup=yes_no(False))
        bot.register_next_step_handler(msga46, start_47)

    def nalet_handler(message):
        if "нет" in message.text.lower():
            answer_dict[message.chat.id][answer45] = '0'
            answer_dict[message.chat.id]["com_nal"] = '0'
            msgansw46 = bot.send_message(message.chat.id, answer46, reply_markup=yes_no(False))
            bot.register_next_step_handler(msgansw46, start_47)
            return
        if "да" in message.text.lower():
            answer_dict[message.chat.id][answer45] = '1'
            msg4444 = bot.send_message(message.chat.id,
                                       "Пожалуйста, поделитесь информацией коротко, но обоснованно и конструктивно.")
            bot.register_next_step_handler(msg4444, comment_nalet_45)
            return
        else:
            answer_dict[message.chat.id][answer45] = "1"
            answer_dict[message.chat.id]["com_nal"] = f'{message.text} '.replace(';', '. ')
            msga46 = bot.send_message(message.chat.id, answer46, reply_markup=yes_no(False))
            bot.register_next_step_handler(msga46, start_47)
            return

    def start_45(message):
        message.text = binary_answer(message)
        answer_dict[message.chat.id][answer44] = message.text
        msga45 = bot.send_message(message.chat.id, answer45, reply_markup=yes_no(True))
        bot.register_next_step_handler(msga45, nalet_handler)

    def start_44(message):
        message.text = binary_answer(message)
        answer_dict[message.chat.id][answer43] = message.text
        msga44 = bot.send_message(message.chat.id, answer44, reply_markup=yes_no(False))
        bot.register_next_step_handler(msga44, start_45)

    def start_43(message):
        message.text = binary_answer(message)
        answer_dict[message.chat.id][answer42] = message.text
        msga43 = bot.send_message(message.chat.id, answer43, reply_markup=yes_no(False))
        bot.register_next_step_handler(msga43, start_44)

    def start_42(message):
        message.text = binary_answer(message)
        answer_dict[message.chat.id][answer41] = message.text
        msga42 = bot.send_message(message.chat.id, answer42, reply_markup=yes_no(False))
        bot.register_next_step_handler(msga42, start_43)

    def start_41(message):
        message.text = binary_answer(message)
        answer_dict[message.chat.id][answer40] = message.text
        msga41 = bot.send_message(message.chat.id, answer41, reply_markup=yes_no(False))
        bot.register_next_step_handler(msga41, start_42)

    def start_40(message):
        message.text = binary_answer(message, )
        answer_dict[message.chat.id][answer39] = message.text
        msga40 = bot.send_message(message.chat.id, answer40, reply_markup=yes_no(False))
        bot.register_next_step_handler(msga40, start_41)

    def start_39(message):
        message.text = binary_answer(message)
        answer_dict[message.chat.id][answer38] = message.text
        msga39 = bot.send_message(message.chat.id, answer39, reply_markup=yes_no(False))
        bot.register_next_step_handler(msga39, start_40)

    def start_38(message):
        message.text = binary_answer(message)
        answer_dict[message.chat.id][answer37] = message.text
        msga38 = bot.send_message(message.chat.id, answer38, reply_markup=yes_no(False))
        bot.register_next_step_handler(msga38, start_39)

    def start_37(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer36] = message.text
        msga37 = bot.send_message(message.chat.id, answer37, reply_markup=yes_no(False))
        bot.register_next_step_handler(msga37, start_38)

    def start_36(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer35] = message.text
        msga36 = bot.send_message(message.chat.id, answer36, reply_markup=general_menu(one_time_param=True))
        bot.register_next_step_handler(msga36, start_37)

    def start_35(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer34] = message.text
        msga35 = bot.send_message(message.chat.id, answer35, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga35, start_36)

    def start_34(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer33] = message.text
        msga34 = bot.send_message(message.chat.id, answer34, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga34, start_35)

    def start_33(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer320] = message.text
        msga33 = bot.send_message(message.chat.id, answer33, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga33, start_34)

    def start_320(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer310] = message.text
        msga320 = bot.send_message(message.chat.id, answer320, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga320, start_33)

    def start_310(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer302] = message.text
        msga310 = bot.send_message(message.chat.id, answer310, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga310, start_320)

    def start_302(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer301] = message.text
        msga302 = bot.send_message(message.chat.id, answer302, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga302, start_310)

    def start_301(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer29] = message.text
        msga301 = bot.send_message(message.chat.id, answer301, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga301, start_302)

    def start_29(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer28] = message.text
        msga29 = bot.send_message(message.chat.id, answer29, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga29, start_301)

    def start_28(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer27] = message.text
        msga28 = bot.send_message(message.chat.id, answer28, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga28, start_29)

    def start_27(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer26] = message.text
        msga27 = bot.send_message(message.chat.id, answer27, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga27, start_28)

    def start_26(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer25] = message.text
        msga26 = bot.send_message(message.chat.id, answer26, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga26, start_27)

    def start_25(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer24] = message.text
        msga25 = bot.send_message(message.chat.id, answer25, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga25, start_26)

    def start_24(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer23] = message.text
        msga24 = bot.send_message(message.chat.id, answer24, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga24, start_25)

    def start_23(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer22] = message.text
        msga23 = bot.send_message(message.chat.id, answer23, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga23, start_24)

    def start_22(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer21] = message.text
        msga22 = bot.send_message(message.chat.id, answer22, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga22, start_23)

    def start_21(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer20] = message.text
        msga21 = bot.send_message(message.chat.id, answer21, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga21, start_22)

    def start_20(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer19] = message.text
        msga20 = bot.send_message(message.chat.id, answer20, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga20, start_21)

    def start_19(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer18] = message.text
        msga19 = bot.send_message(message.chat.id, answer19, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga19, start_20)

    def start_18(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer17] = message.text
        msga18 = bot.send_message(message.chat.id, answer18, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga18, start_19)

    def start_17(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer16] = message.text
        msga17 = bot.send_message(message.chat.id, answer17, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga17, start_18)

    def start_16(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer15] = message.text
        msga16 = bot.send_message(message.chat.id, answer16, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga16, start_17)

    def start_15(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer14] = message.text
        msga15 = bot.send_message(message.chat.id, answer15, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga15, start_16)

    def start_14(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer13] = message.text
        msga14 = bot.send_message(message.chat.id, answer14, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga14, start_15)

    def start_13(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer122] = message.text
        msga13 = bot.send_message(message.chat.id, answer13, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga13, start_14)

    def start_122(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer121] = message.text
        msga122 = bot.send_message(message.chat.id, answer122, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga122, start_13)

    def start_121(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer11] = message.text
        msga121 = bot.send_message(message.chat.id, answer121, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga121, start_122)

    def start_11(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer10] = message.text
        msga11 = bot.send_message(message.chat.id, answer11, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga11, start_121)

    def start_10(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer9] = message.text
        msga10 = bot.send_message(message.chat.id, answer10, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga10, start_11)

    def start_9(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer8] = message.text
        msga9 = bot.send_message(message.chat.id, answer9, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga9, start_10)

    def start_8(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer7] = message.text
        msga8 = bot.send_message(message.chat.id, answer8, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga8, start_9)

    def start_7(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer6] = message.text
        msga7 = bot.send_message(message.chat.id, answer7, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga7, start_8)

    def start_6(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer5] = message.text
        msga6 = bot.send_message(message.chat.id, answer6, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga6, start_7)

    def start_5(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer4] = message.text
        msga5 = bot.send_message(message.chat.id, answer5, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga5, start_6)

    def start_comment_32(message):
        answer_dict[message.chat.id]["Comment_2"] = f'{message.text} '
        msg = bot.send_message(message.chat.id, answer4, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msg, start_5)

    def buttons_comment_32(message):
        if "нет" in message.text.lower():
            message.text = binary_answer(message)
            answer_dict[message.chat.id]["Наличие комментария к инструктору"] = '0'
            answer_dict[message.chat.id]["Comment_2"] = "0"
            msgans4 = bot.send_message(message.chat.id, answer4, reply_markup=general_menu(one_time_param=False))
            bot.register_next_step_handler(msgans4, start_5)
            return
        if "да" in message.text.lower():
            message.text = binary_answer(message)
            answer_dict[message.chat.id]["Наличие комментария к инструктору"] = '1'
            msgsc32 = bot.send_message(message.chat.id, "Пожалуйста, поясните свой ответ.")
            bot.register_next_step_handler(msgsc32, start_comment_32)
            return
        else:
            answer_dict[message.chat.id]["Наличие комментария к инструктору"] = "1"
            answer_dict[message.chat.id]["Comment_2"] = f'{message.text} '.replace(';', '. ')
            msga4 = bot.send_message(message.chat.id, answer4, reply_markup=general_menu(one_time_param=False))
            bot.register_next_step_handler(msga4, start_5)
            return

    def handler_32(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer32] = message.text.replace(';', '. ')
        msgms32 = bot.send_message(message.chat.id, make_sure, reply_markup=yes_no(True))
        bot.register_next_step_handler(msgms32, buttons_comment_32)

    def start_comment_31(message):
        answer_dict[message.chat.id]["Comment_1"] = f'{message.text} '.replace(';', '. ')
        msgans32 = bot.send_message(message.chat.id, answer32, reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msgans32, handler_32)

    def buttons_comment_31(message):
        if "нет" in message.text.lower():
            answer_dict[message.chat.id]["Наличие комментария к руководству"] = '0'
            answer_dict[message.chat.id]["Comment_1"] = "0"
            msgan32 = bot.send_message(message.chat.id, answer32, reply_markup=general_menu(one_time_param=False))
            bot.register_next_step_handler(msgan32, handler_32)
            return
        if "да" in message.text.lower():
            answer_dict[message.chat.id]["Наличие комментария к руководству"] = "1"
            msgc31 = bot.send_message(message.chat.id, "Пожалуйста, поясните свой ответ.")
            bot.register_next_step_handler(msgc31, start_comment_31)
            return
        else:
            answer_dict[message.chat.id]["Наличие комментария к руководству"] = "1"
            answer_dict[message.chat.id]["Comment_1"] = f'{message.text} '.replace(';', '. ')
            msga32 = bot.send_message(message.chat.id, answer32, reply_markup=general_menu(one_time_param=False))
            bot.register_next_step_handler(msga32, handler_32)
            return

    def handler_31(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer31] = message.text
        msgms31 = bot.send_message(message.chat.id, make_sure, reply_markup=yes_no(True))
        bot.register_next_step_handler(msgms31, buttons_comment_31)

    def start_31(message):
        message.text = replace_reverse_order(message)
        answer_dict[message.chat.id][answer2] = message.text
        msga31 = bot.send_message(message.chat.id, answer31, parse_mode='Markdown',
                                  reply_markup=general_menu(one_time_param=True))
        bot.register_next_step_handler(msga31, handler_31)

    def start_2(message):
        message.text = replace_first_order(message)
        answer_dict[message.chat.id][answer1] = message.text
        msga2 = bot.send_message(message.chat.id, answer2, parse_mode='Markdown',
                                 reply_markup=general_menu(one_time_param=False))
        bot.register_next_step_handler(msga2, start_31)

    def start_04(message):
        message.text = filter_position(message)
        answer_dict[message.chat.id][answer04] = message.text
        msga1 = bot.send_message(message.chat.id, answer1, reply_markup=general_menu(one_time_param=False),
                                 parse_mode='Markdown')
        bot.send_message(message.chat.id, f'Вам необходимо выбирать один из вариантов предложенных ниже.')
        bot.register_next_step_handler(msga1, start_2)

    def start_03(message):
        answer_dict[message.chat.id][answer03] = message.text
        msg4 = bot.send_message(message.chat.id, answer04, reply_markup=position(), parse_mode='Markdown')
        bot.register_next_step_handler(msg4, start_04)

    def start_02(message):
        message.text = any_coma(message)
        answer_dict[message.chat.id][answer02] = message.text
        msg3 = bot.send_message(message.chat.id, answer03, reply_markup=otdelenie(), parse_mode='Markdown')
        bot.register_next_step_handler(msg3, start_03)

    def start_01(message):
        answer_dict[message.chat.id][answer01] = message.text
        msg2 = bot.send_message(message.chat.id, answer02, parse_mode='Markdown')
        bot.register_next_step_handler(msg2, start_02)

    msg1 = bot.send_message(message.chat.id, answer01, parse_mode='Markdown')
    bot.register_next_step_handler(msg1, start_01)


bot.polling(none_stop=True)
