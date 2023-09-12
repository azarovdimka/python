x1, y1, x2, y2 = int(input()), int(input()), int(input()), int(input())
if ((x2 == x1 + 1) and (y2 == y1 + 1)) or ((x2 == x1 + 1) and (y2 == y1 - 1)) or (
        (x2 == x1 - 1) and (y2 == y1 - 1)) or ((x2 == x1 - 1) and (y2 == y1 + 1)):
    print('YES')
elif (x1, y1) <= (x2, y2):
    print('YES')
else:
    print('NO')
