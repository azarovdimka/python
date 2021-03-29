# -*- coding: utf-8 -*-
import simple_draw as sd

rainbow_colors = (sd.COLOR_RED, sd.COLOR_ORANGE, sd.COLOR_YELLOW, sd.COLOR_GREEN,
                  sd.COLOR_CYAN, sd.COLOR_BLUE, sd.COLOR_PURPLE)


def draw_rainbow(point=sd.get_point(150, 30), radius=800):
    for color in rainbow_colors:
        radius += 20
        sd.circle(point, radius=radius, color=color, width=40)

# draw_rainbow()
# sd.pause()
