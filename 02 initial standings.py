import datetime

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
import os   # импорт модуля работы с каталогами
import mod_UEFA_club_set    # модуль создания UEFA club set
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
while calc_date + datetime.timedelta(days=1) < DateNow:
    print(calc_date)

    # определение влияния UEFA club rankings на текущий TL standings
    # 1.07.23: 100% UEFA club rankings + 0% TL standings
    # каждый следующий день в 0:00 1/365 переходит в standings
    # определение количества полных дней между текущим временем и 01.07.23 по UTC
    Days_after_0107 = float((calc_date-datetime.datetime(2023, 7, 1))//datetime.timedelta(days=1))
    # коэффициент уменьшения влияния rate TL standings на итоговый rate клубов
    TL_Influence = (1/365)*Days_after_0107
    # коэффициент уменьшения влияния UEFA club rankings на итоговый rate клубов
    UEFA_Influence = 1-TL_Influence

    # Association rating = total club set SUM(pts+1.2) in TL standigs
    # определение UEFA rating
    UEFA_rating = 0
    for ID in TL_standings_rate:
        for SetID in UefaClubSetID:
            if ID == SetID:
                UEFA_rating += TL_standings_rate[ID] + 1.2
                break
    print("UEFA rating: "+str(round(UEFA_rating, 2)))
    # определение National ratings
    Nations_list = []    # создание списка национальных ассоциаций, имеющих представителство в TL standings
    for ID in TL_standings_data:
        Nations_list.append(TL_standings_data[ID][1])
    Nations_list = list(set(Nations_list))  # избавляемся от повторных элементов преобразованием во множество и обратно
    

    calc_date += datetime.timedelta(days=1) # перейти к следующей дате
    print() # добавить пустую строку для разделения дат
