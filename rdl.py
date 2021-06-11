import re
from datetime import date
import docx
import requests

from login_password import logpass

url = 'https://sumrv.rdl-telecom.com/'
link = 'https://sumrv.rdl-telecom.com/api/sumrv-1/carriages/auth'
url_invent = 'https://sumrv.rdl-telecom.com/api/sumrv-1/carriages/kit/invent'
url_daily_statement = 'https://sumrv.rdl-telecom.com/api/sumrv-1/carriages/daily_statement'
trains = {'375': '375Э(ТЫНДА)',
          '364': '364Э',
          '81': '081Э',
          '97': '097Э',
          '235': '235Э'
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
        type_of_paragraph = parsing_paragraph(para.text)
        if type_of_paragraph == 'carriage':
            carriage_number = find_number(para.text)
            carriage_number = str(carriage_number[0])
            para.text = para.text.replace(carriage_number, find_prefix(carriage_number))
        elif type_of_paragraph == 'scheme':
            scheme = find_scheme(para.text)
            if scheme != '000':
                print('id не найдено')
            else:
                para.text = para.text.replace(scheme, find_scheme_id(scheme))
        print(para.text)


def parsing_paragraph(paragraph: str):
    if re.findall(r"[0-9]{5}", paragraph):
        return 'carriage'
    elif re.search("Сх ", paragraph):
        return 'scheme'
    else:
        return 'other'


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


def find_scheme(paragraph: str):
    """
    поиск номера состава
    :param paragraph: string
    :return: 2-3 digit string
    """
    scheme_number = ''
    if re.search("Сх ", paragraph):
        scheme_number = paragraph.split()[1]
        correct_scheme_name = trains[scheme_number]  # правильная запись номера состава
        if correct_scheme_name:
            return find_scheme_id(correct_scheme_name)
    return '000' # не найдено


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


def find_scheme_id(correct_scheme_name: str, get_date=''):
    """
    поиск id состава по номеру состава
    :param correct_scheme_name:  номер состава в правильной нотации
    :param get_date:
    :return: list (номер состава, id состава)
    """
    if not get_date:
        get_date = str(date.today())
    req = f'{url_daily_statement}?search=&date={get_date}&branch=&depot={location}&carriage=&invent_status=&trains_status=&routes_processes_group='
    r = s.get(req).json()
    routes = r['routes']
    for route in routes:
        if route['route'] == correct_scheme_name:
            return route['register_id']
    else:
        return '_________'  # если состав не найден



parsing_docx(filename=filename)
