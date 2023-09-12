def delete_tab_number(tab_numbers, bad_tab_number):
    new_list = ''
    for i in tab_numbers.split(' '):
        if i != bad_tab_number:
            new_list += f"{i} "
        if i == bad_tab_number:
            pass

    return new_list


tab_numbers = '87996 126503 93203 5030'
bad_tab_number = '87996'

print(delete_tab_number(tab_numbers, bad_tab_number))
