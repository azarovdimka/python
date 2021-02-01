#!/usr/bin/env python
# coding: utf-8

import pandas as pd

df = pd.read_csv('/datasets/music_project.csv')

df.head(10)
df.info()
df.columns
df.set_axis(['user_id', 'track_name', 'artist_name', 'genre_name', 'city', 'time', 'weekday'], axis='columns',
            inplace=True)
df.columns
df.isnull().sum()
df['track_name'] = df['track_name'].fillna('unknown')
df['artist_name'] = df['artist_name'].fillna('unknown')
df.isnull().sum()
df.dropna(subset=['genre_name'], inplace=True)
df.isnull().sum()
df.duplicated().sum()
df = df.drop_duplicates().reset_index(drop=True)
df.duplicated().sum()
genres_list = df['genre_name'].unique()


def find_genre(name):
    count = 0
    for genre in genres_list:
        if genre == name:
            count += 1
    return count


find_genre('hip')
find_genre('hop')
find_genre('hip-hop')


def find_hip_hop(df, wrong):
    df['genre_name'] = df['genre_name'].replace(wrong, 'hiphop')
    final = df[df['genre_name'] == wrong]['genre_name'].count()
    return final


find_hip_hop(df, 'hip')

df.info()

df.groupby('city')['genre_name'].count()
df.groupby('weekday')['genre_name'].count()


def number_tracks(df, day, city):
    track_list = df[(df['weekday'] == day) & (df['city'] == city)]
    track_list_count = track_list['genre_name'].count()
    return track_list_count


number_tracks(df, 'Monday', 'Moscow')  # <список композиций для Москвы в понедельник>
number_tracks(df, 'Monday', 'Saint-Petersburg')  # <список композиций для Санкт-Петербурга в понедельник>
number_tracks(df, 'Wednesday', 'Moscow')  # <список композиций для Москвы в среду>
number_tracks(df, 'Wednesday', 'Saint-Petersburg')  # <список композиций для Санкт-Петербурга в среду>
number_tracks(df, 'Friday', 'Moscow')  # <список композиций для Москвы в пятницу>
number_tracks(df, 'Friday', 'Saint-Petersburg')  # <список композиций для Санкт-Петербурга в пятницу>

columns = ['city', 'monday', 'wednesday', 'friday']
data = [['Moscow', 15347, 10865, 15680],
        ['Saint-Petersburg', 5519, 6913, 5802]]
table = pd.DataFrame(data=data, columns=columns)
print(table)

moscow_general = df[df['city'] == 'Moscow']

spb_general = df[df['city'] == 'Saint-Petersburg']


def genre_weekday(df, day, time1, time2):
    genre_list = df[(df['weekday'] == day) & (df['time'] > time1) & (df['time'] < time2)]
    genre_list_sorted = genre_list.groupby('genre_name')['genre_name'].count().sort_values(ascending=False).head(10)
    return genre_list_sorted


genre_weekday(moscow_general, 'Monday', '07:00:00',
              '11:00:00')  # <вызов функции для утра понедельника в Москве (вместо df таблица moscow_general)>
genre_weekday(spb_general, 'Monday', '07:00:00',
              '11:00:00')  # <вызов функции для утра понедельника в Петербурге (вместо df таблица spb_general)>
genre_weekday(moscow_general, 'Friday', '17:00:00', '23:00:00')  # <вызов функции для вечера пятницы в Москве>

genre_weekday(spb_general, 'Friday', '17:00:00', '23:00:00')  # <вызов функции для вечера пятницы в Питере>

moscow_genres = moscow_general.groupby('genre_name')['genre_name'].count().sort_values(ascending=False)

print(moscow_genres.head(10))  # <просмотр первых 10 строк moscow_genres>

spb_genres = spb_general.groupby('genre_name')['genre_name'].count().sort_values(
    ascending=False)  # <группировка таблицы spb_general, расчёт, сохранение в spb_genres>

print(spb_genres.head(10))  # <просмотр первых 10 строк spb_genres>
