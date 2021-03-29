# -*- coding: utf-8 -*-

# (определение функций)

import simple_draw as sd


def draw_smile(point=sd.get_point(300, 300), color=sd.COLOR_WHITE):
    point = point
    sd.circle(center_position=point, radius=70, width=1, color=color)

    sd.circle(center_position=point, radius=50, width=0, color=color)
    point.y += 20
    point.x += 0
    sd.circle(center_position=point, radius=60, width=0, color=sd.background_color)
    point.y += 0
    point.x -= 20
    sd.circle(center_position=point, radius=20, width=0, color=color)
    point.y += 5
    point.x += 5
    sd.circle(center_position=point, radius=10, width=0, color=sd.COLOR_BLACK)
    point.y -= 5
    point.x += 30
    sd.circle(center_position=point, radius=25, width=0, color=sd.background_color)
    sd.circle(center_position=point, radius=20, width=0, color=color)
    point.y += 5
    point.x += 5
    sd.circle(center_position=point, radius=10, width=0, color=sd.COLOR_BLACK)
    point.y += 30
    point.x -= 60

    length = 100
    for angle in range(-5, 100, 12):
        length -= 12
        sd.vector(start=point, angle=angle, width=1, length=length, color=sd.COLOR_WHITE)

#
# draw_smile()
# #
# sd.pause()
