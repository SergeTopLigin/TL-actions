# определение учитываемых нац кубковых турниров
# для всех кубковых турниров учитываются: незавершившийся турнир и предыдущий, если с его финала прошло <150 дней
# задача: определить дату финала минимальным количеством запросов
# оринетироваться на файлы "Tourn YY-YY prev/curr"
# First +год +месяц - для исключения лишних запросов до начала след сезона
# в течение сезона максимум - 1 запрос на турнир каждый день, 4 запроса за раз на восстановление турнира (подробнее - см ниже)

# ситуации 
# нет файлов "curr" и "prev": начало
# есть действительные "curr" и "prev": во время сезона
# есть действительный "prev": в межсезонье
# есть недейст "curr" и дейст "prev": турнир выпал из квотообразующих во время сезона
# есть недействительные "curr" и "prev": турнир выпал из квотообразующих во время одного из прошлых сезонов
# есть недействительный "prev": турнир выпал из квотообразующих во время одного из прошлых межсезоний

# в каталоге нет файлов "curr" и "prev"
    # запрос season = calc_date.year
    # если results != 0: (запрос до января)
        # сохранить запрос в файл "curr"
        # запрос season = calc_date.year -1
        # сохранить запрос в файл "prev"
    # если results == 0: (запрос после января или в межсезонье)
        # запрос season = calc_date.year -1
        # если есть round: Final и status: long: Match Finished: (сезон закончен, идет межсезонье)
            # сохранить запрос в файл "prev"
        # если отсутствует round: Final или его status: long: Not Started: (сезон идет)
            # сохранить запрос в файл "curr"
            # запрос season = calc_date.year -2
            # сохранить запрос в файл "prev"
# в каталоге есть действительные "curr" и "prev" (во время сезона) И
# calc_date < Last +1 из "curr"
    # pass
# в каталоге есть действительный "prev" (в межсезонье) И
# season "prev" = calc_date.year -1
    # если calc.date < First +год +месяц
        # pass
    # если calc.date >= First +год +месяц
        # запрос season = calc_date.year
        # если results != 0: (сезон начался)
            # сохранить запрос в файл "curr"
        # если results == 0: (сезон не начался)
            # pass
# в каталоге есть недейст "curr" и дейст "prev" (наступила дата Last +1 ИЛИ турнир выпал из квотообразующих во время сезона) И
# calc_date >= Last +1 из "curr" И
    # запрос season = calc_date.year
    # если results != 0: (запрос до января)
        # сохранить запрос в файл "curr"
        # если season "curr" -1 > season "prev"
            # удалить суффикс "prev" из имени файла
            # запрос season = "curr" -1
            # сохранить запрос в файл "prev"
    # если results == 0: (запрос после января или в межсезонье)
        # запрос season = calc_date.year -1
        # если отсутствует round: Final или его status: long: Not Started (сезон идет)
            # сохранить запрос в файл "curr"
            # если season "curr" -1 > season "prev"
                # удалить суффикс "prev" из имени файла
                # запрос season = "curr" -1
                # сохранить запрос в файл "prev"
        # если есть round: Final и status: long: Match Finished: (сезон закончен, идет межсезонье)
            # сохранить запрос в файл и изменить его суффикс "curr" на "prev"
            # удалить суффикс "prev" из имени предыдущего файла "prev"
# в каталоге есть недействительные "curr" и "prev" (турнир выпал из квотообразующих во время одного из прошлых сезонов) 
# если в запросе season "curr" есть round: Final и status: long: Match Finished
    # удалить суффиксы "curr" и "prev" из имен файлов
    # выполнить действия из условия: в каталоге нет файлов "curr" и "prev"
    # если есть файл по YY-YY дублирующий только что созданный "prev"
        # удалить этот файл без суффикса
# в каталоге есть недействительный "prev" (турнир выпал из квотообразующих во время одного из прошлых межсезоний)
# если в запросе season "prev" +1 есть round: Final и status: long: Match Finished
    # удалить суффикс "prev" из имени файла
    # выполнить действия из условия: в каталоге нет файлов "curr" и "prev"

# ОБЪЕДИНЕНИЕ
# макс 3 запроса в один день один раз в начале
# if в каталоге нет файлов "curr" и "prev"
    # запрос season = calc_date.year
    # if results != 0: (запрос до января)
        # сохранить запрос в файл "curr"
        # запрос season = calc_date.year -1
        # сохранить запрос в файл "prev"
    # else results == 0: (запрос после января или в межсезонье)
        # запрос season = calc_date.year -1
        # if есть round: Final и status: long: Match Finished: (сезон закончен, идет межсезонье)
            # сохранить запрос в файл "prev"
        # else отсутствует round: Final или его status: long: Not Started: (сезон идет)
            # сохранить запрос в файл "curr"
            # запрос season = calc_date.year -2
            # сохранить запрос в файл "prev"
# 1 запрос в 20 дней, 1 запрос каждый день после последнего матча стадии до жеребьевки следующей, макс 4 запроса один раз для возобновления турнира
# elif в каталоге есть "curr" и "prev" (актуальные или нет)
    # if calc_date < Last +1 из "curr" ("curr" актуальный)
        # pass
    # else calc_date >= Last +1 из "curr" (наступила дата Last +1 ИЛИ турнир выпадал из квотообразующих и возобновляется)
        # запрос season = "curr"
        # if отсутствует round: Final или его status: long: Not Started
            # сохранить запрос в файл "curr"
            # if season "curr" -1 > season "prev"
                # удалить из имени файла суффикс "prev"
                # запрос season "curr" -1
                # сохранить запрос в файле "prev"
        # elif есть round: Final и status: long: Match Finished ("curr" и "prev" НЕ актуальны,турнир выпал из квотообразующих во время одного из прошлых сезонов)
            # сохранить запрос в файл "curr"
            # удалить суффиксы "curr" и "prev" из имен файлов
            # выполнить действия из условия: в каталоге нет файлов "curr" и "prev"
            # если есть файл по YY-YY дублирующий только что созданный "prev"
                # удалить этот файл без суффикса
