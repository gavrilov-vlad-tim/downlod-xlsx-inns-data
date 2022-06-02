from datetime import datetime
from pprint import pprint

import pandas as pd
from tqdm import tqdm
from websbor import WebSborClient

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

org_model = ("address_fact", "date_reg", "id", "inn", "name",
             "ogrn", 
             ("okato_fact", ("code", "name")), 
             ("okato_reg", ("code", "name")),
             ("okfs", ("code", "name")),
             ("okogu", ("code", "name")),
             ("okopf", ("code", "name")),
             "okpo",
             ("oktmo_fact", ("code", "name")),
             ("oktmo_reg", ("code", "name")),
             ("okved2_fact", ("code", "name")),
             "short_name")

report_model = ("comment", "end_time", "form_period", "index", "name",
                "okud", "reported_period")

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


def parse_object(obj, object_model):
    new_obj = {}
    for field in object_model:
        if isinstance(field, tuple):
            field, sub_fields = field
            sub_obj = obj.get(field, {})
            code, name = [sub_obj.get(sub_field, '') 
                          for sub_field in sub_fields]
            new_obj[field] = f'{code}-{name}'
        else:
            new_obj[field] = obj.get(field)
    return new_obj              
                

def get_organisations_data(inns, save_path=None):
    total_orgs = []
    total_reports = []
    websbor_client = WebSborClient(delay=4, progress_bar=tqdm)
    print('Начат сбор данных организаций')
    orgs_data = websbor_client.get_organisations_by_inns_list(inns)
    print('Сбор закончен')
    for org in orgs_data:
        org_id = org.get('id')
        reports = [dict(**parse_object(report, report_model), org_id=org_id)
                   for report in org.pop('reports', ())]
        total_reports.extend(reports)
        total_orgs.append(parse_object(org, org_model))  
    return save_to_xlsx(total_orgs, total_reports, save_path=save_path)


def save_to_xlsx(orgs, reports, save_path=None):
    date_time = datetime.now().strftime('%Y_%m_%d_%H_%M')
    filename = save_path if save_path else f'данные_организаций_{date_time}.xlsx'
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    workbook = writer.book
    orgs_sheet = workbook.add_worksheet('Организации')
    reports_sheet = workbook.add_worksheet('Отчеты')
    writer.sheets['Организации'] = orgs_sheet
    writer.sheets['Отчеты'] = reports_sheet

    df_orgs = pd.DataFrame(orgs)
    df_orgs = df_orgs.astype({'id': int, 'inn': int, 'ogrn': int, 'okpo': int})
    df_orgs.rename(columns=organisation_object_model, inplace=True)
    df_orgs.to_excel(writer, sheet_name='Организации', startcol=0, startrow=0)
    
    df_reports = pd.DataFrame(reports)
    df_reports = df_reports.astype({'okud': int, 'org_id': int})
    df_reports.rename(columns=report_object_model, inplace=True)
    df_reports.to_excel(writer, sheet_name='Отчеты', startcol=0, startrow=0)
    return writer


if __name__ == '__main__':
    with open('inns.txt') as f:
        inns = [int(line) for line in f.readlines()]
        get_organisations_data(inns).close()