import inspect
import json
import logging

from aiogram import Dispatcher

from query_processor.data_source.date_now_data_source import DateNowDataSource
from query_processor.data_source.source import DataSource
from query_processor.data_source.telegram_data_source import TelegramDataSource
from query_processor.gpt.yagpt import yagpt
from query_processor.processors.processor import QueryProcessor
from query_processor.templates.personal_data_docx_template import PersonalDataDocxTemplate
from query_processor.templates.personal_data_string_template import PersonalDataStringTemplate

logger = logging.getLogger(__name__)


class PersonalDataTelegramQueryProcessor(QueryProcessor):
    __name = 'Соглашения об обработке персональных данных'
    fields_data_source: dict[str, DataSource] = {
        'name': TelegramDataSource('Введите имя: '),
        'address': TelegramDataSource('Введите адрес места жительства: '),
        'document': TelegramDataSource('Введите документ, удостоверяющий личность субъекта персональных данных: '),
        'invention_name': TelegramDataSource('Введите имя изобретения: '),
        'invention_register_number': TelegramDataSource('Введите (при наличии) регистрационного номера заявки: '),
        'applicant': TelegramDataSource('Введите имя заявителя: '),
        'signatory': TelegramDataSource('Введите имя подписанта: '),
        'date': DateNowDataSource()
    }

    prompt = ('Есть шаблон документа "согласие на обработку персональных данных",'
              ' этот шаблон состоит из следующих полей: '
              'name: имя субъекта персональных данных,'
              ' address: адресс, '
              'document: документ удостоверяющий имя субъекта,'
              ' invention_name: название изобретения,'
              ' invention_register_number: регистрационный номер заявки, '
              'applicant: имя заявителя, '
              'signatory: имя подписавшего документ. '
              'Так же дан запрос '
              '{query}.'
              ' Выбери из запроса необходимые поля если они есть. '
              'Выведи ответ в формате json, где если поле есть в запросе напиши его из запроса, '
              'если поля нет в запросе напиши null. Ответь кратко')

    @staticmethod
    def get_name():
        return PersonalDataTelegramQueryProcessor.__name

    def __str__(self):
        return PersonalDataTelegramQueryProcessor.__name

    def __init__(self, use_gpt: bool):
        self.template = PersonalDataDocxTemplate()
        self.use_gpt: bool = use_gpt
        self.tg_dispatcher = Dispatcher.get_current()

    async def async_process_query(self, query: str):
        res = {}
        if self.use_gpt:
            gpt_ans = await yagpt(self.prompt.format(query=query))
            json_data: dict = json.loads(gpt_ans)
            logger.info(f"{self.__name} Ответ GPT: {json.dumps(json_data, indent=4)}")
            gpt_res: dict | None = json.loads(
                json_data.get('result', {}).get('alternatives', [{}])[0].get('message', {}).get('text'))
            if gpt_res is None:
                await self.async_communicate_with_user(f"Ошибка работы GPT!!!! {gpt_ans}")
                return ""
            for field, val in gpt_res.items():
                if val != "null":
                    await self.async_communicate_with_user(f"Gpt обнаружил поле {field} - {val}")

            all_resolved = all((field in gpt_res.keys() for field in self.fields_data_source.keys()))
            if not all_resolved:
                await self.async_communicate_with_user("Заполнены не все поля! Нужно их заполнить.")

            for field in self.fields_data_source:
                if field in gpt_res:
                    res[field] = gpt_res[field]
                else:
                    res[field] = self.fields_data_source[field].get()
                    if inspect.isawaitable(res[field]):
                        res[field] = await res[field]

        else:
            for field in self.fields_data_source:
                res[field] = self.fields_data_source[field].get()
                if inspect.isawaitable(res[field]):
                    res[field] = await res[field]

        return [self.template.fill(res)]
