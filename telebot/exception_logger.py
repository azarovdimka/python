import traceback
import time


def writer(exc, request, user_id, fio=None,
           answer=None):  # TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    file_path = "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\telebot\\exception_log\\exception_log.txt"  # "/usr/local/bin/bot/exception_log/exception_log.txt" #
    datetime = time.strftime('%d.%m.%Y %H:%M')

    with open(file_path, 'a', encoding='utf-8') as original:
        original.write(f"\n\n{datetime}\n"
                       f"Пользователь: {user_id} {fio}\n"
                       f"При запросе: {request}\n"
                       f"Ответ пользователю: {answer}\n"
                       f"Возникала ошибка: {type(exc).__name__} {exc} \n"
                       f"Полный traceback:{traceback.format_exc()}\n\n")

# TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
