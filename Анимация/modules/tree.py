# -*- coding: utf-8 -*-
import simple_draw as sd


def draw_branches(point=sd.get_point(300, 30), angle=90, length=100, width=10):
    if length < 10:
        return
    branch = sd.get_vector(point, angle, length, width)
    branch.draw(sd.random_color())
    r_angle = sd.random_number(18, 42)
    r_length = sd.random_number(60, 90) / 100
    draw_branches(branch.end_point, angle + r_angle, length * r_length, width - 1)
    draw_branches(branch.end_point, angle - r_angle, length * r_length, width - 1)

# draw_branches()

# sd.pause()
