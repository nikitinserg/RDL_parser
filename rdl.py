import re
from datetime import date
import docx
import requests

from login_password import logpass

url = 'https://sumrv.rdl-telecom.com/'
link = 'https://sumrv.rdl-telecom.com/api/sumrv-1/carriages/auth'
url_invent = 'https://sumrv.rdl-telecom.com/api/sumrv-1/carriages/kit/invent'
url_toprof = 'https://sumrv.rdl-telecom.com/api/sumrv-1/carriages/kit/toprof'
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
            full_number = find_prefix(carriage_number)
            inventarisation = parsing_carriage(full_number)
            toprof = parsing_toprof(full_number)
            if is_inventarised(full_number):
                full_number_plus_invent = f'{toprof} {full_number}:{inventarisation}'
            else:
                full_number_plus_invent = f'!!! {full_number}: не инвентаризован!!!'
            para.text = para.text.replace(carriage_number, full_number_plus_invent)
        elif type_of_paragraph == 'scheme':
            scheme = find_scheme(para.text)[0]
            correct_scheme = find_scheme(para.text)[1]
            if correct_scheme == '000':
                print('id не найдено')
            else:
                scheme_id = find_scheme_id(correct_scheme)
                para.text = para.text.replace(scheme, f'{scheme} __{scheme_id}__')
        print(para.text)
    doc.save(generate_file_name())


def parsing_paragraph(paragraph: str):
    if re.findall(r"[0-9]{5}", paragraph):
        return 'carriage'
    elif re.search("Сх ", paragraph):
        return 'scheme'
    else:
        return 'other'


def is_inventarised(carriage_number: str):
    """
    Проверка, был ли инвентаризован вагон
    :param carriage_number:
    :return:  True - был инвентаризован, False - не был
    """
    req = f'{url_invent}/{carriage_number}/result/list'
    r = s.get(req).json()
    invent_status = (r['processes'][0]['status'])
    if invent_status == 'not_produced':
        return False
    else:
        return True


def parsing_toprof(carriage_number: str):
    """
    Проверка, был ли сделан ТОпроф
    :param carriage_number:
    :return: str
    """
    if carriage_number[0] == '_':  # депо привязки не выяснено
        return '?'
    else:  # депо привязки == location
        req = f'{url_toprof}/{carriage_number}/result/list'
        r = s.get(req).json()
        if r['processes']:
            toprof = (r['processes'][0]['status'])
            if toprof == 'in_progress':
                return '*'  # надо провести ТОпроф
            elif toprof == 'waiting_for_the_act':
                return '+'  # ТОпроф пройден
            else:
                return '-'  # не надо проводить ТОпроф
        else:
            return '-'


def parsing_carriage(carriage_number: str):
    """
    ищет какое оборудование есть на вагоне
    :param carriage_number:
    :return: str
    """
    carriage_inventarisation = ''
    if carriage_number[0] == '_':  # депо привязки не выяснено
        carriage_inventarisation = '_?________?_'
    else:  # депо привязки == location
        req = f'{url_invent}/{carriage_number}/result/list'
        r = s.get(req).json()
        inventarisation = (r['processes'][0]['blocks'])
        conclusion = inventarisation['conclusion']['text'].lower()
        im = inventarisation['im']['text'].lower()
        skbspp = inventarisation['skbspp']['text'].lower()
        skdu = inventarisation['skdu']['text'].lower()
        svnr = inventarisation['svnr']['text'].lower()
        if re.findall(r'не оборудован|not_equipped_to_it', conclusion):
            carriage_inventarisation = 'Не оборудован'
        else:
            if im != 'не оборудован':
                carriage_inventarisation += 'им,'
            if skbspp != 'не оборудован':
                carriage_inventarisation += 'скб,'
            if skdu != 'не оборудован':
                carriage_inventarisation += 'скду,'
            if svnr != 'не оборудован':
                carriage_inventarisation += 'свнр,'
    return carriage_inventarisation


def generate_file_name(day=''):
    """
    генерация имени файла
    :param day: если day пустой - будет сегодняшняя дата. Формат - ГГГГ-ММ-ДД
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
            return scheme_number, correct_scheme_name
        else:
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
    :return: str (id состава)
    """
    if not get_date:
        get_date = str(date.today())
    req = f'{url_daily_statement}?search=&date={get_date}&branch=&depot={location}&carriage=&invent_status=&trains_status=&routes_processes_group='
    r = s.get(req).json()
    routes = r['routes']
    for route in routes:
        if route['route'] == correct_scheme_name:
            register_id = route['register_id']
            return str(register_id)
    else:
        return 'id_не_найден'  # если состав не найден


parsing_docx(filename=filename)
