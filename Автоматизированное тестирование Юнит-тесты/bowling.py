# -*- coding: utf-8 -*-

# Надо написать python-модуль (назвать bowling), предоставляющий API расчета количества очков:
# функцию get_score, принимающую параметр game_result. Функция должна выбрасывать исключения,
# когда game_result содержит некорректные данные. Использовать стандартные исключения по максимуму,
# если не хватает - создать свои.
# Обязательно написать тесты на этот модуль. Расположить в папке tests.

# файл bowling для хранения логики подсчёта очков
# в bowling размещать всё для реализации подсчёта (подобная логика была в 6 модуле, где функции мы записывали в "движок")


class WrongQuantityFrames(Exception):
    pass


class CheckForZeros(Exception):
    pass


class CheckSlashError(Exception):
    pass


class CheckStrikeError(Exception):
    pass


class TooMuchSum(Exception):
    pass


class Bowling:
    digit_list = []

    def count_score(self, game_result):
        scores = 0
        frames = 0
        i = -1
        while i < len(game_result) - 1:
            i += 1
            if game_result[i] == '/':
                raise CheckSlashError(f" / не может идти первым элементом фрейма")

            if '0' in game_result:
                raise CheckForZeros(f"Введена неправильные символы {game_result}. "
                                    f"ноль не может быть записан, т.к. пустой бросок должен записываться символом '-'")

            if game_result[i].isnumeric() and len(self.digit_list) < 2:
                self.digit_list.append(int(game_result[i]))
                if len(self.digit_list) == 2:
                    if sum(self.digit_list) > 9:
                        raise TooMuchSum(f"Введена неправильная последовательность символов {self.digit_list}"
                                         f", сумма чисел не может превышать 9, так как это получится Strike или Spare")
                    else:
                        self.digit_list.clear()

            if game_result[i].lower() == 'x':
                if frames != int(frames):
                    raise CheckStrikeError(f"strike (х) не может идти вторым после цифры")
                scores += 20
                frames += 1
                continue

            if i + 1 < len(game_result) and game_result[i + 1] == '/':
                self.digit_list.clear()
                scores += 15
                frames += 1
                i += 1
                continue

            if game_result[i] == '-':
                frames += 0.5
                continue

            if game_result[i].isnumeric():
                scores += int(game_result[i])
                frames += 0.5
                continue

            raise ValueError('Введены неправильные символы: ' + game_result[i])

        return scores, frames

    def get_score(self, game_result):
        scores, frames = self.count_score(game_result)
        print("frames", frames)
        if frames > 10:
            raise WrongQuantityFrames('Много фреймов')
            # у наследуемого класса exception есть аргумент message поэтому строку можно передавать напрямую
        if frames < 10:
            raise WrongQuantityFrames('Мало фреймов')
        return scores
