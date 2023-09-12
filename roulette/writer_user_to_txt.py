import telebot
import settings

file_path = "/usr/local/bin/roulette/users.txt"  #  "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\roulette\\users.txt"  #  "/usr/local/bin/roulette/users.txt"  # "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\roulette\\users.txt"
surnames = "/usr/local/bin/roulette/chosen_surnames.txt"  # "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\roulette\\chosen_surnames.txt"  # "/usr/local/bin/roulette/chosen_surnames.txt"  # "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\roulette\\chosen_surnames.txt"
bot = telebot.TeleBot(settings.TOKEN)


def writer_user_id(user_id, participant, chosen_surname):
    with open(file_path, 'r', encoding='utf-8') as original:
        old_file = original.read()
    with open(file_path, 'w', encoding='utf-8') as modified:
        new_data = f'{old_file}\n{user_id} {participant}'
        modified.write(new_data)


    with open(surnames, 'r', encoding='utf-8') as original_surnames:
        old_file_surnames = original_surnames.read()
    with open(surnames, 'w', encoding='utf-8') as modified_surnames:
        new_data_surnames = f'{old_file_surnames}\n{chosen_surname}'
        modified_surnames.write(new_data_surnames)
