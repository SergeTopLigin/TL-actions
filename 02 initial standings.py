import datetime
import math
import os   # импорт модуля работы с каталогами
import mod_UEFA_club_set    # модуль создания UEFA club set
import mod_UEFAtournaments_club_set    # модуль создания UEFA tournament club set

# определение UEFA Club Set
# в UEFA Club Set входят клубы, участвующие/участвовавшие в последней групповой стадии еврокубков, определяющиеся обычно к 01.09
# для определения UEFA Club Set используется API запрос fixtures октября
# определение имени необходимого файла
# при запросе до 01.09 требуется файл, определенный октябрем прошлого года
# при запросе после 31.08 требуется файл, определенный октябрем текущего года
DateNow = datetime.datetime.utcnow()    # текущая дата по UTC
if DateNow.month > 8:
    filename = "UefaClubSet_"+str(DateNow.year)+"-"+str(DateNow.year+1)
    october_year = DateNow.year
else: 
    filename = "UefaClubSet_"+str(DateNow.year-1)+"-"+str(DateNow.year)
    october_year = DateNow.year-1
# определить требуется ли API запрос или файл уже есть в базе
create_flag = 1    # флаг необходимости создания файла
for Set_file in os.listdir('club_set/'):  
# прочитать названия файлов из каталога club_set
    if Set_file.find(filename)!=-1:  # если в каталоге club_set есть текущий UEFA Club Set
        create_flag = 0    # опустить флаг создания файла
if create_flag == 1:   # если флаг создания файла поднят - 
    # создать файл UEFA Club Set
    if mod_UEFA_club_set.UEFA_club_set(october_year) == "prev_season":   # или использовать UEFA club set прошлого сезона при ошибках
        filename = "UefaClubSet_"+str(DateNow.year-1)+"-"+str(DateNow.year)
UefaClubSetID = []    # создание списка id из файла UefaClubSet
with open("club_set\\"+filename+".txt", 'r') as f:
    for line in f:  # цикл по строкам
        kursor = line.find('id:',0) +3    # переместить курсор перед искомой подстрокой
        end_substr = line.find('.',kursor)    # определение конца искомой подстроки (поиск символа "." после позиции курсора)
        UefaClubSetID.append(int(line[kursor:end_substr]))

# создание словарей TL standings на 01.07.23
# два словаря: {id:rate} для сортировки по убыванию рейтинга И {id:[name,nat,...]} - для хранения турнирных данных
TL_standings_rate = {}  # словарь {id:rate} для сортировки по рейтингу
TL_standings_data = {}  # словарь {id:[name,nat,...]} - для хранения турнирных данных
import csv
with open('UEFA club ranking '+str(october_year)+' name;ID;nat;rate.csv') as f:
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        TL_standings_rate[int(row[1])] = float(row[3])  # создание словаря {id:rate}
        TL_standings_data[int(row[1])] = [str(row[0]), str(row[2])]  # создание словаря {id:[name,nat,...]}


# здесь начинается циклическая часть с перерасчетами на каждую дату
# если во входящих в дату standings появилось более одного клуба из одной асоциации, fixtures турниров которой не были запрошены ранее, - создать такие запросы
# результаты игр брать из базы созданных ранее запросов fixtures

