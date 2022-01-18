import exception_logger
import getplan
import os


def write_check_relevance(plan, chat_id, password,
                          plan_notify):  # TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    file_path = "/usr/local/bin/bot/plans/plans" + str(
        chat_id) + ".txt"  # "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\telebot\\plans\\plans" + str(chat_id) + ".txt" #   "/usr/local/bin/bot/plans/plans" + str(chat_id) + ".txt"
    #

    if (password == '' or not password or password == '0') or not plan_notify:
        return None

    if not os.path.exists(file_path):  # ПЛАН ВПЕРВЫЕ РАНЬШЕ НЕ БВЫЛО
        with open(file_path, 'w', encoding='utf-8') as modified:
            modified.write(plan)
            return plan

    else:
        with open(file_path, 'r', encoding='utf-8') as original:
            old_file = original.read()
        with open(file_path, encoding='utf-8') as original:
            lines_old_file = original.readlines()

        if plan == old_file:  # ПРИ ПРОВЕРКЕ ПЛАН НЕ ИЗМЕНИЛСЯ, АБСОЛЮТНО ИДЕНТИЧЕН
            return

        file_lines = []

        for i in lines_old_file:
            file_lines.append(i[:-1])  # убираем символ переноса каретки

        plan_list = plan.split('\n')  # создает из плана список чтобы можно было построчно сравнивать
        if len(plan_list) > 1:
            # del plan_list[-1]
            try:
                # todo сократить код ниже в 2 раза, сделать обратные условия чтобы сократить структуру if else

                # рядовая  ежедневная проверка, был блан вчера -> новый план для исключения [1] out of range при будущем сравнении первых строчек
                if len(plan_list) > 1 and len(file_lines) > 1:  # если это не: "рейсов не найдено"
                    # если просто слетал рейс, но нового рейса не поставили, запишет но не уведомит
                    # TODO ВСЁ РАВНО УВЕДОМЛЯЕТ, ЕСЛИ РЕЙС ОТЛЕТАЛ, НО НЕ УВЕДОМЛЯЕТ, ЕСЛИ ПОМЕНЯЛИ ПЕРВЫЙ РЕЙС И ДЛИНА ПЛАНА ОСТАЛАСТЬ ТА ЖЕ
                    if file_lines[1] != plan_list[1] and (len(file_lines) - len(plan_list) == 1):
                        with open(file_path, 'w', encoding='utf-8') as modified:
                            modified.write(plan)  # изменения в файл запишет
                            return  # но уведомлять не будет если ночью просто прошел день, а соовтетсенно рейс отлетал, а нового ничего не появилось
                    else:  # пришел план, а длина записаноого файла была == 1 (рейсов не найдено, отпуск)
                        with open(file_path, 'w', encoding='utf-8') as modified:
                            modified.write(plan)  # изменения в файл запишет
                            return plan  # уведомит потом новым планом
                else:  # при выходе из отпусков сработает это: рейсов не найдено -> план
                    with open(file_path, 'w', encoding='utf-8') as modified:
                        modified.write(plan)  # изменения в файл запишет
                        return plan  # уведомит потом новым планом

            except Exception as exc:  # todo попробовать перенести except в 42 строку чтобы witn open два раза не вызывать
                exception_logger.writer(exc=exc, request='сравнение старого и нового плана на предмет прошедшего рейса',
                                        fio=chat_id)
                return


# TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def notify(user_id, tab_number, password, autoconfirm, night_notify, time_depart):
    plan = getplan.parser(user_id, tab_number, password, autoconfirm, time_depart)
    # plan не может сожержать None в результате работы функции getplan.parser
    # TODO если функция getplan.parser() будет прервана внутренним return ... может л
    if plan is not None:
        result = write_check_relevance(plan, user_id, password,
                                       night_notify)  # TODO если эта функция возвращает None, то функция просто должна завершиться, но plan=None может послужить причиной исключения
        if result:
            return result
        else:
            return

# notify(512766466)

# TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
