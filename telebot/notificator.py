import exception_logger
import getplan
import os
import time


def write_check_relevance(plan, chat_id):
    # TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    file_path = "/usr/local/bin/bot/plans/plans" + str(chat_id) + ".txt"
    # file_path = "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\telebot\\plans\\plans" + str(chat_id) + ".txt" #   "/usr/local/bin/bot/plans/plans" + str(chat_id) + ".txt"

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

def notify(user_id, tab_number, password, autoconfirm, time_depart):
    """Извлекает план: вызывает функцию парсинга плана с сайта, проверяет план на новизну, если план новый, вызывает
    функцию записи плана, и возвращает уведомление для отправки нового плана"""
    plan = getplan.parser(user_id, tab_number, password, autoconfirm, time_depart)

    if plan is not None:
        # start_time = time.time()
        result = write_check_relevance(plan, user_id)
        # finish_time = time.time()
        # print(finish_time - start_time)
        if result:
            return result
        else:
            return
# TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# notify(512766466, '122411', 'Rabota6!', False, 'msk_start')  # шемякин
# notify(157758328, '119221', '2DH64rf2', True, 'msk_start')  # азаров
# notify(801093934, '5930', 'Voronova090879', False, 'msk_start')


# TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
