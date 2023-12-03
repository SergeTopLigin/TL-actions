from github import Github

# Authentication is defined via github.Auth
from github import Auth

CodingToken = "2g2h2p2_2U2e2q2m212I2C2H232L2Z2J2C2h2f2p2q2s2S2z2S272Z2P2y2J2e2n2J2t202X2i2R2I2N"
UncodingToken = ""
for i in range(len(CodingToken)):
    if i%2 != 0:
        UncodingToken += CodingToken[i]

# using an access token
auth = Auth.Token(UncodingToken)

# Public Web Github
g = Github(auth=auth)


import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "e4531fe674bb4eaab280d63fed977b07"
    }

conn.request("GET", "/status", headers=headers)

res = conn.getresponse()
data = res.read()


repo = g.get_repo("SergeTopLigin/TL-actions")
repo.create_file("test.txt", "test", data.decode("utf-8"), branch="main")
