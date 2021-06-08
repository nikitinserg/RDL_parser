import requests
import docx
import re
import json
from datetime import date
from login_password import logpass

url = 'https://sumrv.rdl-telecom.com/'
link = 'https://sumrv.rdl-telecom.com/api/sumrv-1/carriages/auth'
url_invent = 'https://sumrv.rdl-telecom.com/api/sumrv-1/carriages/kit/invent'
url_daily_statement = 'https://sumrv.rdl-telecom.com/api/sumrv-1/carriages/daily_statement'
trains = {'375': '375Э(ТЫНДА)',
          '364': '364Э',
          '81': '081Э',
          '97': '097Э',
          }

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

location = 'ЛВЧ-2+Тында' # депо привязки
filename = 'Наряд.docx'

s = requests.session()
response = s.post(url=link, data=logpass, headers=headers).text


def parsing_docx(filename):
    """
    получение наряда от диспетчера и распарсивание оного
    :param filename: *.docx
    :return: None
    """
    doc = docx.Document(filename)
    all_prg = doc.paragraphs
    for para in all_prg:
        carriage_number = find_number(para.text)
        if carriage_number:
            carriage_number = str(carriage_number[0])
            para.text = para.text.replace(carriage_number, find_prefix(carriage_number))
        print(para.text)


def parsing_rdl():
    pass


def parsing_daily_statement(location: str, date: str):
    pass


def parsing_carriage(carriage_number):
    pass


def generate_file_name(day=''):
    """
    генерация имени файла
    :param today: если day пустой - будет сегодняшняя дата. Формат - ГГГГ-ММ-ДД
    :return: str - имя файла формата 'Наряд.ГГГГ.ММ.ДД.docx'
    """
    if not day:
        year, month, day = str(date.today()).split('-')
    else:
        year, month, day = day.split('-')
    name = f'Наряд.{year}.{month}.{day}.docx'
    return name


def find_number(paragraph: str):
    """
    поиск номера вагона в параграфе
    :param paragraph: string
    :return: 5 digit number
    """
    carriage_number = re.findall(r"[0-9]{5}", paragraph)
    return carriage_number


def find_prefix(carriage_number, get_date=''):
    """
    Поиск трехзначного префикса номера вагона
    :param carriage_number: номер вагона
    :param get_date:
    :return: str вида 123-45678
    """
    if not get_date:
        get_date = str(date.today())
    req = f'{url_invent}/1?search=&date={get_date}&branch=&depot={location}&carriage={carriage_number}&invent_status=&trains_status=&routes_processes_group='
    r = s.get(req).json()
    cur_elem = list(r['elem_list'].keys())
    if cur_elem:
        full_carriage_number = r['elem_list'][cur_elem[0]]['carriage_number']
        return full_carriage_number
    else:
        return f'___-{carriage_number}' # если вагон не принадлежит депо привязки location


def find_scheme(get_date=''):
    """
    поиск id состава по номеру состава
    :param get_date:
    :return: list (номер состава, id состава)
    """
    if not get_date:
        get_date = str(date.today())
    req = f'{url_daily_statement}?search=&date={get_date}&branch=&depot={location}&carriage=&invent_status=&trains_status=&routes_processes_group='
    r = s.get(req).json()
    routes = r['routes']
    for route in routes:
        yield ([route['route'], route['register_id']])

for i in find_scheme('2021-06-08'):
    print(i)
# parsing_docx(filename=filename)
