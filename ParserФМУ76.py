import json
import re
import time

from PyPDF2 import PdfFileReader as pd
import os

json_programm = {}
# Открываем файл конструктором With
for filename in os.listdir("dataset/ФМУ-76/"):
    errors = []
    try:
        with open("dataset/ФМУ-76/" + filename, 'rb') as pdf_file:
            pdf_open_reader = pd(pdf_file)  # Открываем PDF на чтение
            # Циклом обходим все страницы книги и выводим их содержание на печать
            parse_text = ""
            json_for = {}
            id_predsed = 0
            id_komis = 0
            for page_num in range(pdf_open_reader.numPages):
                pdf_page = pdf_open_reader.getPage(page_num)
                text = pdf_page.extractText("")
                if page_num == 0:
                    # Логика прыжком по значениям
                    list = {
                        "Форма по ОКУД": "по ОКПО",
                        "по ОКПО": "организация",
                        "организация": "БЕ",
                        "БЕ": "структурное подразделение",
                        "АКТНомер Дата": "на списание материальных ценностей",
                        "(руководитель)": "(подпись)",
                        "(подпись)": "(расшифровка подписи)",
                        "(расшифровка подписи)": "Структурное подразделение",  # Обработать после г.
                        "носитель затрат": "Материально",
                        "Материально\nответственное лицо": "Направление расхода",
                        "Направление расхода": "Инвентарный номер ремонтируемого основного средства",
                        "Инвентарный номер ремонтируемого основного средства": "Комиссия в составе:",
                        "Комиссия в составе:": "составила",
                        "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17": "Подписи лиц",
                        "Председатель комиссии": "Члены комиссии:",
                        "Члены комиссии:": "Материально",
                        "Материально ответственное лицо": "(должность)",
                        "(должность)": "(подпись)",
                        "подпись)": "(расшифровка подписи)",
                        "расшифровка подписи)": "г.",

                    }
                    for str_start, str_end in list.items():
                        index_start = text.find(str_start) + len(str_start)
                        index_end = text[index_start:].find(str_end)
                        parse_text += text[index_start: index_start + index_end] + "\\/"
                        text = text[index_start + index_end:]
                    keys = [
                        "Форма по ОКУД", "по ОКПО", "Структурное подразделение", "БЕ",
                        "АКТ_таблица", "УТВЕНикелинАЮ_должность", "УТВЕНикелинАЮ", "УТВЕНикелинАЮ_дата",
                        "Первая таблица", "Материально ответственное лицо", "Направление расхода", "Инвентарный номер",
                        "Коммисия в составе", "Вторая таблица", "Председатель комисии", "Члены коммисии",
                        "Мат_отв_лицо_должность", "Мат_отв_лицо_подпись", "Мат_отв_лицо_ФИО", "Дата"
                    ]
                    elements = parse_text.replace("\n", " ").split("\\/")
                    for index in range(0, len(keys)):
                        if keys[index] == "Форма по ОКУД":
                            json_for[keys[index]] = elements[index].split()[0]
                            json_for["Организация"] = " ".join(elements[index].split()[1:])
                        elif (keys[index] == "АКТ_таблица"):
                            json_for["АКТ_номер"] = elements[index].split()[0]
                            json_for["АКТ_дата"] = elements[index].split()[1]
                        elif (keys[index] == "Председатель комисии"):
                            stroka = " ".join(elements[index].split())
                            for i in range(stroka.count("(должность)")):
                                json_for[f"Председатель{id_predsed}_должность"] = " ".join(
                                    stroka[:stroka.find("(должность)")].split())
                                stroka = stroka[stroka.find("(должность)") + len("(должность)"):]
                                json_for[f"Председатель{id_predsed}_подпись"] = " ".join(
                                    stroka[:stroka.find("(подпись)")].split())
                                stroka = stroka[stroka.find("(подпись)") + len("(подпись)"):]
                                json_for[f"Председатель{id_predsed}_рашифровка_подписи"] = " ".join(
                                    stroka[:stroka.find("(расшифровка подписи)")].split())
                                stroka = stroka[stroka.find("(расшифровка подписи)") + len("(расшифровка подписи)"):]
                                id_predsed += 1
                        elif keys[index] == "Члены коммисии":
                            stroka = " ".join(elements[index].split())
                            for i in range(stroka.count("(должность)")):
                                json_for[f"Член_коммисии{id_komis}_должность"] = " ".join(
                                    stroka[:stroka.find("(должность)")].split())
                                stroka = stroka[stroka.find("(должность)") + len("(должность)"):]
                                json_for[f"Член_коммисии{id_komis}_подпись"] = " ".join(
                                    stroka[:stroka.find("(подпись)")].split())
                                stroka = stroka[stroka.find("(подпись)") + len("(подпись)"):]
                                json_for[f"Член_коммисии{id_komis}_рашифровка_подписи"] = " ".join(
                                    stroka[:stroka.find("(расшифровка подписи)")].split())
                                stroka = stroka[stroka.find("(расшифровка подписи)") + len("(расшифровка подписи)"):]
                                id_komis += 1
                        else:
                            if keys[index] not in json_for.keys():
                                json_for[keys[index]] = " ".join(elements[index].split())
                            else:
                                json_for[keys[index]] += " ".join(elements[index].split())
                else:
                    list = {
                        "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17": "Подписи лиц",
                        "Председатель комиссии": "Члены комиссии:",
                        "Члены комиссии:": "Материально",
                        "Материально ответственное лицо": "(должность)",
                        "(должность)": "(подпись)",
                        "подпись)": "(расшифровка подписи)",
                        "расшифровка подписи)": "г.",
                    }
                    parse_text = ""
                    for str_start, str_end in list.items():
                        index_start = text.find(str_start) + len(str_start)
                        index_end = text[index_start:].find(str_end)
                        parse_text += text[index_start: index_start + index_end] + "\\/"
                        text = text[index_start + index_end:]
                    keys2 = [
                        "Вторая таблица", "Председатель комисии", "Члены коммисии",
                        "Мат_отв_лицо_должность", "Мат_отв_лицо_подпись", "Мат_отв_лицо_ФИО", "Дата"
                    ]
                    elements = parse_text.replace("\n", " ").split("\\/")
                    for index in range(0, len(keys2)):
                        if (keys2[index] == "Председатель комисии"):
                            stroka = " ".join(elements[index].split())
                            for i in range(stroka.count("(должность)")):
                                json_for[f"Председатель{id_predsed}_должность"] = " ".join(
                                    stroka[:stroka.find("(должность)")].split())
                                stroka = stroka[stroka.find("(должность)") + len("(должность)"):]
                                json_for[f"Председатель{id_predsed}_подпись"] = " ".join(
                                    stroka[:stroka.find("(подпись)")].split())
                                stroka = stroka[stroka.find("(подпись)") + len("(подпись)"):]
                                json_for[f"Председатель{id_predsed}_рашифровка_подписи"] = " ".join(
                                    stroka[:stroka.find("(расшифровка подписи)")].split())
                                stroka = stroka[stroka.find("(расшифровка подписи)") + len("(расшифровка подписи)"):]
                                id_predsed += 1
                        elif keys2[index] == "Члены коммисии":
                            stroka = " ".join(elements[index].split())
                            for i in range(stroka.count("(должность)")):
                                json_for[f"Член_коммисии{id_komis}_должность"] = " ".join(
                                    stroka[:stroka.find("(должность)")].split())
                                stroka = stroka[stroka.find("(должность)") + len("(должность)"):]
                                json_for[f"Член_коммисии{id_komis}_подпись"] = " ".join(
                                    stroka[:stroka.find("(подпись)")].split())
                                stroka = stroka[stroka.find("(подпись)") + len("(подпись)"):]
                                json_for[f"Член_коммисии{id_komis}_рашифровка_подписи"] = " ".join(
                                    stroka[:stroka.find("(расшифровка подписи)")].split())
                                stroka = stroka[stroka.find("(расшифровка подписи)") + len("(расшифровка подписи)"):]
                                id_komis += 1
                        else:
                            if keys2[index] not in json_for.keys():
                                json_for[keys2[index]] = " ".join(elements[index].split())
                            else:
                                json_for[keys2[index]] += " ".join(elements[index].split())
            json_for["Дата"] += " г."
    except:
        pass

    print("Название файла: " + filename)
    # print(json_for)
    keys = [
        "Форма по ОКУД", "Организация", "по ОКПО", "Структурное подразделение", "БЕ",
        "АКТ_номер", "АКТ_дата", "УТВЕНикелинАЮ_должность", "УТВЕНикелинАЮ_дата",
        "Первая таблица", "Материально ответственное лицо", "Направление расхода", "Инвентарный номер",
        "Коммисия в составе", "Вторая таблица",
        # "Председатель комисии", "Члены коммисии",
        "Мат_отв_лицо_должность", "Мат_отв_лицо_подпись", "Мат_отв_лицо_ФИО", "Дата"
    ]
    # Обработка ошибок
    for index in range(0, len(keys)):
        if json_for != {}:
            key = keys[index]
            if key == "по ОКПО":
                if len(json_for[key]) != 8:
                    errors.append(f"Некорректный код по ОКПО")
            elif key == "БЕ":
                if len(json_for[key]) != 4:
                    errors.append(f"Некорректный код БЕ")
            elif key == "АКТ_дата":
                date = json_for[key]
                try:
                    time.strptime(date, '%d/%m/%Y')
                except ValueError:
                    errors.append("Некорректно заполнена дата составления в акте")
            elif key == "УТВЕНикелинАЮ_дата":
                stroka = json_for[key][:json_for[key].find("Корреспондирующий счет")]
                day = stroka[1:stroka[1:].find("\"") + 1]
                month = stroka[stroka.find(" ") + 1:]
                age = "".join(month.split(" ")[1:])
                age = age[:age.find("г.")]
                month = "".join(month.split(" ")[0])
                if len(day) != 2 or len(month) < 2 or len(age) != 4:
                    errors.append("Некорректно заполнена дата в 'УТВЕНикелинАЮ'")
            elif key == "Первая таблица":
                table = json_for[key]
                if table[4] != " ":
                    errors.append("Неверно заполнено поле структурное подразделение (цех, участок и др.) в таблице")
                table = table[5:]
                re_itog = re.search(r'[0-9][0-9][0-9]', table)
                table = table[re_itog.span()[0] + 3:]
                re_itog = re.search(r'[0-9][0-9][0-9] ', table)
                if not re_itog:
                    errors.append("Отсутствует код операции в таблице")
                re_itog = re.search(r'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]', table)
                if not re_itog:
                    errors.append("Отсутствует счет. субсчет в таблице")
                statiya = table[-4:]
                re_itog = re.search(r'[0-9][0-9][0-9][0-9]', statiya)
                if not re_itog:
                    errors.append("Отсутствует статья затрат/носитель затрат в таблице")
            elif key == "Вторая таблица":
                table = json_for[key]
                re_itog = re.search(r'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]', table)
                if not re_itog:
                    errors.append("Некорректный технический счёт 32 \"Затраты\" в таблице")
                table = table[table.find(" ") + 1:]
                re_itog = re.search(r'[0-9A-Z][0-9A-Z][0-9A-Z][0-9A-Z][0-9A-Z][0-9A-Z][0-9A-Z][0-9A-Z][0-9A-Z]'
                                    r'[0-9A-Z][0-9A-Z][0-9A-Z][0-9A-Z][0-9A-Z][0-9A-Z][0-9A-Z][0-9A-Z]', table)
                if not re_itog:
                    errors.append("Некорректный производсвенный заказ в таблице")
                table = table[table.find(" ") + 1:]
                re_itog = re.search(r'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]', table)
                if not re_itog:
                    errors.append("Некорректные наименование,сорт, размер,марка в таблице")
                    errors.append("Некорректный номенклатурный номер")
                else:
                    table = table[re_itog.span()[1] + 1:]
                re_itog = re.search(r' [0-9][0-9][0-9] ', table)
                if not re_itog:
                    errors.append("Некорректный Заводской номер детали в таблице")
                re_itog = re.search(r'[0-9][0-9][0-9] ', table)
                if not re_itog:
                    errors.append("Некорректный код Единицы измерения")
                else:
                    table = table[re_itog.span()[1]:]
            elif "Председатель0_должность" in json_for.keys():
                for i in range(0, 10):
                    if f"Председатель{i}_должность" in json_for.keys():
                        if json_for[f"Председатель{i}_должность"]:
                            errors.append(f"Отсутствует у Председателя{i} должность")
                        if json_for[f"Председатель{i}_подпись"] == {}:
                            errors.append(f"Отсутствует у Председателя{i} подпись")
                        if json_for[f"Председатель{i}_рашифровка_подписи"] == {}:
                            errors.append(f"Отсутствует у Председателя{i} расшифровка подписи")
            elif "Член_коммисии0_должность" in json_for.keys():
                for i in range(0, 10):
                    if f"Член_коммисии{i}_должность" in json_for.keys():
                        if json_for[f"Член_коммисии{i}_должность"]:
                            errors.append(f"Отсутствует у Члена комиссии{i} должность")
                        if json_for[f"Член_коммисии{i}_подпись"] == {}:
                            errors.append(f"Отсутствует у Члена комиссии{i} подпись")
                        if json_for[f"Член_коммисии{i}_рашифровка_подписи"] == {}:
                            errors.append(f"Отсутствует у Члена комиссии{i} расшифровка подписи")
            elif key == "Мат_отв_лицо_должность":
                if json_for[key] == {}:
                    errors.append("Некорректная должность материально ответственного лица")
            elif key == "Мат_отв_лицо_подпись":
                if json_for[key] == {}:
                    errors.append("Некорректная подпись материально ответственного лица")
            elif key == "Мат_отв_лицо_ФИО":
                if json_for[key] == {}:
                    errors.append("Некорректная расшифровка подписи материально ответственного лица")
            elif key == "Дата":
                date = json_for[key]
                try:
                    time.strptime(date, '%d/%m/%Y')
                except ValueError:
                    errors.append("Некорректно заполнена дата подписи материально ответственного лица")
            else:
                value = " ".join(json_for[key].split())
                if value:
                    json_for[key] = value
                else:
                    errors.append(f"Отсутствует значение для '{key}'")
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

FMU76_json = json.dumps(json_programm)
with open("FMU76.json", "w") as my_file:
    my_file.write(FMU76_json)
