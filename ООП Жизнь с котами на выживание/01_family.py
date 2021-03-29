# -*- coding: utf-8 -*-

from termcolor import cprint
from random import randint, choice

import rus_ends


######################################################## Часть первая
#
# Создать модель жизни небольшой семьи.
#
# Каждый день участники жизни могут делать только одно действие.
# Все вместе они должны прожить год и не умереть.
#
# Муж может:
#   есть,
#   играть в WoT,
#   ходить на работу,
# Жена может:
#   есть,
#   покупать продукты,
#   покупать шубу,
#   убираться в доме,

# Все они живут в одном доме, дом характеризуется:
#   кол-во денег в тумбочке (в начале - 100)
#   кол-во еды в холодильнике (в начале - 50)
#   кол-во грязи (в начале - 0)
#
# У людей есть имя, степень сытости (в начале - 30) и степень счастья (в начале - 100).
#
# Любое действие, кроме "есть", приводит к уменьшению степени сытости на 10 пунктов
# Кушают взрослые максимум по 30 единиц еды, степень сытости растет на 1 пункт за 1 пункт еды.
# Степень сытости не должна падать ниже 0, иначе чел умрет от голода.
#
# Деньги в тумбочку добавляет муж, после работы - 150 единиц за раз.
# Еда стоит 10 денег 10 единиц еды. Шуба стоит 350 единиц.
#
# Грязь добавляется каждый день по 5 пунктов, за одну уборку жена может убирать до 100 единиц грязи.
# Если в доме грязи больше 90 - у людей падает степень счастья каждый день на 10 пунктов,
# Степень счастья растет: у мужа от игры в WoT (на 20), у жены от покупки шубы (на 60, но шуба дорогая)
# Степень счастья не должна падать ниже 10, иначе чел умирает от депрессии.
#
# Подвести итоги жизни за год: сколько было заработано денег, сколько сьедено еды, сколько куплено шуб.


class House:

    def __init__(self):
        """Содержит атрибуты (свойства) дома."""
        self.money = 100
        self.accountant = 0  # бухгалтер будет считать сколько всего заработали денег за год
        self.expenses = 0  # учет расходов домохозяйцства за год
        self.food = 50
        self.dirt = 0
        self.cat_food = 30
        self.cats_at_house = []  # на котов отдельный список - надо будет выводить информацию о количестве котов
        self.residents_of_the_house = []
        self.count_fur_coats = 0

    def __str__(self):
        return 'В доме    | {} денег; \n' \
               'осталось: | {} еды для человека; \n' \
               '          | {} еды для кота;\n' \
               '__________| {} грязи.'.format(self.money, self.food, self.cat_food, self.dirt)


class Cat:
    cat_names = ["Кеша", "Василий", "Матроскин", "Мурзик", "Барсик", "Антонина", "Мурка", "Фёдор"]

    def __init__(self):
        """Содержит атрибуты кота. Имена создаваемому коту присваиваются автоматически из списка уличных
         котов внутри класса."""
        self.name = choice(__class__.cat_names)
        self.fullness = 30
        self.house = None

    def __str__(self):
        """Выводит информацию о степени сытости кота."""
        return f'Кот {self.name}| уровень сытости: {self.fullness}%\n' \
               '-----------'

    def eat(self):
        """Кот ест."""
        self.fullness += 10
        cprint(f'Кот {self.name} поел', color='green')

    def sleep(self):
        """Кот спит."""
        self.fullness -= 10
        cprint(f'Кот {self.name} поспал', color='green')

    def tear_up_the_wallpapper(self):
        """Кот дерет обои."""
        self.house.dirt += 5
        self.fullness -= 10
        cprint(f'Кот {self.name} подрал обои', color='red')

    def act(self):
        """Кот выбирает действие."""
        if self.fullness <= 0:
            cprint(f'Кот {self.name} умер...', color='red')
            return
        if self.fullness <= 10:
            self.eat()
        elif self.fullness < 30:
            self.tear_up_the_wallpapper()
        elif self.fullness >= 30:
            self.sleep()


