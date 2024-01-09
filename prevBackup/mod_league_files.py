# модуль актуализации файлов нац лиг по запросу fixtures для определения club set
# если по api запросу results != 0 - сохранить файл лиги, иначе - pass
def set_league_files(League, Season, LeagueID, FixtSeason):     # League должен соответствовать названию турнира в mod_Nat_tournaments.Nat_Tournaments[ass][0]
                                                                # Season = YY-YY (как в названии файла)
                                                                # FixtSeason = YYYY для fixtures
    import traceback
    import datetime     # модуль для определния текущей даты
    DateNow = str(datetime.datetime.utcnow())[:19].replace(":", "-")    # текущая дата по UTC, отформатированная под строку для имени файла
    try:    # обработка исключений для определения ошибки и записи ее в bug_file в блоке except
        import os   # импорт модуля работы с каталогами
        for League_file in os.listdir('tournaments/'):
            if League_file.find(League) != -1 and League_file.find(Season) != -1:
                return()
        import mod_apisports_key    # модуль с ключом аккаунта api
        api_league = mod_apisports_key.api_key("/fixtures?league="+LeagueID+"&season="+FixtSeason)
        with open("tournaments\\"+League+" "+Season+".txt", 'w') as f:    # "Tourn YY-YY"
            f.write(api_league)
    except: 
        with open("bug_files\\"+DateNow+".txt", 'w') as f:
            traceback.print_exc(file=f)     # создание файла ошибки с указанием файла кода и строки в необходимой
        return("pass")     # приводит к ожиданию следующего workflow для перерасчета этой лиги