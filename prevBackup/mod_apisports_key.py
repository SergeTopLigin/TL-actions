def api_key(api_request):
    import traceback
    import datetime     # модуль для определния текущей даты
    DateNow = str(datetime.datetime.utcnow())[:19].replace(":", "-")    # текущая дата по UTC, отформатированная под строку для имени файла
    try:

        import http.client

        conn = http.client.HTTPSConnection("v3.football.api-sports.io")

        headers = {
            'x-apisports-key': ""
            }

        conn.request("GET", api_request, headers=headers)

        res = conn.getresponse()
        data = res.read()

        api_answer = data.decode("utf-8")

        return(api_answer)

    except:
        with open("bug_files\\"+DateNow+".txt", 'w') as f:
            traceback.print_exc(file=f)
            f.write(str(api_request))
