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

Association_rating = {}     # словарь {Association:Rating}

# цикл на каждую дату с 01.07.23 по сегодня
calc_date = datetime.datetime(2023, 7, 1)
while calc_date + datetime.timedelta(days=1) < DateNow: # datetime.datetime(2023, 12, 20):
    print(calc_date)    # вывод на экран расчетной даты

    

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
    Associations_dict = dict(zip(Nations_list, Nations_list_rate))   # объединение списков нац ассоциаций и их рейтингов в одном словаре
    Associations_dict["UEFA"] = UEFA_rating     # добавляем в словарь ассоциацию УЕФА
    Associations_dict = dict(sorted(Associations_dict.items(), key=lambda x: x[1], reverse=True))   # сортировка словаря рейтинга ассоциаций по убыванию рейтинга

    # Association quota = ˻ 50 * Assoiation rating / Σ (Assoiation ratings) ˼
    Associations_rate_sum = 0   # сумма рейтингов ассоциаций
    for ass_n in Associations_dict:
        Associations_rate_sum += Associations_dict[ass_n]
    Associations_rate_sum = round(Associations_rate_sum, 2)
    for ass_n in Associations_dict:
        Association_quota = math.floor(50 * Associations_dict[ass_n] / Associations_rate_sum)
        Associations_dict[ass_n] = [Associations_dict[ass_n], Association_quota]    # увеличение вложенности словаря ассоциаций: {ass:[rate,quota]}
    # учет квоты TL на 10 лидеров
    Associations_dict["TopLiga"] = [0, 10]
    Associations_dict = dict(sorted(Associations_dict.items(), key=lambda x: x[1][1], reverse=True))   # сортировка словаря рейтинга ассоциаций по убыванию рейтинга

    # вывод на экран Association rating & quota
    for ass_n in Associations_dict:
        print("{0:8.2f}  {1:2}  {2:}".format(Associations_dict[ass_n][0], Associations_dict[ass_n][1], ass_n))
    


    # Tournament rating & quota

    # UEFA tournaments rating & quota
    # определение UEFA tournaments club set
    # жеребьевка группового этапа еврокубков проходит в конце августа
    # для получения group set следует с 01.09 ежедневно делать запрос на игры в октябре, пока в папке club set/ не будет сформирован соответсвующий файл
    # жеребьевка 1 стадии плей-офф еврокубков проходит на следующей неделе после 6-го тура групп в середине декабря. 1/8 проходит в феврале/марте
    # для получения playoff set следует с 16.12 ежедневно делать запрос на игры в феврале и марте, пока в папке club set/ не будет сформирован соответсвующий файл
    # 01.09-15.12: требуются group set и playoff set прошлого сезона; 15.12-01.09: требуется последний playoff set
    # определение имени и наличия необходимого файла, необходимости api-запроса
    UEFA_tourn_club_set = []   # список tournament club set
    UEFA_tourn_club_set_ID = {}    # словарь ID клубов из club sets
    UEFA_leagues = ("UCL", "UEL", "UECL")
    for league in UEFA_leagues:
        # определение имен файлов tournament club set
        if (calc_date.month > 8 and calc_date.month < 12) or (calc_date.month == 12 and calc_date.day < 16):
            UEFA_tourn_club_set.append([league, str(calc_date.year-1)+"-"+str(calc_date.year), "playoff set"])
            UEFA_tourn_club_set.append([league, str(calc_date.year)+"-"+str(calc_date.year+1), "group set"])
        elif calc_date.month < 9:
            UEFA_tourn_club_set.append([league, str(calc_date.year-1)+"-"+str(calc_date.year), "playoff set"])
        elif calc_date.month == 12 and calc_date.day > 15:
            UEFA_tourn_club_set.append([league, str(calc_date.year)+"-"+str(calc_date.year+1), "playoff set"])
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
        # заполнение словаря ID клубов из club sets
        LegueClubSetID = []    # создание списка id из файла UefaClubSet
        with open("club_set\\"+UEFA_tourn_club_set[i][0]+" "+UEFA_tourn_club_set[i][1]+" "+UEFA_tourn_club_set[i][2]+".txt", 'r') as f:
            for line in f:  # цикл по строкам
                kursor = line.find('id:',0) +3    # переместить курсор перед искомой подстрокой
                end_substr = line.find('.',kursor)    # определение конца искомой подстроки (поиск символа "." после позиции курсора)
                LegueClubSetID.append(int(line[kursor:end_substr]))
        UEFA_tourn_club_set_ID[str(UEFA_tourn_club_set[i][0]+" "+UEFA_tourn_club_set[i][1]+" "+UEFA_tourn_club_set[i][2])] = LegueClubSetID
        i += 1


    

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
