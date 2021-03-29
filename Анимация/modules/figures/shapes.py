# -*- coding: utf-8 -*-

import simple_draw as sd


# sd.resolution = (1000, 800)


def draw_triangle(point=sd.get_point(30, 200), length=100):
    sides = 3
    draw_figure(sides=sides, start_point=point, length=length)


def draw_square(point=sd.get_point(210, 185), length=100):
    sides = 4
    draw_figure(sides=sides, start_point=point, length=length)


def draw_figure(sides, start_point, length):
    point = start_point
    step = round(360 / sides)
    for angle in range(0, 360, step):
        side = sd.get_vector(start_point=point, angle=angle, width=3, length=length)
        point = side.end_point
        side.draw()

# draw_square()
# sd.pause()
