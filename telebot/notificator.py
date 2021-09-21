import getplan
import dict_users
import os


#
# def timer():
#     time.sleep()


def write_check_relevance(plan, chat_id):  # TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    file_path = "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\telebot\\plans\\plans" + str(
        chat_id) + ".txt"  # "/usr/local/bin/bot/plans/plans" + str(chat_id) + ".txt"
    #

    # если пароля у пользователя в словаре нет - то для него он не будет дальше проверять и функция закончится
    if dict_users.users[chat_id]['password'] == '' or not dict_users.users[chat_id]['plan_notify']:
        return None
    # если файла с планом ранее не существоало
    if not os.path.exists(file_path):
        # создаст файл и запищет в него план полученный через параметры без дополнительных сравнений и проверок
        with open(file_path, 'w', encoding='utf-8') as modified:
            modified.write(plan)
            return plan  # отправлять уведомление с новыми рейсами
    # если пароль в словаре есть и какой-то файл уже был
    else:
        # читает старый файл
        with open(file_path, 'r', encoding='utf-8') as original:
            old_file = original.read()

        with open(file_path, encoding='utf-8') as original:
            lines_old_file = original.readlines()  # преобразовали в список для будущего построчного сравнения
        # если имеющийся файл совпадает с полученными данными парсера
        if plan == old_file:
            return  # ничего не происходит, ничего не уведомляет # TODO быть может так что файлы равны, и программа не завершается, а интерпретатор продолжает читать код дальше и
        lines = []  # создание нового списка строк из файла без \n для корректного сравнения строк
        for i in lines_old_file:
            lines.append(i[:-1])  # убираем символ переноса каретки

        plan_list = plan.split('\n')  # создает из плана список чтобы можно было построчно сравнивать
        # если первая строка не совпадает и длина полученного плана меньше на одну строку:
        try:
            if lines[1] != plan_list[1] and (len(lines) - len(
                    plan_list) + 1 == 1):  # приходится плюсовать единицу, потому что при plan.split('\n') он бобавляет в конце еще одну пустую строку, так как в конце последней строки тоже стоит \n
                with open(file_path, 'w', encoding='utf-8') as modified:
                    modified.write(plan)  # изменения в файл запишет
                    return  # но уведомлять не будет если ночью просто прошел день, а соовтетсенно рейс отлетал, а нового ничего не появилось
        except Exception:  # todo попробовать перенести except в 42 строку чтобы witn open два раза не вызывать
            with open(file_path, 'w', encoding='utf-8') as modified:
                modified.write(plan)  # изменения в файл запишет

                return
        # если файлы не совпадают
        else:
            # перезаписывает файл полностью на новые данные
            with open(file_path, 'w', encoding='utf-8') as modified:
                modified.write(plan)
                return plan  # уведомит новым планом


# TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def notify(user_id):
    plan = getplan.parser(user_id)
    # plan не может сожержать None в результате работы функции getplan.parser
    # TODO если функция getplan.parser() будет прервана внутренним return ... может л
    if plan is not None:
        result = write_check_relevance(plan,
                                       user_id)  # TODO если эта функция возвращает None, то функция просто должна завершиться, но plan=None может послужить причиной исключения
        if result:
            # print(result)
            return result
        else:
            return

# notify(716423609)

# TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
