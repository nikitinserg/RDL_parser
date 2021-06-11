from login_password import logpass
import requests


url_invent = 'https://sumrv.rdl-telecom.com/api/sumrv-1/carriages/kit/invent'
link = 'https://sumrv.rdl-telecom.com/api/sumrv-1/carriages/auth'

headers = {
    'Host': 'sumrv.rdl-telecom.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json;charset=utf-8',
    'Content-Length': '42',
    'Origin': 'https://sumrv.rdl-telecom.com',
    'Connection': 'keep-alive',
    'Referer': 'https://sumrv.rdl-telecom.com/',
    'Cookie': 'role=view',
}

s = requests.session()
response = s.post(url=link, data=logpass, headers=headers).text
carriage_number = '097-11102'


def parsing_carriage(carriage_number):
    req = f'{url_invent}/{carriage_number}/result/list'
    r = s.get(req).json()
    inventarisation = (r['processes'][0]['blocks'])
    conclusion = inventarisation['conclusion']['text']
    im = inventarisation['im']['text']
    skbspp = inventarisation['skbspp']['text']
    skdu = inventarisation['skdu']['text']
    svnr = inventarisation['svnr']['text']
    carriage_inventarisation = ''
    if conclusion != 'Не оборудован':
        if im != 'Не оборудован':
            carriage_inventarisation += 'ИМ, '
        if skbspp != 'Не оборудован':
            carriage_inventarisation += 'СКБСПП, '
        if skdu != 'Не оборудован':
            carriage_inventarisation += 'СКДУ, '
        if svnr != 'Не оборудован':
            carriage_inventarisation += 'СВНР, '
    else:
        carriage_inventarisation = 'Не оборудован'
    print(carriage_inventarisation)

parsing_carriage(carriage_number)