from dataclasses import dataclass, asdict
from datetime import datetime

import pandas as pd
from tqdm import tqdm
from websbor import WebSborClient


def parse_subfields(field):
    code = field.get('code')
    name = field.get('name')
    return f'{code}-{name}'


@dataclass(init=False)
class Organization:
    address_fact: str
    date_reg: str
    id: str
    name: str
    ogrn: str
    okato_fact: str
    okato_reg: str
    okfs: str
    okogu: str
    okopf: str
    oktmo_fact: str
    oktmo_reg: str
    okved2_fact: str
    okpo: str
    short_name: str

    def __init__(self, **kwargs):
        complex_fileds = (
            'okato_fact',
            'okato_reg',
            'okfs',
            'okogu',
            'okopf',
            'oktmo_fact',
            'oktmo_reg',
            'okved2_fact'
        )
        for key, value in kwargs.items():
            if key in complex_fileds:
                value = parse_subfields(value)
                setattr(self, key, value)
            else:
                setattr(self, key, value)


@dataclass(init=False)
class Report:
    comment: str 
    end_time: str 
    form_period: str 
    index: str 
    name: str
    okud: str 
    reported_period: str
    org_id: str

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

organisation_object_model = {
    "address_fact": "Фактический адресс",
    "date_reg": "Дата регистрации",
    "id": "ID организации",
    "inn": "ИНН",
    "name": "Полное название",
    "ogrn": "ОГРН",
    "okato_fact": "ОКАТО-факт",
    "okato_reg": "ОКАТО-рег",
    "okfs": "ОКФС",
    "okogu": "ОКОГУ",
    "okopf": "ОКОП",
    "okpo": "ОКПО",
    "oktmo_fact": "ОКТМО-факт",
    "oktmo_reg": "ОКТМО-рег",
    "okved2_fact": "ОКВЕД2-факт",
    "short_name": "Краткое название"
}


report_object_model = {
    "comment": "Комментарий",
    "end_time": "Срок сдачи формы",
    "form_period": "Периодичность формы",
    "index": "Индекс формы",
    "name": "Наименование формы",
    "okud": "ОКУД",
    "reported_period": "Отчетный период",
    "org_id": "ID организации"
}


def get_organisations_data(inns, buffer=None):
    total_orgs = []
    total_reports = []
    websbor_client = WebSborClient(delay=4, progress_bar=tqdm)

    print('Начат сбор данных организаций')
    orgs_data = websbor_client.get_organisations_by_inns_list(inns)
    print('Сбор закончен')

    for org in orgs_data:
        org_reports = org.pop('reports', ()) 
        org = Organization(**org)
        reports = [
            asdict(Report(**report, org_id=org.id))
            for report in org_reports
        ]
        total_reports.extend(reports)
        total_orgs.append(asdict(org))

    return save_to_xlsx(total_orgs, total_reports, buffer=buffer)


def save_to_xlsx(orgs, reports, buffer=None):
    date_time = datetime.now().strftime('%Y_%m_%d_%H_%M')
    filename = buffer if buffer else f'данные_организаций_{date_time}.xlsx'
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    workbook = writer.book
    orgs_sheet = workbook.add_worksheet('Организации')
    reports_sheet = workbook.add_worksheet('Отчеты')
    writer.sheets['Организации'] = orgs_sheet
    writer.sheets['Отчеты'] = reports_sheet

    df_orgs = pd.DataFrame(orgs)
    df_orgs.rename(columns=organisation_object_model, inplace=True)
    print(df_orgs.dtypes)
    print(df_orgs)
    df_orgs.to_excel(writer, sheet_name='Организации', startcol=0, startrow=0)
    
    df_reports = pd.DataFrame(reports)
    df_reports.rename(columns=report_object_model, inplace=True)
    df_reports.to_excel(writer, sheet_name='Отчеты', startcol=0, startrow=0)
    return writer


if __name__ == '__main__':
    with open('inns.txt') as f:
        inns = [int(line) for line in f.readlines()]
        get_organisations_data(inns).close()