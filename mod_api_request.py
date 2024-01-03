# формирование словаря из запроса
# поиск и выдача необходимой информации из запроса
# функции модуля принимают в качестве параметра ответ на api запрос в формате строки

def CupIsFinished(answer):    # функция определяет закончен ли сезон в кубке
# сезон закончен, если есть round: Final и его status: short: FT / AET / PEN / CANC / AWD / WO
# параметр: ответ на апи запрос fixtures в формате строки
    import traceback
    import datetime     # модуль для определния текущей даты
    DateNow = str(datetime.datetime.utcnow())[:19].replace(":", "-")    # текущая дата по UTC, отформатированная под строку для имени файла
    try:    # обработка исключений для определения ошибки и записи ее в bug_file в блоке except
        import json     # модуль формирование словаря из строки
        answer_dict = json.loads(answer)
        completion_status = ["FT", "AET", "PEN", "CANC", "AWD", "WO"]   # список статусов, обозначающих завершение матча
        # сезон закончен, если есть round: Final и его status: short: FT / AET / PEN / CANC / AWD / WO
        if answer_dict["response"][-1]["league"]["round"] == "Final" and \
            answer_dict["response"][-1]["fixture"]["status"]["short"] in completion_status:
            return("finished")
        else:
            return("in_progress")
    except: 
        with open("bug_files\\"+DateNow+".txt", 'w') as f:
            traceback.print_exc(file=f)     # создание файла ошибки с указанием файла кода и строки в необходимой
        return("pass")     # приводит к ожиданию следующего workflow для перерасчета этого кубка


def CupLast(answer):    # функция определяет дату последнего известного матча кубка
    import traceback
    import datetime     # модуль для определния текущей даты
    DateNow = str(datetime.datetime.utcnow())[:19].replace(":", "-")    # текущая дата по UTC, отформатированная под строку для имени файла
    try:    # обработка исключений для определения ошибки и записи ее в bug_file в блоке except
        import json     # модуль формирование словаря из строки
        answer_dict = json.loads(answer)
        last_date = datetime.datetime(2000, 1, 1)
        for fixture in answer_dict["response"]:
            fixt_date = fixture["fixture"]["date"]
            fixt_date = datetime.datetime(int(fixt_date[:4]), int(fixt_date[5:7]), int(fixt_date[8:10]))
            if fixt_date > last_date:
                last_date = fixt_date
        return(last_date)
    except: 
        with open("bug_files\\"+DateNow+".txt", 'w') as f:
            traceback.print_exc(file=f)     # создание файла ошибки с указанием файла кода и строки в необходимой
        return("pass")     # приводит к ожиданию следующего workflow для перерасчета этого кубка


def CupFirst(answer):    # функция определяет дату первого матча кубка
    import traceback
    import datetime     # модуль для определния текущей даты
    DateNow = str(datetime.datetime.utcnow())[:19].replace(":", "-")    # текущая дата по UTC, отформатированная под строку для имени файла
    try:    # обработка исключений для определения ошибки и записи ее в bug_file в блоке except
        import json     # модуль формирование словаря из строки
        answer_dict = json.loads(answer)
        first_date = datetime.datetime(2100, 1, 1)
        for fixture in answer_dict["response"]:
            fixt_date = fixture["fixture"]["date"]
            fixt_date = datetime.datetime(int(fixt_date[:4]), int(fixt_date[5:7]), int(fixt_date[8:10]))
            if fixt_date < first_date:
                first_date = fixt_date
        return(first_date)
    except: 
        with open("bug_files\\"+DateNow+".txt", 'w') as f:
            traceback.print_exc(file=f)     # создание файла ошибки с указанием файла кода и строки в необходимой
        return("pass")     # приводит к ожиданию следующего workflow для перерасчета этого кубка