# скорее всего 1 запрос для выхода из межсезонья, макс 3 запроса для возобновления турнира
# elif в каталоге есть только "prev" (актуальный или нет)
    # if calc.date < First +год +месяц "prev"
        # pass
    # else calc.date >= First +год +месяц "prev"
        # запрос season = calc_date.year
        # if results != 0: (сезон начался)
            # сохранить запрос в файл "curr"
            # if season "curr" -1 > season "prev"
                # удалить из имени файла суффикс "prev"
                # запрос season "curr" -1
                # сохранить запрос в файл "prev"
        # else results == 0: (сезон не начался или запрос весной, а файл старого сезона)
            # запрос season = calc_date.year -1
            # if отсутствует round: Final или его status: long: Not Started (запрос весной, а файл старого сезона)
                # сохранить запрос season = calc_date.year -1 в файл "curr"
                # if season "curr" -1 > season "prev"
                    # удалить из имени файла суффикс "prev"
                    # запрос season "curr" -1
                    # сохранить запрос в файл "prev"
            # elif есть round: Final и status: long: Match Finished (сезон не начался)
                # if season "prev" < calc_date.year -1
                    # удалить из имени файла суффикс "prev"
                    # сохранить запрос в файл "prev"
# ИТОГО: 3 запроса в начале, 1 запрос в 20 дней для поддержания турнира, макс 4 запроса один раз для возобновления турнира


import time # модуль для паузы и определения текущего UEFA club set
import datetime
import os   # импорт модуля работы с каталогами
import mod_apisports_key    # модуль с ключом аккаунта api
import mod_Nat_tournaments  # модуль словаря {Association:[AssType,Season,Tournament,TournID,TournType]}

def func_cup_files(Cup, calc_date):

    Ass_TournIdType = mod_Nat_tournaments.Nat_Tournaments()     # словарь {Association:[AssType,Season,Tournament,TournID,TournType]}
    # определение ID турнира    
    for ass in Ass_TournIdType:
        for AssType in Ass_TournIdType[ass]:
            if Cup == AssType[0]:
                CupID = AssType[3]
                break

    file_find_flag = 0  # флаг наличия в каталоге файла
    # if в каталоге нет файлов "curr" и "prev"
    for Cup_file in os.listdir('tournaments/'):
        if Cup_file.find(Cup) != -1 and (Cup_file.find("curr") != -1 or Cup_file.find("prev") != -1):
            file_find_flag = 1
            break
    if file_find_flag == 0:
        # запрос season = calc_date.year
        try:
            api_date_year = mod_apisports_key.api_key("/fixtures?league="+CupID+"&season="+calc_date.year)
        except: # исключение "не удалось создать запрос"
            return("pass")   # приводит к ожиданию следующего workflow для перерасчета этого кубка
        time.sleep(7)   # лимит: 10 запросов в минуту: между запросами 7 секунд: https://dashboard.api-football.com/faq Technical
        # if results != 0: (запрос до января)
        if api_date_year[api_date_year.find("results")+9 : api_date_year.find("results")+10] != "0":
            # сохранить запрос в файл "curr"
            with open("tournaments\\"+Cup+" "+str(calc_date.year)[2:]+"-"+str(calc_date.year+1)[2:]+" curr.txt", 'w') as f:    # "Tourn YY-YY prev/curr"
                f.write(api_date_year)
            # запрос season = calc_date.year -1
            try:
                api_date_prev_year = mod_apisports_key.api_key("/fixtures?league="+CupID+"&season="+str(calc_date.year-1))
            except: # исключение "не удалось создать запрос"
                return("pass")   # приводит к ожиданию следующего workflow для перерасчета этого кубка
            time.sleep(7)   # лимит: 10 запросов в минуту: между запросами 7 секунд: https://dashboard.api-football.com/faq Technical
            # сохранить запрос в файл "prev"
            with open("tournaments\\"+Cup+" "+str(calc_date.year-1)[2:]+"-"+str(calc_date.year)[2:]+" prev.txt", 'w') as f:    # "Tourn YY-YY prev/curr"
                f.write(api_date_prev_year)
        # else results == 0: (запрос после января или в межсезонье)
        else:
            # запрос season = calc_date.year -1
            try:
                api_date_prev_year = mod_apisports_key.api_key("/fixtures?league="+CupID+"&season="+str(calc_date.year-1))
            except: # исключение "не удалось создать запрос"
                return("pass")   # приводит к ожиданию следующего workflow для перерасчета этого кубка
            time.sleep(7)   # лимит: 10 запросов в минуту: между запросами 7 секунд: https://dashboard.api-football.com/faq Technical

            # if есть round: Final и status: long: Match Finished: (сезон закончен, идет межсезонье)
                # сохранить запрос в файл "prev"
            # else отсутствует round: Final или его status: long: Not Started: (сезон идет)
                # сохранить запрос в файл "curr"
                # запрос season = calc_date.year -2
                # сохранить запрос в файл "prev"


# вспомогательные переменные и вызов функции (удалить после тестирования)
Cup = "ENG Cup"     # в соответствии с AssType словаря из mod_Nat_tournaments
calc_date = datetime.datetime(2023, 8, 7)
if func_cup_files(Cup, calc_date) == "pass":
    print("ожидание следующего workflow")