class Person:

    def __init__(self, name):
        """Содержит общие атрибуты(свойства) для каждого человека."""
        self.name = name
        self.fullness = 30
        self.happiness = 100
        self.house = None

    def __str__(self):
        return '{}      | уровень счастья: {}%\n' \
               '__________| уровень сытости: {}%'.format(self.name, self.happiness, self.fullness)

    def go_to_the_house(self, house):
        """Человек заселяется в дом."""
        self.house = house
        self.house.residents_of_the_house.append(self)
        self.fullness -= 10
        cprint(f'{self.name} заселяется в дом', color='cyan')

    def pet_the_cat(self):
        """Человек гладит кота."""
        self.happiness += 5
        self.fullness -= 10
        cprint(f'{self.name} погладил кота {cat.name}', color='green')

    def pick_cat_up(self, adopted_cat):
        self.house.cats_at_house.append(adopted_cat)
        adopted_cat.house = self.house
        cprint(f'{self.name} подобрал кота {adopted_cat.name}', color='green')

    def try_pick_cat_up(self, stray_cats):
        """Человек подбирает кота втом случае, если дома еще нет котов, либо при наличии уже взятого одного или
        нескольких котов, для того чтобы взять нового он проверит для начала сытость котов взятых до этого а также
        количесвто грязи в доме: выбирает кота из списка уличных котов - записывает его в кота, потом
        добавляет его в список котов, живущих в доме, присваивает ему дом, и сообщает об этом."""

        hungry_cat_found = any(c.fullness <= 10 for c in self.house.cats_at_house)
        if len(self.house.cats_at_house) == 0 or (self.house.dirt < 30 and not hungry_cat_found):
            self.pick_cat_up(choice(stray_cats))

    def feed_the_cat(self):
        """Помимо того , что кот может сам есть, его может кормить еще человек."""
        cat.fullness += 10
        cprint(f'{self.name} покормил кота {cat.name}', color='green')

    def eat(self):
        """Человек ест."""
        end = rus_ends.change_person(self.name)  # определяет пол человенка для глагола поел
        if self.house.food >= 10:
            self.fullness += 15  # Кушают взрослые максимум по 30 единиц еды, степень сытости растет на 1 пункт за 1 пункт еды.
            self.house.food -= 15
            cprint(f'{self.name} поел{end}', color='green')
        else:
            cprint(f'{self.name} хотел{end} поесть, но не поел{end}', color='red')

    def act(self):
        """Любой человек перед совершением какого-либо дейсвтия, вначале проверяет степень своей сытости: если она меньше или
        равна нулю - умирает; степень своего счастья: если оно меньше десяти - умирает от дипрессии. Затем проверяет
        степень грязи в доме, затем выполняет одно из действий уже в дочернем методе."""

        if self.fullness <= 0 or self.happiness < 10:
            end = rus_ends.change_person(self.name)
            cprint(f'{self.name} мертв{end}...', color='red')
        if self.house.dirt >= 90:
            self.happiness -= 10
            return


class Husband(Person):
    def act(self):
        """Метод акт в дочернем классе джополнен различнгыми действиями для каждого класса."""
        if self.fullness <= 40:
            self.eat()
        elif self.house.money < 200:
            self.work()
        elif self.happiness <= 90:
            self.gaming()
        else:
            self.work()
        if self.happiness < 20:
            self.pet_the_cat()

    def work(self):
        """Муж работает."""
        self.house.money += 150
        self.house.accountant += 150  # аналогичную сумму мы сообщаем бухгалтеру, => узнать кол-во зараб-х денег за год
        self.fullness -= 10
        cprint(f'{self.name} поработал', color='green')

    def gaming(self):
        """Муж играет в World of Tanks."""
        self.happiness += 20
        self.fullness -= 10
        cprint(f'{self.name} поиграл в World of Tanks', color='green')


