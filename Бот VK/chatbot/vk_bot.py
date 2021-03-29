#!/usr/bin/env python3
try:
    import settings
except ImportError:
    exit('DO cp settings.py.default settings.py and set token')

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll as LongPoll, VkBotEventType as EventType
import random
import logging

# ДЗ 10.02.2021 15:26

log = logging.getLogger('bot')  # создаем объект логгера и задаем ему имя


def configure_logging():
    stream_handler = logging.StreamHandler()  # создаём консольный handler посылает сообщения в консоль
    stream_handler.setFormatter(logging.Formatter(
        "%(levelname)s %(message)s"))  # asctime время, levelname - уровень логирования, message - само сообщение
    stream_handler.setLevel(
        logging.INFO)  # setLevel приоритетный. запретили логирование уровня debug # отдельно устанавливать уровень для хедлера и для лога не обязательно, будет срабатывать более жесткое правило (levelname)
    log.addHandler(stream_handler)  # этот хедлер нужно добавить к нашему объекту

    file_handler = logging.FileHandler("bot_log.txt",
                                       encoding='utf-8')  # будет щаписывать в файл # delay - отложить создание файла до первого вызова
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s",
                                                datefmt='%d.%m.%Y, %H:%M'))  # datefmt отвечает за форматирование даты и времени
    file_handler.setLevel(logging.DEBUG)  # setLevel приоритетный. хотим видеть и с уровнем дебаг тоже
    log.addHandler(file_handler)

    log.setLevel(
        logging.DEBUG)  # основной логер и установка уровня для основного логера включили логирование всех сообщений
    # logging.CRITICAL
    # logging.ERROR
    # Logging.INFO
    # logging.DEBUG # необходимо установить уровень логирования: Чем ниже степень важности - попадать в логи не будут/ Если выбрать уровень critical - попадут все сообщения


# принты необходибо заменить на log.debug()

class Bot:
    """
    Echo bot for vk.com.
    Use Python3.7
    """

    def __init__(self, group_id, token):
        """
        :param group_id: group id из группы вконтакте
        :param token: секретный токен
        """
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = LongPoll(self.vk, self.group_id)  # ходит в контакт и реально что-то делает
        self.api = self.vk.get_api()

    def run(self):
        """Запуск бота."""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception(
                    "ошибка в обработке события")  # сообщение будет залогировано с уровнем error: основная и дополнительная информация об исключении из охватывающего кода с номерами строк и стеком вызовов

    def on_event(self, event):
        """Отправляет сообщение назад, если это сообщение текстовое
        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type == EventType.MESSAGE_NEW:
            log.debug(
                'отработка уровня логирования: отправляем сообщение обратно')  # Info чтобы видеть как уровни логирвоания срабатывают
            self.api.messages.send(message='привет',
                                   # 'Я тебя понял, да  ' + event.object.text.lower() + ', приём? Что дальше?',
                                   random_id=random.randint(0, 2 ** 20),
                                   peer_id=event.object.peer_id)
        else:
            log.info("мы пока не умеем обрабатывать события такого типа %s",
                     event.type)  # %s куда вставлять переменную (типа {var}) %10s - 10 пробелов
            # raise ValueError('неизвестное сообщение') стандартный вызов исключения который будет залогирован
            # log.debug - опредлеили конкретный уровень логирования в этом месте


if __name__ == '__main__':
    configure_logging()
    bot = Bot(settings.GROUP_ID, settings.TOKEN)
    bot.run()
