from random import random
from unittest import TestCase
from unittest.mock import patch, Mock, ANY

from vk_api.bot_longpoll import VkBotMessageEvent

from vk_bot import Bot  # для того чтобы теститровать какой-то скрипт, его нужно импортировать сюда в файл тестов


class Test1(TestCase):
    RAW_EVENT = {
        'type': 'message_new',
        'object': {'date': 1613126122, 'from_id': 939628, 'id': 41, 'out': 0, 'peer_id': 939628, 'text': 'привет',
                   'conversation_message_id': 41, 'fwd_messages': [], 'important': False, 'random_id': 0,
                   'attachments': [], 'is_hidden': False},
        'group_id': 202393641}

    def test_ok(self):
        count = 5
        obj = {'a': 1}
        events = [obj] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch(
                'vk_bot.vk_api.VkApi'):  # patch импортируется из Unittest - она принимает на вход адрес объекта, который ей нужно (пропатчить - замокать -- ??). Мок - не вызываться в реальности
            with patch('vk_bot.LongPoll',
                       return_value=long_poller_listen_mock):  # код который будет исполняться внутри патчей будет исполняться так как будто бы эти модули не были импортированы, а были просто моками
                bot = Bot('', '')  # чтобы пронаблюдать результат - создаем бота при новых условиях
                bot.on_event = Mock()
                bot.run()

                bot.on_event.assert_called()  # assert_called проверяет что on_event был вызван
                bot.on_event.assert_any_call(obj)

                assert bot.on_event.call_count == count

    def test_on_event(self):
        event = VkBotMessageEvent(raw=self.RAW_EVENT)

        send_mock = Mock()
        with patch(
                'vk_bot.vk_api.VkApi'):  # patch импортируется из Unittest - она принимает на вход адрес объекта, который ей нужно (пропатчить - замокать -- ??). Мок - не вызываться в реальности
            with patch('vk_bot.LongPoll'):
                bot = Bot('', '')
                bot.api = Mock()
                bot.api.messages.send = send_mock

                bot.on_event(event)

        send_mock.assert_called_once_with(
            message=self.RAW_EVENT['object']['text'],
            random_id=ANY,
            peer_id=self.RAW_EVENT['object']['peer_id']
        )
