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

# создание словаря/списка TL standings на 01.07.23
# в нем хранятся: name, nat, rate и, возможно, еще доп данные


# здесь начинается циклическая часть с перерасчетами на каждую дату
# если во входящих в дату standings появилось более одного клуба из одной асоциации, fixtures турниров которой не были запрошены ранее, - создать такие запросы
# результаты игр брать из базы созданных ранее запросов fixtures

# цикл на каждую дату с 01.07.23 по сегодня
calc_date = datetime.datetime(2023, 7, 1)
while calc_date + datetime.timedelta(days=1) < DateNow:

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
    

    # UEFA rating


    calc_date += datetime.timedelta(days=1)
