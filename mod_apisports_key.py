def api_key(api_request):
    import http.client

    conn = http.client.HTTPSConnection("v3.football.api-sports.io")

    headers = {
        'x-apisports-key': "e4531fe674bb4eaab280d63fed977b07"
        }

    conn.request("GET", api_request, headers=headers)

    res = conn.getresponse()
    data = res.read()

    api_answer = data.decode("utf-8")

    return(api_answer)