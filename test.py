from datetime import datetime

import pandas as pd


data = [{'A': f'000{str(i)}000'} for i in range(5)]
df = pd.DataFrame(data)
date_time = datetime.now().strftime('%Y_%m_%d_%H_%M')
filename = f'данные_организаций_{date_time}.xlsx'
writer = pd.ExcelWriter(filename, engine='xlsxwriter')
book = writer.book
sh = book.add_worksheet('A')
writer.sheets['A'] = sh
df.to_excel(writer, sheet_name='A', startcol=0, startrow=0)
writer.close()
