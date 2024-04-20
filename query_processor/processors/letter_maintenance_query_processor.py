import json
from datetime import datetime

from query_processor.data_source.console_data_source import ConsoleDataSource
from query_processor.data_source.letter_maintenance_patent_xlsx_data_source import LetterMaintenancePatentXlsxDataSource
from query_processor.data_source.letter_maintenance_payment_xlsx_data_source import \
    LetterMaintenancePaymentXlsxDataSource
from query_processor.gpt.yagpt import yagpt
from query_processor.processors.processor import QueryProcessor
from query_processor.templates.letter_maintenance_template import LetterMaintenanceDocxTemplate
from query_processor.templates.template import Template


class LetterMaintenanceQueryProcessor(QueryProcessor):
    __name = 'Обслуживание писем'
    __fields = [
        'id',
        'date', 'first_application', 'timestamp', 'main_application',
        'patent_id', 'patent_name', 'payment_order', 'payment_date', 'payment_count'
    ]

    __default_template = LetterMaintenanceDocxTemplate
    __default_payment_xlsx_path = './data_source/docs/LetterMaintenancePayment.xlsx'
    __default_patent_xlsx_path = './data_source/docs/LetterMaintenancePathentNTMK.xlsx'

    __fields_default_datasource = {
        'id': ConsoleDataSource("Введите id письма"),
        'date': ConsoleDataSource("Введите дату написания письма"),
        'first_application': ConsoleDataSource("Введите номер первой  заявки в письме"),
        'timestamp': ConsoleDataSource("Введите время на которое продляете патент"),
        'main_application': ConsoleDataSource("Введите номер заявки на патент, который продляете"),
        'patent_id': ConsoleDataSource("Введите номер патента, который продляете"),
        'patent_name': ConsoleDataSource("Введите имя патент, который продляете"),
        'payment_order': ConsoleDataSource("Введите номер платёжного поручения"),
        'payment_date': ConsoleDataSource("Введите дату оплаты"),
        'payment_count': ConsoleDataSource("Введите стоимость продления")
    }

    __prompt = ("В документе есть эти поля:"
                " payment_xlsx_path - путь к таблице с платёжными поручениями;"
                "patent_xlsx_path - путь к таблице с патентами; "
                "id - номер письма;"
                "date - дата на которую заполняется письмо приведи к формату "
                "%Y-%m-%d числами чтобы её можно было спарсить python datetime.datetime.strptime(date, '%Y-%m-%d');"
                ";first_application - первая заявка;"
                "timestamp - время на которое продляется патент;"
                "main_application - заявка по которой был создан патент;"
                "patent_id - номер патента;"
                "patent_name - название патента;"
                "payment_order - номер платёжного поручения;"
                "payment_date - дата платёжного поручения  приведи к формату"
                " %Y-%m-%d числами чтобы её можно было спарсить python datetime.datetime.strptime(date, '%Y-%m-%d');;"
                "payment_count - сумма платёжного поручения."
                "Вот запрос пользователя: {query}; "
                "Пользователь может ввести несколько значений каждого поля, если это так то запиши их в массив json")

    __can_find_in_payment_xlsx = ['timestamp', 'patent_id', 'payment_order',
                                  'payment_date', 'payment_count']

    __can_find_in_patent_xlsx = ['patent_id', 'patent_name']

    def __init__(self, template: Template | None = None, use_gpt: bool = False):
        self.template = template or self.__default_template()
        self.use_gpt = use_gpt

    @staticmethod
    def get_name():
        return LetterMaintenanceQueryProcessor.__name

    def get_fields_from_user(self, found_fields: dict | None = None):
        # TODO Если в одном из полей несколько значений, то нужно сгенерировать несколько файлов или переспросить об
        #  этом пользователя
        res = {}
        for field in self.__fields:
            if found_fields and field in found_fields:
                if isinstance(found_fields[field], list):
                    res[field] = found_fields[field][0]
                else:
                    res[field] = found_fields[field]
            else:
                res[field] = self.__fields_default_datasource[field].get()
        return self.template.fill(res)

    def process_query(self, query: str):
        """
        Функция генерирует столько файлов сколько найдёт строк с помощью фильтров, если
        не передано не одного поля по которому можно фильтровать xlsx, нужно заполнить
        их руками

        В полях  по которым возможен поиск строк в xlsx может быть несколько значений,

        В полях по которым не ведётся поиск строк в xlsx должны быть только одно значение,
        если GPT обнаружит несколько то берём первое
        приимер
        Составь письма для патентов с номерами 2662850 206343 245109 2811313 с датой оплаты 02.02.2024 и id 2281337
        """
        user_query = self.__prompt.format(query=query)
        res = {}
        if not self.use_gpt:
            return self.get_fields_from_user()

        gpt_ans = yagpt(user_query)
        json_data: dict = json.loads(gpt_ans)
        gpt_res: dict | None = json.loads(json_data.get('result', {})
                                          .get('alternatives', [{}])[0]
                                          .get('message', {})
                                          .get('text'))
        if gpt_res is None:
            print(f"Ошибка работы GPT!!!! {gpt_ans}")
            return ""

        fields_cant_find_in_xlsx = []
        for field in self.__fields:
            if field in gpt_res:
                fild_from_gpt = gpt_res[field]
                if fild_from_gpt is None or (isinstance(fild_from_gpt, list) and len(fild_from_gpt) == 0):
                    continue

                if field in ('date', 'payment_date'):
                    if not isinstance(fild_from_gpt, list):
                        fild_from_gpt = datetime.strptime(fild_from_gpt, '%Y-%m-%d')
                    else:
                        fild_from_gpt = [datetime.strptime(x, '%Y-%m-%d') for x in fild_from_gpt]
                res[field] = fild_from_gpt
                print(f"Gpt обнаружил поле {field} - {fild_from_gpt}")
                if (field not in self.__can_find_in_patent_xlsx and
                        field not in self.__can_find_in_payment_xlsx):
                    if isinstance(fild_from_gpt, list):
                        if len(fild_from_gpt) > 1:
                            print("Это поле не является фильтром, но содержит несколько значений: ", field,
                                  fild_from_gpt)
                            res[field] = fild_from_gpt[0]
                            print(f"Выбрано первое значение: {fild_from_gpt[0]}")
                    else:
                        print("Обнаружено поле, которое не является фильтром: ", field, fild_from_gpt)
                    fields_cant_find_in_xlsx.append(field)

        payment_xlsx_path: any = gpt_res.get('payment_xlsx_path', self.__default_payment_xlsx_path)
        patent_xlsx_path: any = gpt_res.get('patent_xlsx_path', self.__default_patent_xlsx_path)

        if not isinstance(payment_xlsx_path, str):
            if isinstance(payment_xlsx_path, list):
                payment_xlsx_path = payment_xlsx_path[0]
            else:
                print(f"Не удалось получить путь к файлу с платёжными поручениями: {payment_xlsx_path}")
                payment_xlsx_path = self.__default_payment_xlsx_path

        if not isinstance(patent_xlsx_path, str):
            if isinstance(patent_xlsx_path, list):
                patent_xlsx_path = patent_xlsx_path[0]
            else:
                print(f"Не удалось получить путь к файлу с патентами: {patent_xlsx_path}")
                patent_xlsx_path = self.__default_payment_xlsx_path

        print("Файлы xlsx: ", payment_xlsx_path, patent_xlsx_path)

        rows_from_xlsx = []
        try:
            if any((field_from_gpt in self.__can_find_in_payment_xlsx for field_from_gpt in res.keys())):
                filters = {field: res[field] for field in res if field in self.__can_find_in_payment_xlsx}
                print("Фильтр: ", filters)

                payment_xlsx_datasource = LetterMaintenancePaymentXlsxDataSource(payment_xlsx_path)

                rows_from_xlsx = payment_xlsx_datasource.get(filter_dict=filters)
                print("Подходящие строки: ", rows_from_xlsx)
            else:
                print("GPT не обнаружил поля по которым можно было бы отфильтровать строки!!!")
        except Exception as e:
            print("Не удалось открыть файл с платёжными поручениями: ", payment_xlsx_path)
            print(e)

        if len(rows_from_xlsx) == 0:
            return self.get_fields_from_user(res)

        # Заносим в строки те поля, которые переданы пользователем, но которых нет в xlsx
        for row in rows_from_xlsx:
            for field in fields_cant_find_in_xlsx:
                row[field] = res[field]

        patent_datasource: None | LetterMaintenancePatentXlsxDataSource = None
        try:
            patent_datasource = LetterMaintenancePatentXlsxDataSource(patent_xlsx_path)
        except Exception as e:
            print("Не удалось открыть файл с патентами: ", patent_xlsx_path)
            print(e)

        for row in rows_from_xlsx:
            # Если в строке осталось не заполненное поле
            empty_fields = [field for field in self.__fields if field not in row]
            founded_fields_on_past_iterations: list = []
            if len(empty_fields) != 0:
                print("Не все поля заполнены в строке: ", row)
                for field in empty_fields:
                    if field in founded_fields_on_past_iterations:
                        continue
                    if (field in self.__can_find_in_patent_xlsx and
                            patent_datasource is not None and
                            any((field_ in row for field_ in self.__can_find_in_patent_xlsx))):
                        field_filter_for_patent_xlsx = {field_: row[field_] for field_ in row
                                                        if field_ in self.__can_find_in_patent_xlsx}
                        print("Поля для фильтрации в xlsx с патентами: ", field_filter_for_patent_xlsx)
                        found_rows_in_patent_for_row = patent_datasource.get(filter_dict=field_filter_for_patent_xlsx)
                        if len(found_rows_in_patent_for_row) == 1:
                            row_from_patent = found_rows_in_patent_for_row[0]
                            for patent_field in row_from_patent:
                                if patent_field not in row:
                                    row[patent_field] = row_from_patent[patent_field]
                                    founded_fields_on_past_iterations.append(patent_field)
                        elif len(found_rows_in_patent_for_row) > 1:
                            print("Найдено несколько строк с патентами: ", found_rows_in_patent_for_row)
                            print("используем первое значение: ", found_rows_in_patent_for_row[0])
                            row_from_patent = found_rows_in_patent_for_row[0]
                            for patent_field in row_from_patent:
                                if patent_field not in row:
                                    row[patent_field] = row_from_patent[patent_field]
                                    founded_fields_on_past_iterations.append(patent_field)
                        elif len(found_rows_in_patent_for_row) == 0:
                            print("Ничего не нашли")
                            print("Необходимо заполнить поле для письма с:", row)
                            row[field] = self.__fields_default_datasource[field].get()
                            founded_fields_on_past_iterations.append(field)

                    else:
                        #TODO Нужно вывподить пользователю для кокого письма он вводит поле
                        print("Необходимо заполнить поле для письма с:", row)
                        row[field] = self.__fields_default_datasource[field].get()

        res_files = []
        for row in rows_from_xlsx:
            res_file = self.template.fill(row)
            res_files.append(res_file)
        return res_files
