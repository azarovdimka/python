import simple_draw as sd

sd.resolution = (1500, 800)


def draw_house(point=sd.get_point(600, 0), height=300, width=300):
    sd.rectangle(left_bottom=point, right_top=sd.get_point(point.x + width + 25, point.y + height), width=5)
    draw_triangle(point=sd.get_point(point.x, point.y + height), length=width + 25, width=5)
    draw_brickwall(point=point, height=height, width=width)
    draw_window(point=sd.get_point(point.x + 50, point.y + 100), width=width, height=height)


def draw_window(point, width, height):
    width = width // 3 + 125 + point.x
    height = height // 3 + 50 + point.y
    sd.rectangle(left_bottom=point, right_top=sd.get_point(width, height), width=0, color=sd.background_color)
    sd.rectangle(left_bottom=point, right_top=sd.get_point(width, height), width=5)


def draw_brickwall(point, height, width):
    brick_x, brick_y = 50, 25
    height = point.y + height
    width = point.x + width
    row = 0
    for y in range(point.y, height, brick_y):
        row += 1
        for x in range(point.x, width, brick_x):
            x0 = x if row % 2 else x + brick_x // 2
            left_bottom = sd.get_point(x0, y)
            right_top = sd.get_point(x0 + brick_x, y + brick_y)
            sd.rectangle(left_bottom=left_bottom, right_top=right_top, width=1)


def draw_triangle(point, length, width):
    sides = 3
    draw_figure(sides=sides, start_point=point, length=length, width=width)


def draw_square(point, length):
    sides = 4
    draw_figure(sides=sides, start_point=point, length=length)


def draw_figure(sides, start_point, length, width):
    point = start_point
    step = round(360 / sides)
    for angle in range(0, 360, step):
        point = sd.vector(start=point, angle=angle, width=width, length=length)

# draw_house()
# sd.pause()
