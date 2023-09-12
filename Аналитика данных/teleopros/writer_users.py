def writer(result):
    file_path = "/usr/local/bin/teleopros/users.txt"  # "C:\\PycharmProjects\\Probe\\мои примеры\\GitHub\\Аналитика данных\\teleopros\\users.txt"  # "/usr/local/bin/teleopros/users.txt"  #
    try:
        with open(file_path, 'r', encoding='utf-8') as original:
            old_file = original.read()
        with open(file_path, 'w', encoding='utf-8') as modified:
            modified.write(f'{old_file}\n{result}')

    except Exception as exc:
        return exc