class Wife(Person):

    def act(self):
        """Дополнен базовый метод act, добавлены условия проверки для шопинга, уборки в доме, покупки шубы."""
        if self.house.food <= 40:
            self.shopping()
        elif self.fullness <= 40:
            self.eat()
        elif self.house.dirt >= 100:
            self.clean_house()
        elif self.house.money > 350:
            self.buy_fur_coat()
        elif self.happiness >= 20:
            self.pet_the_cat()
        else:
            self.shopping()

    def shopping(self):
        """Жена сходила в магазин."""
        if self.house.money >= 60:
            self.house.money -= 60
            self.house.expenses += 60  # аналогичную сумму мы записываем в годовые расходы
            self.house.cat_food += 5
            self.house.food += 55
            self.fullness -= 10
            cprint(f'{self.name} сходила в магазин', color='green')
        else:
            cprint(f'{self.name} не смогла сходить в магазин - не хватило денег', color='red')

    def buy_fur_coat(self):
        """Жена купила шубу."""
        if self.house.money > 350:
            self.house.money -= 350
            self.house.expenses += 350  # аналогичную сумму мы записываем в годовые расходы
            self.fullness -= 10
            self.happiness += 60
            self.house.count_fur_coats += 1
            cprint(f'{self.name} купила шубу', color='green')
        else:
            cprint(f'{self.name} хотела купить шубу, но ей не хватило денег.', color='green')

    def clean_house(self):
        """Жена прибралась в доме."""
        self.house.dirt -= 100
        self.fullness -= 10
        cprint(f'{self.name} убралась в доме', color='green')


class Child(Person):

    def eat(self):
        """Человек ест."""
        end = rus_ends.change_person(self.name)  # определяет пол человенка для глагола поел
        if self.house.food > 10:
            self.fullness += 10  # Кушают взрослые максимум по 30 единиц еды, степень сытости растет на 1 пункт за 1 пункт еды.
            self.house.food -= 10
            cprint(f'{self.name} поел{end}', color='green')
        else:
            cprint(f'{self.name} хотел{end} поесть, но не поел{end}', color='red')

    def act(self):
        """Для дополнен базовый метод, добавлен метод спать. Ребенок в базовом методе проверяет сытость и счатлив ли
         он, чтобы вслуче чего - умереть, затем выбирает действие, которое он будет делать: есть или спать."""
        if self.fullness <= 40:
            self.eat()
        elif self.fullness > 40:
            self.sleep()

    def sleep(self):
        """Ребенок поспал."""
        self.fullness -= 10
        cprint(f'{self.name} Ребенок поспал', color='green')


house = House()

serge = Husband(name='Серж')
masha = Wife(name='Мари')
kolya = Child(name='Коля')

stray_cats = [Cat() for i in range(10)]  # Создает сразу 10 уличных котов

serge.go_to_the_house(house=house)
masha.go_to_the_house(house=house)
kolya.go_to_the_house(house=house)

for day in range(1, 366):
    cprint('================== День {} =================='.format(day), color='white')
    house.dirt += 5

    serge.act()
    masha.act()
    kolya.act()

    serge.try_pick_cat_up(stray_cats)

    for cat in house.cats_at_house:  # каждый кот живущий в доме выполнит действие
        cat.act()

    cprint(serge, color='cyan')  # отчет о состоянии маши сережи и коли
    cprint(masha, color='cyan')
    cprint(kolya, color='cyan')

    for cat in house.cats_at_house:  # распечатает информацию про каждого кота, живущего в доме
        cprint(cat, color='cyan')

    cprint(house, color='cyan')  # информация об остаткая денег и еды в доме на конец дня

cprint("Всего за данный период {} смогла купить {} {}.".format(masha.name, house.count_fur_coats,
                                                               rus_ends.change_coat(house.count_fur_coats)),
       color='blue')
cprint("Всего в доме проживает {} {}.".format(len(house.cats_at_house), rus_ends.change_cat(house.cats_at_house)),
       color='blue')
