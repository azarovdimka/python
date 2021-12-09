import traceback
import time


def writer(exc, request, fio=None, answer=None):  # TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!
    file_path = "/usr/local/bin/bot/exception_log/exception_log.txt"  # "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\telebot\\exception_log\\exception_log.txt"  #  "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\telebot\\exception_log\\exception_log.txt"  #
    datetime = time.strftime('%d.%m.%Y %H:%M')
    text_error = f"Пользователь: {fio}\n" \
                 f"При запросе: {request}\n" \
                 f"Ответ пользователю: {answer}\n" \
                 f"Возникала ошибка: {type(exc).__name__} {exc} \n" \
                 f"Полный traceback:{traceback.format_exc()}\n\n"
    with open(file_path, 'r', encoding='utf-8') as old_file:
        old_file = old_file.read()
        if text_error in old_file:
            return
        else:
            with open(file_path, 'a', encoding='utf-8') as new_data:
                new_data.write(f"\n\n{datetime}\n" \
                               f"{text_error}")
                return "!!! Внесена запись о возникшей ошибке в лог ошибок"

# TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
