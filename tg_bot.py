import asyncio
from dataclasses import dataclass
from datetime import datetime
from fileinput import filename
import os, io

from aiogram import Bot, Dispatcher, executor, types 

from controllers import get_organisations_data
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')

bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot)



@dataclass
class States:
    is_process: bool = False


states = States()


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    answer_msg = """
        Доступные комманды:

        /get_reports
        Комманда принимает файл с номерами ИНН и возвращает
        файл с собранными данными. До отправки комманды необходимо прикрепить 
        файс номерами ИНН
        Файл с номерами ИНН должен быть в формате TXT.

        Каждый ИНН должен быть расположен на отдельной строке.
        Например, файл с тремя ИНН должен выглядеть так:

        ИНН1
        ИНН2
        ИНН3

        /help
        Выводит список комманд с их описанием
    """ 
    await message.answer(answer_msg)


@dp.message_handler(commands=['get_reports'])
async def get_reports(message: types.Message):
    states.is_process= True
    await message.answer('Присылай файл с ИНН')
   

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def file_processing(message: types.Message):

    if message.document:
        file_name = message.document.file_name
        if not states.is_process:
            answer_msg = f"""
            Если нужно обработать файл {file_name} выполните следующие действия:
            1) Отправьте команду /get_reports
            2) Отправьте файл {file_name}
            """
        else:    
            answer_msg = f'Обработка файла {file_name}'
            f = await message.document.download(destination_file=io.BytesIO())
            inns = [int(line.decode('UTF-8')) for line in f.readlines()]
            f.close()

            name = f'orgs_data_{datetime.now().strftime("%Y_%m_%d_%H_%M")}.xlsx'
            orgs_data =io.BytesIO()
            get_organisations_data(inns=inns, save_path=orgs_data).close()
            orgs_data.seek(0)
            outfile = types.InputFile(orgs_data, filename=name)
            await message.answer_document(outfile)

    else:
        answer_msg = 'Ты не прислал файл'

    states.is_process = False
    await message.answer(answer_msg) 


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
