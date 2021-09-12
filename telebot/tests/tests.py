from unittest import TestCase
import unittest
from testflightbot import *


# если возникли странные проблемы с импортом и тестами поставьте метку на lesson_014 - mark directory as - source root
# телефон бронирования - два слова стоящие в разных местах в вопросе при поиске 'телефон бронирования' в случайном порядке возникала ошибка ApiTelegramException A request to the Telegram API was unsuccessful. Error code: 400 Description: Bad Request: can't parse entities: Can't find end of the entity starting at byte offset 60

class TestBowling(TestCase):
    def setUp(self):
        self.bowling = Bowling()

    def test_strike(self):
        expected = 20
        actual = self.bowling.count_score("X")
        self.assertEqual(expected, actual[0])  # assertEqual сравнивает ожидаемое и передаваемое значение

    def test_spare(self):
        self.assertEqual(15, self.bowling.count_score("4/")[0])

    @unittest.expectedFailure
    def test_values(self):
        self.assertEqual(10, self.bowling.count_score("55")[0])


if __name__ == '__main__':
    unittest.main()
