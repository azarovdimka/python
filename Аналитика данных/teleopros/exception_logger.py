import traceback
import time


def writer(exc, request, user_id, fio=None,
           answer=None):  # TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    file_path = "/exception_log/exception_log.txt"  # "/usr/local/bin/bot/exception_log/exception_log.txt" #
    datetime = time.strftime('%d.%m.%Y %H:%M')
    text_error = f"Пользователь: {user_id} {fio}\n" \
                 f"При запросе: {request}\n" \
                 f"Ответ пользователю: {answer}\n" \
                 f"Возникала ошибка: {type(exc).__name__} {exc} \n" \
                 f"Полный traceback:{traceback.format_exc()}\n\n"
    with open(file_path, 'r', encoding='utf-8') as writed_file:
        if text_error in writed_file:
            return
        else:
            with open(file_path, 'a', encoding='utf-8') as original:
                original.write(f"\n\n{datetime}\n" \
                               f"{text_error}")

# TODO НЕ ЗАБУДЬ ПОМЕНЯТЬ АДРЕС!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
