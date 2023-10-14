import json
from pprint import pprint
from PyPDF2 import PdfFileReader as pd
import os

json_programm = {}
# Открываем файл конструктором With
for filename in os.listdir("dataset/ФМУ-76/"):
    try:
        with open("dataset/ФМУ-76/"+filename, 'rb') as pdf_file:
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
                        "АКТ_таблица", "УТВЕНикелинАЮ_должность", "УТВЕНикелинАЮ_хз", "УТВЕНикелинАЮ_дата",
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
                                json_for[f"Член_коммисии{id_komis}_подпись"] = " ".join(stroka[:stroka.find("(подпись)")].split())
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
                    keys = [
                        "Вторая таблица", "Председатель комисии", "Члены коммисии",
                        "Мат_отв_лицо_должность", "Мат_отв_лицо_подпись", "Мат_отв_лицо_ФИО", "Дата"
                    ]
                    elements = parse_text.replace("\n", " ").split("\\/")
                    for index in range(0, len(keys)):
                        if (keys[index] == "Председатель комисии"):
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
            json_for["Дата"] += " г."
        print(json_for)
        json_programm[filename] = json_for
    except:
        print("Произошла ошибка!")
FMU76_json = json.dumps(json_programm)
with open("FMU76.json", "w") as my_file:
    my_file.write(FMU76_json)



