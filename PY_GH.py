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

# import os   # импорт модуля работы с каталогами
# for Set_file in os.listdir('club_set/'):
#     text = Set_file

import mod_apisports_key    # модуль с ключом аккаунта api
api_answer = mod_apisports_key.api_key("/fixtures?league=2&season=2023&from=2023-10-01&to=2023-10-31")
text = api_answer

repo = g.get_repo("SergeTopLigin/TL-actions")
repo.create_file("test1.txt", "test", text, branch="main")
