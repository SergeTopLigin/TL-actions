def UEFA_club_set(october_year):   # определение текущего UEFA club set: 
                    # множества (удаление дубликатов) клубов из fixtures турниров за октябрь 2023 при запросе 01.09.23-31.08.24
    import os   # импорт модуля работы с каталогами
    import time # модуль для паузы и определения текущего UEFA club set
    import mod_apisports_key    # модуль с ключом аккаунта api
    id_UEFA_Leagues = (2, 3, 848) # кортеж (неизменяемый список) id UEFA Leagues (UCL, UEL, UECL)
    
    # загрузка в папку cache api-запросов fixtures турниров за октябрь искомого года
    for id_league in id_UEFA_Leagues: # цикл по лигам УЕФА
        try:
            api_answer = mod_apisports_key.api_key("/fixtures?league="+str(id_league)+"&season="+str(october_year)+
                                                    "&from="+str(october_year)+"-10-01&to="+str(october_year)+"-10-31")
            with open("cache\\"+str(id_league)+".txt", 'w') as f:
                f.write(api_answer)
            time.sleep(7)   # лимит: 10 запросов в минуту: между запросами 7 секунд: https://dashboard.api-football.com/faq Technical
        except: # исключение "не удалось создать запрос"
            return("prev_season")   # приводит к использованию UEFA club set прошлого сезона
    
    # набор UEFA club set из созданных файлов
    UEFA_clubs = [] # список клубов в UEFA club set
    for id_league in id_UEFA_Leagues: # цикл по лигам УЕФА
        try:
            with open("cache\\"+str(id_league)+".txt", 'r') as f:
                # проверка наличия fixtures в октябре: если хотя бы в одном из файлов не будет игр - использовать UEFA club set прошлого сезона 
                # проверка значения поля results
                for line in f:  # цикл по строкам
                    kursor = 0  # начальная позиция курсора
                    end_substr = 0   # позиция конца искомой подстроки
                    kursor = line.find('results":',0) +9    # переместить курсор перед искомой подстрокой
                    end_substr = line.find(',',kursor)    # определение конца искомой подстроки (поиск символа , после позиции курсора)
                    results = int(line[kursor:end_substr])  # извлечение значения поля results
                    if results == 0:    # если в файле нет игр
                        return("prev_season")   # использовать UEFA club set прошлого сезона
                # набор UEFA club set
                    while True:     # пока поиск не дошел до конца строки
                        if line.find('"teams"',kursor) ==-1:
                            break
                        kursor = line.find('"teams"',kursor)    # переместить курсор перед подстрокой "teams"
                        for х in range(1, 3):
                            kursor = line.find('"id":',kursor)+5    # переместить курсор за подстроку "id":
                            end_substr = line.find(',',kursor)    # определение конца искомой подстроки (поиск символа , после позиции курсора)
                            UEFA_club_id = line[kursor:end_substr]     # извлечение id клуба
                            kursor = line.find('"name":"',kursor)+8    # переместить курсор за подстроку "name":"
                            end_substr = line.find('"',kursor)    # определение конца искомой подстроки (поиск символа " после позиции курсора)
                            UEFA_club = line[kursor:end_substr]     # извлечение названия клуба
                            # UEFA_club = bytes(UEFA_club, "utf-8").decode("unicode_escape")   # декодирование символов не utf-8
                            # if UEFA_club.find("\\"): UEFA_club = UEFA_club.replace("\\","") # удаление из названия символов \\
                            if [UEFA_club, UEFA_club_id] not in UEFA_clubs:
                                UEFA_clubs.append([UEFA_club, UEFA_club_id])  # и добавление его в список
        except FileNotFoundError:   # исключение "нет файла"
            return("prev_season")   # приводит к использованию UEFA club set прошлого сезона

    # создание файла UEFA club set
    with open("club_set\\UefaClubSet_"+str(october_year)+"-"+str(october_year+1)+".txt", 'w') as f:
        for club in range(0, len(UEFA_clubs)):
            if club == len(UEFA_clubs)-1: f.write(UEFA_clubs[club][0]+";   id:"+UEFA_clubs[club][1]+".")
            else: f.write(UEFA_clubs[club][0]+";   id:"+UEFA_clubs[club][1]+".\n")
    
    # чистка папки cache
    for id_league in id_UEFA_Leagues: # цикл по лигам УЕФА
        os.remove("cache\\"+str(id_league)+".txt")