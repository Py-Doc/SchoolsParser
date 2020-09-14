#!/usr/bin/python
import grequests
import requests
import json
from tqdm import *
import csv

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0',
           'Accept': 'application/json, text/javascript, */*; q=0.01'}
base = [['Наименование', 'Директор', 'Адрес', 'Тип населённого пункта',
         'Регион', 'Телефон', 'Сайт', 'E-mail', 'Источник']]
with open('regions.json', 'r', encoding='utf-8') as fh:
    DATA = json.load(fh)


def writing_raw(pages, region):
    pages_list = [f'https://bus.gov.ru/public/agency/agency.json?agency={page}' for page in pages]
    jsons = (grequests.get(page_url) for page_url in pages_list)
    for i in list(filter(lambda x: x.status_code == 200, grequests.map(jsons))):
        i = i.json()
        try:
            name = i['agency']['shortClientName'].strip()
        except:
            name = i['agency']['shortClientAltName'].strip()
        address = i['agency']['agencyAddress']['fullAddress'].strip()
        try:
            loc_type = f"{i['publicInfo']['ppo']['settlementType']}"
        except:
            loc_type = None
        try:
            phone = i['agency']['phone'].strip()
        except:
            phone = i['agency']['branch']['headAgency']['phone'].strip()
        try:
            site = i['agency']['website'].strip()
        except:
            site = None
        try:
            link = f"https://bus.gov.ru/pub/info-card/{i['agency']['id']}".strip()
        except:
            link = f"https://bus.gov.ru/pub/info-card/{i['agency']['branch']['headAgency']['id']}".strip()
        try:
            director = f"{i['agency']['managerSecondName']} " \
                       f"{i['agency']['managerFirstName']} " \
                       f"{i['agency']['managerMiddleName']}"
        except:
            director = f"{i['agency']['branch']['headAgency']['managerSecondName']} " \
                       f"{i['agency']['branch']['headAgency']['managerFirstName']} " \
                       f"{i['agency']['branch']['headAgency']['managerMiddleName']}"
        try:
            email = f"{i['agency']['email']}"
        except:
            email = f"{i['agency']['branch']['headAgency']['email']}"
        base.append([name, director, address, loc_type, region, phone, site, email, link])


def get_info(region, data=DATA):
    print(f'Working at {region}...')
    region_pages = [f'https://bus.gov.ru/public-rest/api/agency/search/init?d-442831-p={j}&'
                    f'orderAttributeName=rank&orderDirectionASC=false&pageSize=30&regionId={data[region][0]}&'
                    f'regions={data[region][0]}&searchString=%D1%88%D0%BA%D0%BE%D0%BB%D0%B0&searchTermCondition=or'
                    for j in range(1, int(data[region][1]) // 30 + 2)]

    outer_jsons = (grequests.get(page_url) for page_url in region_pages)
    outer_lst = grequests.map(outer_jsons)
    id_list = []
    for i in [y['agencies'] for y in [x.json() for x in outer_lst]]:
        for j in i:
            id_list.append(j["agencyId"])
    writing_raw(id_list, region)
    print(f'Region {region} id done...')


print('Staring parse...')
with tqdm(total=len(DATA)) as pbar:
    for reg, region_list in DATA.items():
        map(get_info(reg), DATA)
        pbar.update()
        print()

with open('base.csv', 'w') as f:
    w = csv.writer(f)
    w.writerows(base)
    f.close()

print('Done!')
