import simple_draw as sd


def draw_sun(point=sd.get_point(550, 550), length=90):
    for angle in range(0, 360, 3):
        sd.vector(start=point, angle=angle, width=2, length=length)
    # while True:
    for angle in range(0, 360, 15):
        sd.vector(start=point, angle=angle, width=1, length=length + 50, color=sd.COLOR_WHITE)
        sd.sleep(0.02)
        sd.vector(start=point, angle=angle * 2, width=1, length=length + 30, color=sd.background_color)
        sd.vector(start=point, angle=angle * 2, width=1, length=length)
        sd.sleep(0.02)

    # if sd.user_want_exit():
    #     break

# draw_sun()
#
# sd.pause()
