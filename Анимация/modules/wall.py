# -*- coding: utf-8 -*-

# (цикл for)

import simple_draw as sd


# Нарисовать стену из кирпичей. Размер кирпича - 100х50
# Использовать вложенные циклы for


# Подсказки:
#  Для отрисовки кирпича использовать функцию rectangle
#  Алгоритм должен получиться приблизительно такой:
#
#   цикл по координате Y
#       вычисляем сдвиг ряда кирпичей
#       цикл координате X
#           вычисляем правый нижний и левый верхний углы кирпича
#           рисуем кирпич
def draw_wall():
    width = 100  # ширина кирпича
    height = 50  # высота кирпича
    y = 0  # начальная точка рисования снизу
    y1 = height  # высота кирпича
    for i in range(12):
        start_point = sd.get_point(0, y)
        end_point = sd.get_point(600, y)
        sd.line(start_point, end_point, width=4)  # рисует горизонтальную линию между рядами кирпичей
        if i % 2 == 0:  # если при делении в остатке ноль - кирпич рисовать от 0 по оси Х
            x1 = 0
            x2 = 0
            for _ in range(7):
                start_point = sd.get_point(x1, y)
                end_point = sd.get_point(x2, y + y1)
                sd.line(start_point, end_point, width=4)  # рисует вертикальную линию в каждом первом ряду снизу
                x1 += width
                x2 += width
        else:
            x1 = width / 2  # рисуем полкирпича
            x2 = width / 2
            for _ in range(6):
                start_point = sd.get_point(x1, y)
                end_point = sd.get_point(x2, y + y1)
                sd.line(start_point, end_point, width=4)  # рисует вертикальную линию в каждом втором ряду снизу
                x1 += width
                x2 += width
        y += height  # по окончании итерации увеличение высоты на height

    # sd.pause()

# зачет!
