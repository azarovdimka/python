from unittest import TestCase
import unittest
from bowling import *


# если возникли странные проблемы с импортом и тестами поставьте метку на lesson_014 - mark directory as - source root


class TestBowling(TestCase):
    def setUp(self):
        self.bowling = Bowling()

    def test_strike(self):
        expected = 20
        actual = self.bowling.count_score("X")
        self.assertEqual(expected, actual[0])  # assertEqual сравнивает ожидаемое и передаваемое значение

    def test_spare(self):
        self.assertEqual(15, self.bowling.count_score("4/")[0])

    def test_spare_1(self):
        self.assertEqual(15, self.bowling.count_score("1/")[0])

    def test_spare_2(self):
        self.assertEqual(15, self.bowling.count_score("9/")[0])

    def test_spare_3(self):
        self.assertEqual(30, self.bowling.count_score("1/1/")[0])

    def test_spare_4(self):
        self.assertEqual(45, self.bowling.count_score("1/1/1/")[0])

    def test_strike_spare(self):
        self.assertEqual(35, self.bowling.count_score("X4/")[0])

    def test_strike_spare_1(self):
        self.assertEqual(35, self.bowling.count_score("4/X")[0])

    def test_minus(self):
        self.assertEqual(0, self.bowling.count_score("-")[0])

    def test_minus_1(self):
        self.assertEqual(1, self.bowling.count_score("-1")[0])

    def test_minus_2(self):
        self.assertEqual(1, self.bowling.count_score("1-")[0])

    def test_minus_3(self):
        self.assertEqual(2, self.bowling.count_score("1-1")[0])

    def test_numbers(self):
        self.assertEqual(1, self.bowling.count_score("1")[0])

    def test_numbers_1(self):
        self.assertEqual(2, self.bowling.count_score("11")[0])

    def test_valid_results(self):
        self.assertEqual(21, self.bowling.count_score("X-1")[0])

    def test_valid_results_1(self):
        self.assertEqual(36, self.bowling.count_score("X1/-1")[0])

    def test_valid_results_2(self):
        self.assertEqual(42, self.bowling.count_score("X4/34")[0])

    def test_valid_results_3(self):
        self.assertEqual(46, self.bowling.count_score("X4/34-4")[0])

    def test_valid_results_4(self):
        self.assertEqual(105, self.bowling.count_score("3532X332/3/62--62X")[0])

    def test_not_enough_frames(self):
        with self.assertRaises(WrongQuantityFrames) as exc:
            self.bowling.get_score("4/")
        self.assertEqual(str(exc.exception), 'Мало фреймов')

    def test_frames(self):
        with self.assertRaises(TooMuchSum):
            self.bowling.get_score("4/65X46--/89-/-5665/-")
            print("тест выполненнн")

    def test_value_error(self):
        with self.assertRaises(ValueError) as exc:
            self.bowling.count_score("Ь")

    def test_zeros(self):
        with self.assertRaises(CheckForZeros) as exc:  # а здесь ошибка не возникает вообще
            self.bowling.count_score("00")
            print("тест выполнен")

    def test_cant_start_slash(self):
        with self.assertRaises(CheckSlashError) as exc:
            self.bowling.count_score("/5")

    def test_strike_cant_be_second(self):
        with self.assertRaises(CheckStrikeError) as exc:
            self.bowling.count_score("5x")

    @unittest.expectedFailure
    def test_values(self):
        self.assertEqual(10, self.bowling.count_score("55")[0])


if __name__ == '__main__':
    unittest.main()
