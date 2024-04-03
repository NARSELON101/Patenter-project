import json

from query_processor.data_source.console_data_source import ConsoleDataSource
from query_processor.data_source.date_now_data_source import DateNowDataSource
from query_processor.data_source.source import DataSource
from query_processor.gpt.yagpt import yagpt
from query_processor.processors.processor import QueryProcessor
from query_processor.templates.template import Template


class PersonalDataQueryProcessor(QueryProcessor):
    __name = 'Процессор для Соглашения об обработке персональных данных'
    fields_data_source: dict[str, DataSource] = {
        'name': ConsoleDataSource('Введите имя: '),
        'address': ConsoleDataSource('Введите адрес места жительства: '),
        'document': ConsoleDataSource('Введите документ, удостоверяющий личность субъекта персональных данных: '),
        'invention_name': ConsoleDataSource('Введите имя изобретения: '),
        'invention_register_number': ConsoleDataSource('Введите (при наличии) регистрационного номера заявки: '),
        'applicant': ConsoleDataSource('Введите имя заявителя: '),
        'signatory': ConsoleDataSource('Введите имя подписанта: '),
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
        return PersonalDataQueryProcessor.__name

    def __str__(self):
        return PersonalDataQueryProcessor.__name

    def __init__(self, use_gpt: bool, template: Template):
        self.template = template
        self.use_gpt: bool = use_gpt

    def process_query(self, query: str):
        res = {}
        if self.use_gpt:
            gpt_ans = yagpt(self.prompt.format(query=query))
            json_data = json.loads(gpt_ans)
            gpt_res: dict = json.loads(json_data['result']['alternatives'][0]['message']['text'])

            for field, val in gpt_res.items():
                if val != "null":
                    print(f"Gpt обнаружил поле {field} - {val}")

            all_resolved = all((field in gpt_res.keys() for field in self.fields_data_source.keys()))
            if not all_resolved:
                print("Заполнены не все поля! Нужно их заполнить.")

            for field in self.fields_data_source:
                if field in gpt_res:
                    res[field] = gpt_res[field]
                else:
                    res[field] = self.fields_data_source[field].get()
        else:
            for field in self.fields_data_source:
                res[field] = self.fields_data_source[field].get()

        return self.template.fill(res)
