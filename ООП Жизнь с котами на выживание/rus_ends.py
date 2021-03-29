# -*- coding: utf-8 -*-
# это самый правильный вариант кода!!! смотерть сюда при слиянии
def change_coat(coats):
    """Меняет окончание у слова "Шуба" в зависимости от количества."""
    return "шубы" if 2 <= coats <= 4 else "шуб" if coats > 4 else "шуба" if "1" in str(coats) or len(
        coats) != 11 else None


def change_cat(cats):
    """Меняет окончание у слова "Кот" в зависимости от количества."""
    return "кота" if 2 <= len(cats) <= 4 else "котов" if len(cats) > 4 else "кот" if 1 == len(cats) and len(
        cats) != 11 else None


def change_person(name):
    """Определяет род человека и в зависимости от этого обавляет ему букву а или нет к концу слова."""
    return '' if name == "Серж" else 'а' if name == "Мари" else '' if name == "Коля" else None
# это самый правильный вариант кода!!! смотерть сюда при слиянии
