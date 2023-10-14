import json
from PyPDF2 import PdfFileReader as pd
import os
json_programm = {}
#Открываем файл конструктором With
for filename in os.listdir("dataset/М-11/"):
    with open("dataset/М-11/"+filename, 'rb') as pdf_file:
        pdf_open_reader = pd(pdf_file) #Открываем PDF на чтение
        #Циклом обходим все страницы книги и выводим их содержание на печать
        parse_text = ""
        for page_num in range(pdf_open_reader.numPages):
            pdf_page = pdf_open_reader.getPage(page_num)
            # print(f"Page:  {page_num +1}")
            text = pdf_page.extractText("")
            # Логика прыжком по значениям
            list = {
                "ТРЕБОВАНИЕ-НАКЛАДНАЯ №  ": "\n",
                "Организация ": "по ОКПО",
                "по ОКПО ":"\n",
                "Структурное\nподразделение": "Отправитель",
                "(работ,\nуслуг)": "Через кого", # Таблица
                "Через кого": "Затребовал",
                "Затребовал": "Разрешил",
                "Разрешил": "Материальные",
                "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16": "Отпустил",
                "Отпустил" : "(должность)",
                "(должность)":"(подпись)",
                "(подпись)":"(расшифровка подписи)Получил",
                "расшифровка подписи)Получил":"(должность)",
                "должность)":"(подпись)",
                "подпись)":"(расшифровка подписи)",
                "расшифровка подписи)":"Документ подписан электронной подписью",
            }
            for str_start, str_end in list.items():
                index_start = text.find(str_start) + len(str_start)
                index_end = text[index_start:].find(str_end)
                parse_text += text[index_start: index_start+ index_end] + " \\/"
                text=text[index_start+index_end:]

    keys = [
        "ТРЕБОВАНИЕ-НАКЛАДНАЯ №", "Организация", "по ОКПО", "Структурное подразделение",
        "Первая таблица", "Через кого", "Затребовал", "Разрешил", "Вторая таблица", "Отпустил_должность",
        "Отпустил_подпись", "Отпустил_ФИО", "Получил_должность", "Получил_подпись", "Получил_ФИО"
    ]
    json_for = {}
    elements = parse_text.replace("\n", " ").split("\\/")
    for index in range(0, len(keys)):
        if keys[index] == "Структурное подразделение":
            json_for[keys[index]] = " ".join(elements[index].split())[:-4]
            json_for["БЕ"] = " ".join(elements[index].split())[-4:]
        else:
            json_for[keys[index]] = " ".join(elements[index].split())
    json_programm[filename] = json_for
    print(json_for)

M_11_json = json.dumps(json_programm)
with open("M-11.json", "w") as my_file:
    my_file.write(M_11_json)