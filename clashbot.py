from urllib.request import Request, urlopen
import json,sys,subprocess
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

clan = Request('https://api.royaleapi.com/clan/PLPQQ0U8')
past = Request('https://api.royaleapi.com/clan/PLPQQ0U8/warlog')
past.add_header('auth', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MjA5NywiaWRlbiI6IjEwODMyNjAxOTM5OTcwODY3MiIsIm1kIjp7fSwidHMiOjE1NDM5NDE0NjU5OTR9.IpB1GqSRbxvfqVbZfgfYKTQV9LIyDxeZtUXMnyjdM0I')
clan.add_header('auth', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MjA5NywiaWRlbiI6IjEwODMyNjAxOTM5OTcwODY3MiIsIm1kIjp7fSwidHMiOjE1NDM5NDE0NjU5OTR9.IpB1GqSRbxvfqVbZfgfYKTQV9LIyDxeZtUXMnyjdM0I')

past_data = urlopen(past).read()
clan_data = urlopen(clan).read()
membros = json.loads(clan_data.decode("utf-8"))
guerras = json.loads(past_data.decode("utf-8"))

jogadores = []
for i in membros["members"]:
    jogadores.append(i["name"])

data = {}
playersData = {}

for i in jogadores:
    playersData[i] = {}

for i in guerras:
    ts = i["createdDate"]
    diaGuerra = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
    data[diaGuerra] = {}
    for j in jogadores:
        data[diaGuerra][j] = {}
    #print(data)
    for k in i["participants"]:
        if k["name"] in jogadores:
            data[diaGuerra][k["name"]]["batalhasJogadas"] = k["battlesPlayed"]
            data[diaGuerra][k["name"]]["vitorias"] = k["wins"]
            data[diaGuerra][k["name"]]["Batalhas da Coleta Jogadas"] = k["collectionDayBattlesPlayed"]

sheet = client.open('clashBot')
ws=client.open('clashBot').sheet1
row = [[ "Nome do Jogador", "Batalhas Jogadas", "Vitorias", "Batalhas de Coleta","TOTAL DE VITORIAS"]]

datas = []
added = []
for i in data:
    datas.append(i)
    for y in data[i]:
        k = []
        k.append(i)
        k.append(y)
        for u in data[i][y]:
            k.append(data[i][y][u])
        if k not in added:
            added.append(k)
datas = sorted(datas)
ultima = datas[-1]
ultimaGuerraStats = []
for k in added:
    if k[0] == ultima:
        ultimaGuerraStats.append(k[1:])

for m in ultimaGuerraStats:
    if len(m) > 1:
        m.append(m[2])
    else:
        for n in range(4):
            m.append(0)

#recolher vitorias de guerra para atualizar
nomes_ = sheet.values_get('Sheet1!A2:A')
if "values" in nomes_:

    nomes_ = nomes_["values"]

    winsG =  sheet.values_get('Sheet1!E2:E')
    winsG = winsG['values']

    vitoriasPerPlayer = {}
    i = 0
    for player_ in nomes_:
        vitoriasPerPlayer[player_[0]] = winsG[i][0]
        i+=1

    for stat in ultimaGuerraStats:
        if len(stat) > 1 and len(stat)<6:
            stat[4] += int(vitoriasPerPlayer[stat[0]])

sheet.values_clear('Sheet1!A:A')
sheet.values_clear('Sheet1!B:B')
sheet.values_clear('Sheet1!C:C')
sheet.values_clear('Sheet1!D:D')

sheet.values_update('Sheet1!A1', params={'valueInputOption': 'RAW'}, body = {'values': row})
sheet.values_update(
    'Sheet1!A2',
     params={'valueInputOption': 'RAW'},
     body = {'values': ultimaGuerraStats}
)
