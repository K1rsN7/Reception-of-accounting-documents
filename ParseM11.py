import json
from PyPDF2 import PdfFileReader as pd
import os
import re
import time

json_programm = {}
for filename in os.listdir("М-11/"):
    errors = []
    with open("М-11/" + filename, 'rb') as pdf_file:
        pdf_open_reader = pd(pdf_file)  # Открываем PDF на чтение
        # Циклом обходим все страницы книги и выводим их содержание на печать
        parse_text = ""
        for page_num in range(pdf_open_reader.numPages):
            pdf_page = pdf_open_reader.getPage(page_num)
            text = pdf_page.extractText("")
            # Логика прыжком по парсенному тексту
            list = {
                "ТРЕБОВАНИЕ-НАКЛАДНАЯ №  ": "\n",
                "Организация ": "по ОКПО",
                "по ОКПО ": "\n",
                "Структурное\nподразделение": "Отправитель",
                "(работ,\nуслуг)": "Через кого",  # Таблица
                "Через кого": "Затребовал",
                "Затребовал": "Разрешил",
                "Разрешил": "Материальные",
                "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16": "Отпустил",
                "Отпустил": "(должность)",
                "(должность)": "(подпись)",
                "(подпись)": "(расшифровка подписи)Получил",
                "расшифровка подписи)Получил": "(должность)",
                "должность)": "(подпись)",
                "подпись)": "(расшифровка подписи)",
                "расшифровка подписи)": "Документ подписан электронной подписью",
            }
            for str_start, str_end in list.items():
                index_start = text.find(str_start) + len(str_start)
                index_end = text[index_start:].find(str_end)
                parse_text += text[index_start: index_start + index_end] + " \\/"
                text = text[index_start + index_end:]

    keys = [
        "ТРЕБОВАНИЕ-НАКЛАДНАЯ №", "Организация", "по ОКПО", "Структурное подразделение",
        "Первая таблица", "Через кого", "Затребовал", "Разрешил", "Вторая таблица", "Отпустил_должность",
        "Отпустил_подпись", "Отпустил_ФИО", "Получил_должность", "Получил_подпись", "Получил_ФИО"
    ]
    json_for = {}
    elements = parse_text.replace("\n", " ").split("\\/")
    # Обработка ошибок
    for index in range(0, len(keys)):
        key = keys[index]
        if key == "Структурное подразделение":
            value = " ".join(elements[index].split())[:-4]
            be = " ".join(elements[index].split())[-4:]
            if value:
                json_for[key] = value
            else:
                errors.append(f"Отсутствует значение для ключа '{key}'")
            if be:
                json_for["БЕ"] = be
            else:
                errors.append(f"Отсутствует значение для ключа 'БЕ'")
        elif key == "по ОКПО":
            len_okpo = len(" ".join(elements[index].split()))
            if len_okpo < 8 or len_okpo > 10:
                errors.append(f'Некорректный ОКПО {key}')
            json_for[key] = " ".join(elements[index].split())
        elif key == "Первая таблица":
            table = elements[index][1:]
            date_table = table.split(" ")[0]
            try:
                time.strptime(date_table, '%d/%m/%Y')
            except ValueError:
                errors.append("Некорректно заполнена дата составления в таблице")
            table = " ".join(table.split(" ")[1:])
            table = table[3:]
            nomnumber_table = table[:table[1:].find(f"{table[0:3]}")]
            if nomnumber_table[4] != " ":
                errors.append("Некорректно заполнен 'отправитель,структурное подразделений'")
            table = table[table[1:].find(f"{table[0:3]}") + 1:]
            re_itog = re.search(r'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]', table)
            if re_itog:
                strpodrazdel = table[:re_itog.span()[0] - 3]
                subschet = table[re_itog.span()[0]:re_itog.span()[1]]
            else:
                strpodrazdel = table[:table.find("- - ")]
                subschet = None
            if not subschet:
                errors.append("Некорректно заполнен субсчёт в таблице")
            if strpodrazdel[4] != " ":
                errors.append("Некорректно заполнен 'получатель, структурное подразделение'")
        elif key == "Вторая таблица":
            table = elements[index][1:-3]
            re_itog = re.search(r'[0-9][0-9][0-9][0-9] [0-9][0-9][0-9][0-9][0-9][0-9]', table)
            if re_itog:
                subschet = "".join(table[re_itog.span()[0]:re_itog.span()[1]].split())
                table = table[re_itog.span()[1]:]
            else:
                subschet = None
                table = table[1:]
            if not subschet:
                errors.append("Некорректно заполнено поле 'Корреспондирующий счет, субсчет' в таблице")
            re_itog = re.search(r'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9] [0-9][0-9]', table)
            if re_itog:
                nomnumber_table2 = "".join(table[re_itog.span()[0]:re_itog.span()[1]].split())
                naimen_table = table[:re_itog.span()[0]]
                table = table[re_itog.span()[1]:]
            else:
                nomnumber_table2 = table[:table.find("- ")]
                naimen_table = None
            if not naimen_table:
                errors.append("Некорректно заполнено поле 'Материальные ценности, номенклатурный номер'")
            re_itog = re.search(r' [0-9][0-9][0-9] ', table)
            if re_itog:
                code_unit = table[re_itog.span()[0] + 1:re_itog.span()[1] - 1]
                table = table[re_itog.span()[1]:]
            else:
                code_unit = None
            re_itog = re.search(r'[0-9]', table)
            if re_itog:
                ed_iz = table[:re_itog.span()[0]]
                table = table[re_itog.span()[0]:]
            else:
                ed_iz = None
            number_zadreb = table[:table.find(".") + 4]
            table = table[table.find(".") + 5:]
            number_otpush = table[:table.find(".") + 4]
            table = table[table.find(".") + 5:]
            price = table[:table.find(",") + 3]
            table = table[table.find(",") + 4:]
            sum = table[:table.find(",") + 3]
            table = table[table.find(",") + 4:]
            try:
                if ("".join(number_otpush.split(" "))) not in "".join(number_zadreb.split(" ")):
                    errors.append("Количество затраченного и отпущенного не сходится в таблице")
            except:
                errors.append("Некорректно указано количество затраченного и отпущенного не сходится в таблице")
        else:
            value = " ".join(elements[index].split())
            if value:
                json_for[key] = value
            else:
                errors.append(f"Отсутствует значение для '{key}'")

    print("Название файла: " + filename)
    errors_json = []
    if len(errors) == 0:
        errors = "Корректно заполнен"
    else:
        print("Список ошибок: ")
        for error in set(errors):
            errors_json += error
            print("     " + error)
    json_programm[filename] = errors_json
    print("-" * 30)

M_11_json = json.dumps(json_programm)
with open("M-11.json", "w") as my_file:
    my_file.write(M_11_json)
input()