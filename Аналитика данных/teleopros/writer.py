def writer(result):
    file_path = "/usr/local/bin/teleopros/result.txt"  # "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\Аналитика данных\\teleopros\\result.txt"  #
    try:
        with open(file_path, 'r', encoding='utf-8') as original:
            old_file = original.read()  # приходится плюсовать единицу, потому что при plan.split('\n') он бобавляет в конце еще одну пустую строку, так как в конце последней строки тоже стоит \n
        with open(file_path, 'w', encoding='utf-8') as modified:
            modified.write(f'{old_file}\n{result}')  # изменения в файл запишет

    except Exception as exc:
        return exc