# цикл на каждую дату с 01.07.23 по сегодня
calc_date = datetime.datetime(2023, 7, 1)
while calc_date + datetime.timedelta(days=1) < DateNow: # datetime.datetime(2023, 12, 12):
    print(calc_date)    # вывод на экран расчетной даты

    Association_rating = {}     # словарь рейтингов и квот ассоциаций {Association:[Rating,Quota]}
    Ass_TournRateQuot = {}     # общий словарь рейтингов и квот всех турниров {Association:[Tournament,Rating,Quota]}
    

    # Association rating & quota

    # Association rating = total club set SUM(pts+1.2) in TL standigs
    print("Association ratings & quotas:")
    # определение UEFA rating
    UEFA_rating = 0
    for ID in TL_standings_rate:
        for SetID in UefaClubSetID:
            if ID == SetID:
                UEFA_rating += TL_standings_rate[ID] + 1.2
                break
    UEFA_rating = round(UEFA_rating, 2)
    # определение National ratings
    Nations_list = []    # создание списка национальных ассоциаций, имеющих представителство в TL standings
    Nations_list_rate = []  # и списка их рейтингов
    for ID in TL_standings_data:
        Nations_list.append(TL_standings_data[ID][1])
    Nations_list = list(set(Nations_list))  # избавляемся от повторных элементов преобразованием во множество и обратно
    for country in Nations_list:
        Nation_rate = 0   # инициализация рейтинга конкретной ассоциации
        for ID in TL_standings_data:
            if country == TL_standings_data[ID][1]:
                Nation_rate += TL_standings_rate[ID] + 1.2
        Nations_list_rate.append(round(Nation_rate, 2))
    # формирование общего словаря рейтингов ассоциаций
    Association_rating = dict(zip(Nations_list, Nations_list_rate))   # объединение списков нац ассоциаций и их рейтингов в одном словаре
    Association_rating["UEFA"] = UEFA_rating     # добавляем в словарь ассоциацию УЕФА
    Association_rating = dict(sorted(Association_rating.items(), key=lambda x: x[1], reverse=True))   # сортировка словаря рейтинга ассоциаций по убыванию рейтинга

    # Association quota = ˻ 50 * Assoiation rating / Σ (Assoiation ratings) ˼
    Associations_rate_sum = 0   # сумма рейтингов ассоциаций
    for ass_n in Association_rating:
        Associations_rate_sum += Association_rating[ass_n]
    Associations_rate_sum = round(Associations_rate_sum, 2)
    for ass_n in Association_rating:
        Association_quota = math.floor(50 * Association_rating[ass_n] / Associations_rate_sum)
        Association_rating[ass_n] = [Association_rating[ass_n], Association_quota]    # увеличение вложенности словаря ассоциаций: {ass:[rate,quota]}
    # учет квоты TL на 10 лидеров
    Association_rating["TopLiga"] = [1, 10]

    # сортировка словаря рейтинга ассоциаций по убыванию квот
    Association_rating = dict(sorted(Association_rating.items(), key=lambda x: x[1][1], reverse=True))   

    # вывод на экран Association rating & quota
    for ass_n in Association_rating:
        print("{0:8.2f}  {1:2}  {2:}".format(Association_rating[ass_n][0], Association_rating[ass_n][1], ass_n))
    


    # Tournament rating & quota

    # UEFA tournaments rating & quota
    # определение UEFA tournaments club set
    # жеребьевка группового этапа еврокубков проходит в конце августа
    # для получения group set следует с 01.09 ежедневно делать запрос на игры в октябре, пока в папке club set/ не будет сформирован соответсвующий файл
    # жеребьевка 1 стадии плей-офф еврокубков проходит на следующей неделе после 6-го тура групп в середине декабря. 1/16 проходит в феврале/марте
        # победители групп (до сезона 24/25) или 1-8 места общего этапа (с сезона 24/25) начинают с 1/8, жеребьевка которой проходит после 1/16
    # для получения playoff set (до сезона 24/25) следует с 16.12 ежедневно делать запрос на игры в феврале и марте, 
        # пока в папке club set/ не будет сформирован соответсвующий файл
        # а также запрос standings на 1-е места групп для UEL и UECL, если запрос fixtures на февраль-март дал результат
    # для получения playoff set (с сезона 24/25) с 01.02 запрашивать standings на 1-24 места в общем групповом этапе во всех трех турнирах 
    # во время групповой стадии с 01.09 требуются текущий group set и playoff set прошлого сезона; 
    # после завершения групповой стадии по 31.08 требуется последний playoff set
    
    # UEFA tournaments club set
    # определение имени и наличия необходимого файла, необходимости api-запроса
    UEFA_tourn_club_set = []   # список tournament club set
    UEFA_tourn_club_set_ID = {}    # словарь ID клубов из club sets {club_set:[id]}
    UEFA_leagues = ("UCL", "UEL", "UECL")
    # определение имен файлов tournament club set
    if calc_date < datetime.datetime(2024, 9, 1):    # до сезона 24/25
        for league in UEFA_leagues:
            if (calc_date.month > 8 and calc_date.month < 12) or (calc_date.month == 12 and calc_date.day < 16):
                UEFA_tourn_club_set.append([league, str(calc_date.year-1)+"-"+str(calc_date.year), "playoff set"])
                UEFA_tourn_club_set.append([league, str(calc_date.year)+"-"+str(calc_date.year+1), "group set"])
            elif calc_date.month < 9:
                UEFA_tourn_club_set.append([league, str(calc_date.year-1)+"-"+str(calc_date.year), "playoff set"])
            elif calc_date.month == 12 and calc_date.day > 15:
                UEFA_tourn_club_set.append([league, str(calc_date.year)+"-"+str(calc_date.year+1), "playoff set"])
    elif calc_date > datetime.datetime(2024, 8, 31):    # с сезона 24/25
        for league in UEFA_leagues:
            if calc_date.month > 8:
                UEFA_tourn_club_set.append([league, str(calc_date.year-1)+"-"+str(calc_date.year), "playoff set"])
                UEFA_tourn_club_set.append([league, str(calc_date.year)+"-"+str(calc_date.year+1), "group set"])
            elif calc_date.month == 1:
                UEFA_tourn_club_set.append([league, str(calc_date.year-1)+"-"+str(calc_date.year), "group set"])
            else:
                UEFA_tourn_club_set.append([league, str(calc_date.year-1)+"-"+str(calc_date.year), "playoff set"])
    # определение наличия необходимого файла или необходимости api-запроса
    i = 0
    while i < len(UEFA_tourn_club_set):
        create_flag = 1    # флаг необходимости создания файла
        for Set_file in os.listdir('club_set/'):  
        # прочитать названия файлов из каталога club_set
            if Set_file.find(str(UEFA_tourn_club_set[i][0]+" "+UEFA_tourn_club_set[i][1]+" "+UEFA_tourn_club_set[i][2]))!=-1:  
                # если в каталоге club_set есть необходимый файл
                create_flag = 0    # опустить флаг создания файла
        if create_flag == 1:   # если флаг создания файла поднят - 
            # создать необходимый файл
            if mod_UEFAtournaments_club_set.UEFAtournaments_club_set(UEFA_tourn_club_set[i][0], UEFA_tourn_club_set[i][1], UEFA_tourn_club_set[i][2]) == \
            "use_prev":   
            # или использовать предыдущий club set при ошибках
                if calc_date < datetime.datetime(2024, 9, 1):    # до сезона 24/25
                    # если ошибка при запросе group set - использовать предыдущий playoff set, который уже есть в UEFA_tourn_club_set
                    if UEFA_tourn_club_set[i][2] == "group set":
                        # удалить UT_club_set из UEFA_tourn_club_set
                        del UEFA_tourn_club_set[i]
                        i -= 1   # смещение на итерацию назад, тк после удаления элемента номерация смещается
                    # если ошибка при запросе playoff set, выполненном 01.09-15.12
                    elif UEFA_tourn_club_set[i][2] == "playoff set" and (calc_date.month > 8 and calc_date.month < 12) or \
                    (calc_date.month == 12 and calc_date.day < 16):
                        # удалить UT_club_set из UEFA_tourn_club_set
                        del UEFA_tourn_club_set[i]
                        i -= 1
                    # если ошибка при запросе playoff set, выполненном после декабря
                    elif UEFA_tourn_club_set[i][2] == "playoff set" and calc_date.month < 9:
                        # изменить его на group set текущего розыгрыша
                        UEFA_tourn_club_set[i][1] = str(calc_date.year-1)+"-"+str(calc_date.year)
                        UEFA_tourn_club_set[i][2] = "group set"
                    # если ошибка при запросе playoff set, выполненном в декабре
                    elif UEFA_tourn_club_set[i][2] == "playoff set" and (calc_date.month == 12 and calc_date.day > 15):
                        # изменить его на group set текущего розыгрыша
                        UEFA_tourn_club_set[i][1] = str(calc_date.year)+"-"+str(calc_date.year+1)
                        UEFA_tourn_club_set[i][2] = "group set"
                elif calc_date > datetime.datetime(2024, 8, 31):    # с сезона 24/25
                    # если ошибка при запросе group set, выполненный до января - использовать предыдущий playoff set, который уже есть в UEFA_tourn_club_set
                    if UEFA_tourn_club_set[i][2] == "group set":
                        # удалить UT_club_set из UEFA_tourn_club_set
                        del UEFA_tourn_club_set[i]
                        i -= 1   # смещение на итерацию назад, тк после удаления элемента номерация смещается
                    # если ошибка при запросе playoff set, выполненном с сентября по декабрь
                    elif UEFA_tourn_club_set[i][2] == "playoff set" and calc_date.month > 8:
                        # удалить UT_club_set из UEFA_tourn_club_set
                        del UEFA_tourn_club_set[i]
                        i -= 1
                    # если ошибка при запросе group set, выполненном в январе
                    elif UEFA_tourn_club_set[i][2] == "group set" and calc_date.month == 1:
                        # изменить его на playoff set прошлого розыгрыша
                        UEFA_tourn_club_set[i][1] = str(calc_date.year-2)+"-"+str(calc_date.year-1)
                        UEFA_tourn_club_set[i][2] = "playoff set"
                    # если ошибка при запросе playoff set, выполненном с февраля по август
                    elif UEFA_tourn_club_set[i][2] == "playoff set" and (calc_date.month < 9 and calc_date.month > 1):
                        # изменить его на group set текущего розыгрыша
                        UEFA_tourn_club_set[i][1] = str(calc_date.year-1)+"-"+str(calc_date.year)
                        UEFA_tourn_club_set[i][2] = "group set"
        # заполнение словаря ID клубов из club sets
        LegueClubSetID = []    # создание списка id из файла UefaClubSet
        with open("club_set\\"+UEFA_tourn_club_set[i][0]+" "+UEFA_tourn_club_set[i][1]+" "+UEFA_tourn_club_set[i][2]+".txt", 'r') as f:
            for line in f:  # цикл по строкам
                kursor = line.find('id:',0) +3    # переместить курсор перед искомой подстрокой
                end_substr = line.find('.',kursor)    # определение конца искомой подстроки (поиск символа "." после позиции курсора)
                LegueClubSetID.append(int(line[kursor:end_substr]))
        UEFA_tourn_club_set_ID[str(UEFA_tourn_club_set[i][0]+" "+UEFA_tourn_club_set[i][1]+" "+UEFA_tourn_club_set[i][2])] = LegueClubSetID
        i += 1
    
    # Tournament rating = total club set SUM(pts+1.2) in TL standigs / Number of clubs in the set
    print("Tournaments ratings & quotas:")
    # определение UEFA tournaments rating
    # определение наличия временного фактора при постепенном перетекании рейтинга из плейофф прошлого турнира в групповой этап текущего
    time_factor = 0     # инициализация временного фактора
    # и формирование списка UEFA_club_sets
    UEFA_club_sets = []
    for club_set in UEFA_tourn_club_set_ID:     # поиск слова group в названии ключа словаря
        if club_set.find("group") != -1:
            # при наличии слова group - задействовать временной фактор
            first_year = club_set[club_set.find(" ")+1:club_set.find(" ")+5]    # определение года начала турнира group set
            # кол-во дней прошедших с 01.09, деленное на 100 = % использования group set
            time_factor = min((calc_date - datetime.datetime(int(first_year), 8, 31)) / (datetime.timedelta(days=1) * 100), 1)  
        UEFA_club_sets.append(club_set)
    Ass_TournRateQuot["UEFA"] = UEFA_club_sets  # начальное заполнение значений ключа UEFA списком длиной, равной количеству турниров UEFA
    i = 0   # счетчик итераций для индексов списка турниров UEFA в словаре Ass_TournRateQuot
    for club_set in UEFA_tourn_club_set_ID:     # для каждого ключа словаря (рассматриваемого турнира)
        tourn_rating = 0    # рейтинг рассмтриваемого турнира
        for SetID in UEFA_tourn_club_set_ID[club_set]:     # для каждого элемента списка ключа словаря (id клуба из club set рассматриваемого турнира)
            for StandID in TL_standings_rate:   # для каждого id клуба из TL standings
                if StandID == SetID:
                    tourn_rating += TL_standings_rate[StandID] + 1.2
                    break
        # определение рейтинга турнира с увеличением вложенности словаря до {Association:[Tournament,Rating]}
        Ass_TournRateQuot["UEFA"][i] = [club_set, tourn_rating / len(UEFA_tourn_club_set_ID[club_set])]
        # если задействован временной фактор: уменьшать рейтинг playoff set с 100% до 0% и увеличивать рейтинг group set с 0% до 100% каждый день на 1% с 01.09
        if time_factor != 0:
            if club_set.find("group") != -1:
                Ass_TournRateQuot["UEFA"][i][1] *= time_factor
            elif club_set.find("playoff") != -1:
                Ass_TournRateQuot["UEFA"][i][1] *= 1 - time_factor
        Ass_TournRateQuot["UEFA"][i][1] = round(Ass_TournRateQuot["UEFA"][i][1], 2)
        i += 1

    # UEFA tournament quota распределяется пропорционально рейтингам турниров
    UEFA_tourn_rate_sum = 0   # сумма рейтингов всех турниров УЕФА в Ass_TournRateQuot["UEFA"]
    for tourn in Ass_TournRateQuot["UEFA"]:
        UEFA_tourn_rate_sum += tourn[1]
    UEFA_tourn_rate_sum = round(UEFA_tourn_rate_sum, 2)
    # словарь рейтингов и квот каждого турнира {tourn:[rate,quota]}  (во время групповой стадии: сумма рейтингов playoff set и group set)
    whole_tourn_rate_quota = {"UCL": [0, 0], "UEL": [0, 0], "UECL": [0, 0]}     
    # определить рейтинг каждого турнира 
    for tourn in Ass_TournRateQuot["UEFA"]:
        for league in whole_tourn_rate_quota:
            if tourn[0].find(league) != -1:
                whole_tourn_rate_quota[league][0] += tourn[1]
    # определить квоту каждого турнира
    for league in whole_tourn_rate_quota:
        whole_tourn_rate_quota[league][1] = Association_rating["UEFA"][1] * whole_tourn_rate_quota[league][0] / UEFA_tourn_rate_sum
    # сумма квот турниров УЕФА, округленных до целого в меньшую сторону
    UEFA_tourn_quota_int_sum = 0   
    for league in whole_tourn_rate_quota:
        UEFA_tourn_quota_int_sum += math.floor(whole_tourn_rate_quota[league][1])
    # общая квота УЕФА, отброшенная в качестве дробных частей
    fractional_quota = Association_rating["UEFA"][1] - UEFA_tourn_quota_int_sum
    # распределение суммы дробных частей квот между турнирами в качестве целых квот в порядке уменьшения их дробной части
    if fractional_quota == 1:   # если сумма дробных частей квот равна 1
        fractional_part = 0   # дробная часть квоты турнира (инициализация)
        for league in whole_tourn_rate_quota:   # определение макс дробной части среди квот турниров
            if whole_tourn_rate_quota[league][1] % 1 > fractional_part:
                fractional_part = whole_tourn_rate_quota[league][1] % 1
                add_tourn = league
        whole_tourn_rate_quota[add_tourn][1] += 1   # присвоение целой квоты турниру с макс дробной частью
    if fractional_quota == 2:   # если сумма дробных частей квот равна 2
        fractional_part = 1   # дробная часть квоты турнира (инициализация)
        for league in whole_tourn_rate_quota:   # определение мин дробной части среди квот турниров
            if whole_tourn_rate_quota[league][1] % 1 < fractional_part:
                fractional_part = whole_tourn_rate_quota[league][1] % 1
                not_add_tourn = league
        for league in whole_tourn_rate_quota:   # присвоение целой квоты двум турнирам с макс дробной частью
            if league != not_add_tourn:
                whole_tourn_rate_quota[league][1] += 1
    # округление до целого квоты каждого турнира
    for league in whole_tourn_rate_quota:
        whole_tourn_rate_quota[league][1] = math.floor(whole_tourn_rate_quota[league][1])
    # во время групповой стадии квота распределяется между playoff set и group set пропорционально их рейтингам с округлением до целого в сторону playoff set
    for tourn in Ass_TournRateQuot["UEFA"]:
        for league in whole_tourn_rate_quota:
            if tourn[0].find(league) != -1:
                if tourn[0].find("group") != -1:
                    tourn.append(math.floor(round(whole_tourn_rate_quota[league][1] * tourn[1] / whole_tourn_rate_quota[league][0], 3)))
                if tourn[0].find("playoff") != -1:
                    tourn.append(math.ceil(round(whole_tourn_rate_quota[league][1] * tourn[1] / whole_tourn_rate_quota[league][0], 3)))
    
    # учет квоты TL на 10 лидеров
    Ass_TournRateQuot["TL"] = [["TopLiga", 1, 10]]


    Tourn_RateQuot = {}   # создание словаря квот турниров {Tournament:[Rating,Quota]}
    for ass_n in Ass_TournRateQuot:
        for tourn in Ass_TournRateQuot[ass_n]:
            if tourn[0].find("group") !=-1:
                tournament = tourn[0][:tourn[0].find("group")-1]
            elif tourn[0].find("playoff") !=-1:
                tournament = tourn[0][:tourn[0].find("playoff")-1]
            else:
                tournament = tourn[0]
            # if tourn[2] !=0:
            Tourn_RateQuot[tournament] = [str("{0:.2f}".format(tourn[1]))+" in "+ass_n, tourn[2]]
    
    # сортировка словаря квот турниров по убыванию квот
    Tourn_RateQuot = dict(sorted(Tourn_RateQuot.items(), key=lambda x: x[1][1], reverse=True))   

    # вывод на экран Tournament quota
    for tourn in Tourn_RateQuot:
        print("    {0:15}  {1:2}  {2:}".format(Tourn_RateQuot[tourn][0], Tourn_RateQuot[tourn][1], tourn))



    # # определение National ratings
    # Nations_list = []    # создание списка национальных ассоциаций, имеющих представителство в TL standings
    # Nations_list_rate = []  # и списка их рейтингов
    # for ID in TL_standings_data:
    #     Nations_list.append(TL_standings_data[ID][1])
    # Nations_list = list(set(Nations_list))  # избавляемся от повторных элементов преобразованием во множество и обратно
    # for country in Nations_list:
    #     Nation_rate = 0   # инициализация рейтинга конкретной ассоциации
    #     for ID in TL_standings_data:
    #         if country == TL_standings_data[ID][1]:
    #             Nation_rate += TL_standings_rate[ID] + 1.2
    #     Nations_list_rate.append(round(Nation_rate, 2))
    # # формирование общего словаря рейтингов ассоциаций
    # Association_rating = dict(zip(Nations_list, Nations_list_rate))   # объединение списков нац ассоциаций и их рейтингов в одном словаре
    # Association_rating["UEFA"] = UEFA_rating     # добавляем в словарь ассоциацию УЕФА
    # Association_rating = dict(sorted(Association_rating.items(), key=lambda x: x[1], reverse=True))   # сортировка словаря рейтинга ассоциаций по убыванию рейтинга

    # # Association quota = ˻ 50 * Assoiation rating / Σ (Assoiation ratings) ˼
    # Associations_rate_sum = 0   # сумма рейтингов ассоциаций
    # for ass_n in Association_rating:
    #     Associations_rate_sum += Association_rating[ass_n]
    # Associations_rate_sum = round(Associations_rate_sum, 2)
    # for ass_n in Association_rating:
    #     Association_quota = math.floor(50 * Association_rating[ass_n] / Associations_rate_sum)
    #     Association_rating[ass_n] = [Association_rating[ass_n], Association_quota]    # увеличение вложенности словаря ассоциаций: {ass:[rate,quota]}
    # # учет квоты TL на 10 лидеров
    # Association_rating["TopLiga"] = [0, 10]
    # Association_rating = dict(sorted(Association_rating.items(), key=lambda x: x[1][1], reverse=True))   # сортировка словаря рейтинга ассоциаций по убыванию рейтинга

    # # вывод на экран Association rating & quota
    # for ass_n in Association_rating:
    #     print("{0:8.2f}  {1:2}  {2:}".format(Association_rating[ass_n][0], Association_rating[ass_n][1], ass_n))



    

    # определение влияния UEFA club rankings на текущий TL standings
    # 1.07.23: 100% UEFA club rankings + 0% TL standings
    # каждый следующий день в 0:00 1/365 переходит в standings
    # определение количества полных дней между текущим временем и 01.07.23 по UTC
    Days_after_0107 = float((calc_date-datetime.datetime(2023, 7, 1))//datetime.timedelta(days=1))
    # коэффициент уменьшения влияния rate TL standings на итоговый rate клубов
    TL_Influence = (1/365)*Days_after_0107
    # коэффициент уменьшения влияния UEFA club rankings на итоговый rate клубов
    UEFA_Influence = 1-TL_Influence

    calc_date += datetime.timedelta(days=1) # перейти к следующей дате
    print() # добавить пустую строку для разделения дат