cprint(f"Всего за год муж заработал {house.accountant} долларов.", color='blue')
cprint(f"Всего за год жена потратила {house.expenses} долларов.", color='blue')

# зачет второго этапа!
# зачет!

# Любое действие, кроме "есть", приводит к уменьшению степени сытости на 10 пунктов
# Кушают взрослые максимум по 30 единиц еды, степень сытости растет на 1 пункт за 1 пункт еды.
# Степень сытости не должна падать ниже 0, иначе чел умрет от голода.

# Деньги в тумбочку добавляет муж, после работы - 150 единиц за раз.
# Еда стоит 10 денег 10 единиц еды. Шуба стоит 350 единиц.

######################################################## Часть вторая
#
# После подтверждения учителем первой части надо
# отщепить ветку develop и в ней начать добавлять котов в модель семьи
#
# Кот может:
#   есть,
#   спать,
#   драть обои
#
# Люди могут:
#   гладить кота (растет степень счастья на 5 пунктов)
#
# В доме добавляется:
#   еда для кота (в начале - 30)
#
# У кота есть имя и степень сытости (в начале - 30)
# Любое действие кота, кроме "есть", приводит к уменьшению степени сытости на 10 пунктов
# Еда для кота покупается за деньги: за 10 денег 10 еды.
# Кушает кот максимум по 10 единиц еды, степень сытости растет на 2 пункта за 1 пункт еды.
# Степень сытости не должна падать ниже 0, иначе кот умрет от голода.
#
# Если кот дерет обои, то грязи становится больше на 5 пунктов

#
# ######################################################## Часть вторая бис
# #
# # После реализации первой части надо в ветке мастер продолжить работу над семьей - добавить ребенка
# #
# # Ребенок может:
# #   есть,
# #   спать,
# #
# # отличия от взрослых - кушает максимум 10 единиц еды,
# # степень счастья  - не меняется, всегда ==100 ;)
#
#
# ######################################################## Часть третья
# #
# # после подтверждения учителем второй части (обоих веток)
# # влить в мастер все коммиты из ветки develop и разрешить все конфликты
# # отправить на проверку учителем.
#
#
# home = House()
# serge = Husband(name='Сережа')
# masha = Wife(name='Маша')
# kolya = Child(name='Коля')
# murzik = Cat(name='Мурзик')
#
# for day in range(365):
#     cprint('================== День {} =================='.format(day), color='red')
#     serge.act()
#     masha.act()
#     kolya.act()
#     murzik.act()
#     cprint(serge, color='cyan')
#     cprint(masha, color='cyan')
#     cprint(kolya, color='cyan')
#     cprint(murzik, color='cyan')
#
#
# # Усложненное задание (делать по желанию)
# #
# # Сделать из семьи любителей котов - пусть котов будет 3, или даже 5-10.
# # Коты должны выжить вместе с семьей!
# #
# # Определить максимальное число котов, которое может прокормить эта семья при значениях зарплаты от 50 до 400.
# # Для сглаживание случайностей моделирование за год делать 3 раза, если 2 из 3х выжили - считаем что выжили.
# #
# # Дополнительно вносить некий хаос в жизнь семьи
# # - N раз в год вдруг пропадает половина еды из холодильника (коты?)
# # - K раз в год пропадает половина денег из тумбочки (муж? жена? коты?!?!)
# # Промоделировать - как часто могут случаться фейлы что бы это не повлияло на жизнь героев?
# #   (N от 1 до 5, K от 1 до 5 - нужно вычислит максимумы N и K при котором семья гарантированно выживает)
# #
# # в итоге должен получится приблизительно такой код экспериментов
# # for food_incidents in range(6):
# #   for money_incidents in range(6):
# #       life = Simulation(money_incidents, food_incidents)
# #       for salary in range(50, 401, 50):
# #           max_cats = life.experiment(salary)
# #           print(f'При зарплате {salary} максимально можно прокормить {max_cats} котов')
