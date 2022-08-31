import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "e4531fe674bb4eaab280d63fed977b07"
    }

conn.request("GET", "/status", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
# на этом месте заканчивается стандартный запрос
print()
answer = str(data.decode("utf-8"))  # преобразование полученных данных в строку

answer = answer[1:]
# после символа { или [ или , установить по '   ' в количестве = (разница между количеством { и }) + (разница между количеством [ и ]) перед этим символом
symbol = 0
lenght = len(answer)
while symbol < lenght:
    if answer[symbol] == '{' or answer[symbol] == '[':
        fig_open = answer.count('{',0,symbol)
        fig_clos = answer.count('}',0,symbol)
        sqr_open = answer.count('[',0,symbol)
        sqr_clos = answer.count(']',0,symbol)
        if fig_open+1 != fig_clos or sqr_open != sqr_clos:
            answer = answer[0:symbol+1] + ('   ' * ((fig_open+1 - fig_clos) + (sqr_open - sqr_clos))) + answer[symbol+1:]
            symbol += (3 * ((fig_open+1 - fig_clos) + (sqr_open - sqr_clos)))
            lenght += (3 * ((fig_open+1 - fig_clos) + (sqr_open - sqr_clos)))
    if answer[symbol] == ',':
        fig_open = answer.count('{',0,symbol)
        fig_clos = answer.count('}',0,symbol)
        sqr_open = answer.count('[',0,symbol)
        sqr_clos = answer.count(']',0,symbol)
        if fig_open != fig_clos or sqr_open != sqr_clos:
            answer = answer[0:symbol+1] + ('   ' * ((fig_open - fig_clos) + (sqr_open - sqr_clos))) + answer[symbol+1:]
            symbol += (3 * ((fig_open - fig_clos) + (sqr_open - sqr_clos)))
            lenght += (3 * ((fig_open - fig_clos) + (sqr_open - sqr_clos)))
    symbol += 1
answer = answer.replace('},','\n')
answer = answer.replace('],','\n')
answer = answer.replace(',','\n')
answer = answer.replace('"','')
answer = answer.replace(':{',':\n')
answer = answer.replace(':[',':\n')
answer = answer.replace(':',': ')
answer = answer.replace('}','')
print(answer)
print()

# запись answer в файл (для экономии запросов)
import time
d = time.localtime()
date_fname = str(d.tm_year) + '-' + str(d.tm_mon)  + '-' + str(d.tm_mday)  + '_' + str(d.tm_hour)  + '-' + str(d.tm_min)  + '-' + str(d.tm_sec)
fname = 'answer ' + date_fname
f = open("C:\\Users\\Серж\\Desktop\\TopLiga\\!new realities\\TL_work\\API interaction\\answers\\"+fname+".txt", 'w')
f.write(answer)
f.write('\n\n\n')
f.write(data.decode("utf-8"))
f.close()
