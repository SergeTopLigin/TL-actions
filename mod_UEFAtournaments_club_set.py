# жеребьевка группового этапа еврокубков проходит в конце августа
# для получения group set следует с 01.09 ежедневно делать запрос на игры в октябре, пока в папке club set/ не будет сформирован соответсвующий файл
# жеребьевка 1 стадии плей-офф еврокубков проходит на следующей неделе после 6-го тура групп в середине декабря. 1/8 проходит в феврале/марте
# для получения playoff set следует с 16.12 ежедневно делать запрос на игры в феврале и марте, пока в папке club set/ не будет сформирован соответсвующий файл

def UEFAtournaments_club_set(tournament, season, stage):   # входящие параметры: турнир, сезон, стадия
    # список из множества (удаление дубликатов) клубов из fixtures турниров за необходимые месяцы
    import os   # импорт модуля работы с каталогами
    import time # модуль для паузы и определения текущего UEFA club set
    import mod_apisports_key    # модуль с ключом аккаунта api
    
    # определение id турнира
    if tournament == "UCL": id_league = 2
    elif tournament == "UEL": id_league = 3
    elif tournament == "UECL": id_league = 848

    # определение года начала сезона (для запроса)
    first_year = season[:4]

    # определение дат from-to
    if stage == "group set":
        from_to = "from="+str(season[:4])+"-10-01&to="+str(season[:4])+"-10-31"
    elif stage == "playoff set":
        from_to = "from="+str(season[5:])+"-02-01&to="+str(season[5:])+"-03-31"

    # загрузка в папку cache api-запросов fixtures турниров за октябрь (для групп) или февраль-март (для плейофф) искомого сезона
    try:
        api_answer = mod_apisports_key.api_key("/fixtures?league="+str(id_league)+"&season="+str(first_year)+"&"+from_to)
        with open("cache\\"+tournament+" "+season+" "+stage+" request.txt", 'w') as f:
            f.write(api_answer)
        time.sleep(7)   # лимит: 10 запросов в минуту: между запросами 7 секунд: https://dashboard.api-football.com/faq Technical
    except: # исключение "не удалось создать запрос"
        return("use_prev")   # приводит к использованию предыдущего tournament_club_set
    
    # набор tournament_club_set из созданного файла
    tournament_club_set = [] # список клубов турнира
    try:
        with open("cache\\"+tournament+" "+season+" "+stage+" request.txt", 'r') as f:
            # проверка наличия fixtures: если в файле не будет игр - использовать предыдущий tournament_club_set
            # проверка значения поля results
            for line in f:  # цикл по строкам
                kursor = 0  # начальная позиция курсора
                end_substr = 0   # позиция конца искомой подстроки
                kursor = line.find('results":',0) +9    # переместить курсор перед искомой подстрокой
                end_substr = line.find(',',kursor)    # определение конца искомой подстроки (поиск символа , после позиции курсора)
                results = int(line[kursor:end_substr])  # извлечение значения поля results
                if results == 0:    # если в файле нет игр
                    return("use_prev")   # использовать предыдущий tournament_club_set
            # набор tournament_club_set
                while True:     # пока поиск не дошел до конца строки
                    if line.find('"teams"',kursor) ==-1:
                        break
                    kursor = line.find('"teams"',kursor)    # переместить курсор перед подстрокой "teams"
                    for х in range(1, 3):
                        kursor = line.find('"id":',kursor)+5    # переместить курсор за подстроку "id":
                        end_substr = line.find(',',kursor)    # определение конца искомой подстроки (поиск символа , после позиции курсора)
                        tournament_club_id = line[kursor:end_substr]     # извлечение id клуба
                        kursor = line.find('"name":"',kursor)+8    # переместить курсор за подстроку "name":"
                        end_substr = line.find('"',kursor)    # определение конца искомой подстроки (поиск символа " после позиции курсора)
                        tournament_club = line[kursor:end_substr]     # извлечение названия клуба
                        if [tournament_club, tournament_club_id] not in tournament_club_set:
                            tournament_club_set.append([tournament_club, tournament_club_id])  # и добавление его в список
    except FileNotFoundError:   # исключение "нет файла"
        return("use_prev")   # приводит к использованию предыдущего tournament_club_set

    # создание файла tournament_club_set
    with open("club_set\\"+tournament+" "+season+" "+stage+".txt", 'w') as f:
        for club in range(0, len(tournament_club_set)):
            if club == len(tournament_club_set)-1: f.write(tournament_club_set[club][0]+";   id:"+tournament_club_set[club][1]+".")
            else: f.write(tournament_club_set[club][0]+";   id:"+tournament_club_set[club][1]+".\n")
    
    # чистка папки cache
    os.remove("cache\\"+tournament+" "+season+" "+stage+" request.txt")