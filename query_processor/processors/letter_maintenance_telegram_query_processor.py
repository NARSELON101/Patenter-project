import json
import json
import logging
import re
from datetime import datetime

from aiogram import Dispatcher

from query_processor.data_source.fips_fetcher_data_source import FipsFetcherDataSource
from query_processor.data_source.letter_maintance_monitoring_data_source import \
    LetterMaintenanceMonitoringXlsxDataSource
from query_processor.data_source.letter_maintenance_patent_xlsx_data_source import LetterMaintenancePatentXlsxDataSource
from query_processor.data_source.letter_maintenance_payment_xlsx_data_source import \
    LetterMaintenancePaymentXlsxDataSource
from query_processor.data_source.telegram_data_source import TelegramDataSource
from query_processor.gpt.yagpt import yagpt
from query_processor.processors.processor import QueryProcessor
from query_processor.templates.letter_maintenance_template import LetterMaintenanceDocxTemplate
from query_processor.templates.template import Template
from utils.telegram_input import telegram_input

logger = logging.getLogger(__name__)


class LetterMaintenanceTelegramQueryProcessor(QueryProcessor):
    __name = 'Письмо о поддержании патента в силе'
    __fields = [
        'id',
        'date', 'timestamp', 'main_application',
        'patent_id', 'patent_name', 'payment_order', 'payment_date', 'payment_count'
    ]

    __default_template = LetterMaintenanceDocxTemplate
    __default_payment_xlsx_path = './query_processor/data_source/docs/LetterMaintenancePayment.xlsx'
    __default_patent_xlsx_path = './query_processor/data_source/docs/LetterMaintenancePathentNTMK.xlsx'
    __default_monitoring_xlsx_path = './query_processor/data_source/docs/LetterMaintenanceMonitoring.xlsx'

    __fields_default_datasource = {
        'id': TelegramDataSource("Введите id письма: "),
        'date': TelegramDataSource("Введите дату написания письма: "),
        'timestamp': TelegramDataSource("Введите время на которое продляете патент: "),
        'main_application': TelegramDataSource(
            "Введите номер заявки на патент, который продляете: "),
        'patent_id': TelegramDataSource("Введите номер патента, который продляете: "),
        'patent_name': TelegramDataSource("Введите имя патент, который продляете: "),
        'payment_order': TelegramDataSource("Введите номер платёжного поручения: "),
        'payment_date': TelegramDataSource("Введите дату оплаты: "),
        'payment_count': TelegramDataSource("Введите стоимость продления: ")
    }

    __prompt = ("В документе есть эти поля:"
                "use_xlsx - использовать ли таблицы с платёжными поручениями и патентами;"
                "monitoring_xlsx_path - путь к таблице с мониторингом;"
                " payment_xlsx_path - путь к таблице с платёжными поручениями;"
                "patent_xlsx_path - путь к таблице с патентами; "
                "id - номер письма;"
                "date - дата написания письма, приведи к формату "
                "%Y-%m-%d числами чтобы её можно было спарсить python datetime.datetime.strptime(date, '%Y-%m-%d');"
                ";first_application - первая заявка;"
                "timestamp - время на которое продляется патент;"
                "main_application - заявка по которой был создан патент;"
                "patent_id - номер патента;"
                "patent_name - название патента;"
                "payment_order - номер платёжного поручения;"
                "payment_date - дата платёжного поручения когда за патент заплатили, приведи к формату"
                " %Y-%m-%d числами чтобы её можно было спарсить python datetime.datetime.strptime(date, '%Y-%m-%d');;"
                "payment_count - сумма платёжного поручения."
                "Вот запрос пользователя: {query}; "
                "Пользователь может ввести несколько значений каждого поля, если это так то запиши их в массив json")

    __can_find_in_payment_xlsx = ['timestamp', 'patent_id', 'payment_order',
                                  'payment_date', 'payment_count']

    __can_find_in_patent_xlsx = ['patent_id', 'patent_name']

    __can_find_in_fips_fetcher = ['main_application', 'patent_id', 'patent_name']

    __can_find_in_monitoring_xlsx = ['patent_name', 'main_application', 'timestamp', 'payment_count']

    def __init__(self, template: Template | None = None, use_gpt: bool = False):
        self.tg_dispatcher = Dispatcher.get_current()
        self.template = template or self.__default_template()
        self.use_gpt = use_gpt

    @staticmethod
    def get_name():
        return LetterMaintenanceTelegramQueryProcessor.__name

    async def async_communicate_with_user(self, prompt: str, *args, **kwargs):
        bot = self.tg_dispatcher.bot
        state = self.tg_dispatcher.current_state()
        if args is not None:
            sep = ' '
            if kwargs is not None:
                sep = kwargs.get('sep', ' ')
            for arg in args:
                prompt += sep
                prompt += str(arg)
        return await self.tg_dispatcher.bot.send_message(state.chat, prompt)

    async def get_fields_from_user(self, found_fields: dict | None = None):
        # TODO Если в одном из полей несколько значений, то нужно сгенерировать несколько файлов или переспросить об
        #  этом пользователя
        res = {}
        for field in self.__fields:
            if found_fields and field in found_fields:
                if isinstance(found_fields[field], list):
                    try:
                        await self.async_communicate_with_user(
                            f"Для поля {field} указано несколько значений, без использования xlsx, "
                            f"будет выбрано {found_fields[field][0]}")
                    except AttributeError as e:
                        logger.error(f"Невозможно общаться с пользователем: {e}")
                        return None
                    res[field] = found_fields[field][0]
                else:
                    res[field] = found_fields[field]
            else:
                res[field] = await self.__fields_default_datasource[field].get()
        return self.template.fill(res)

    async def async_process_query(self, query: str | None = None) -> list[str]:
        """
        Функция генерирует столько файлов сколько найдёт строк с помощью фильтров, если
        не передано не одного поля по которому можно фильтровать xlsx, нужно заполнить
        их руками

        В полях по которым возможен поиск строк в xlsx может быть несколько значений,
        В полях по которым не ведётся поиск строк в xlsx должны быть только одно значение,
        если GPT обнаружит несколько то берём первое.
        Пример:
        Составь письма для патентов с номерами 2662850 206343 245109 2811313 с датой оплаты 02.02.2024 и id 2281337
        В этом примере программа возьмёт из xlsx файла с платёжными поручениями строки с номерами патентов 2662850,
        206343, 245109, 2811313 и строки с датой оплаты 02.02.2024. Добавит к этим строкам поля id 2281337,
        попробует получить поле имя патента из xlsx таблицы с патентами.
        И попросит пользователя ввести поля оставшиеся пустыми.


        Составь письма для патента 2811313 и с датой платёжного поручения 02.02.2024
        """
        if not self.use_gpt:
            return [await self.get_fields_from_user()]

        #  Формируем запрос к GPT
        if query is not None:
            user_query = self.__prompt.format(query=query)
            res = {}
        else:
            logger.error("Не передан запрос!")
            raise RuntimeError("Не передан запрос!")

        #  Отправляем запрос к GPT
        gpt_ans = await yagpt(user_query)
        # Получаем ответ GPT
        json_data: dict = json.loads(gpt_ans)

        logger.info(f"{self.__name} Ответ GPT: {json.dumps(json_data, indent=4)}")

        gpt_ans_txt: str = json_data.get('result', {}).get('alternatives', [{}])[0].get('message', {}).get('text')
        gpt_ans_txt = re.search(r"\{[\n\s\S]*\}", gpt_ans_txt).group(0)
        gpt_res: dict | None = json.loads(gpt_ans_txt)
        if gpt_res is None:
            await self.async_communicate_with_user(f"Ошибка работы GPT!!!! {gpt_ans}")
            return []

        # Обрабатываем полученные данные
        # Список полей которые не являются фильтрами для поиска строк в xlsx
        fields_cant_find_in_xlsx = []
        for field in self.__fields:
            if field in gpt_res:
                fild_from_gpt = gpt_res[field]
                # Если gpt не определил поле то  не добавляем его в res
                if fild_from_gpt is None or (isinstance(fild_from_gpt, list) and len(fild_from_gpt) == 0):
                    continue
                # Если это поле дата, то преобразуем к datetime
                if field in ('date', 'payment_date'):
                    if not isinstance(fild_from_gpt, list):
                        fild_from_gpt = datetime.strptime(fild_from_gpt, '%Y-%m-%d')
                    else:
                        fild_from_gpt = [datetime.strptime(x, '%Y-%m-%d') for x in fild_from_gpt]
                res[field] = fild_from_gpt
                await self.async_communicate_with_user(f"Gpt обнаружил поле {field} - {fild_from_gpt}")
                # Если это поле не является фильтром, то оно должно содержать только 1 значение
                if (field not in self.__can_find_in_patent_xlsx and
                        field not in self.__can_find_in_payment_xlsx and
                        field not in self.__can_find_in_monitoring_xlsx):
                    if isinstance(fild_from_gpt, list):
                        if len(fild_from_gpt) > 1:
                            await self.async_communicate_with_user(
                                "Это поле не является фильтром, но содержит несколько значений: ", field,
                                fild_from_gpt)
                            res[field] = fild_from_gpt[0]
                            await self.async_communicate_with_user(f"Выбрано первое значение: {fild_from_gpt[0]}")
                    else:
                        await self.async_communicate_with_user("Обнаружено поле, которое не является фильтром: ", field,
                                                               fild_from_gpt)
                    fields_cant_find_in_xlsx.append(field)

        # Если не нужно использовать xlsx, то заполняем поля, которые указал пользователь,
        # и спрашиваем его об оставшихся
        if "use_xlsx" in gpt_res:
            use_xlsx = gpt_res["use_xlsx"]
            if use_xlsx is not None and isinstance(use_xlsx, bool) and use_xlsx:
                return [await self.get_fields_from_user(found_fields=res)]

        payment_xlsx_path: any = gpt_res.get('payment_xlsx_path', self.__default_payment_xlsx_path)
        patent_xlsx_path: any = gpt_res.get('patent_xlsx_path', self.__default_patent_xlsx_path)
        monitoring_xlsx_path: any = gpt_res.get('monitoring_xlsx_path', self.__default_monitoring_xlsx_path)

        if not isinstance(payment_xlsx_path, str):
            if isinstance(payment_xlsx_path, list):
                payment_xlsx_path = payment_xlsx_path[0]
            else:
                await self.async_communicate_with_user(
                    f"Не удалось получить путь к файлу с платёжными поручениями: {payment_xlsx_path}")
                payment_xlsx_path = self.__default_payment_xlsx_path

        if not isinstance(patent_xlsx_path, str):
            if isinstance(patent_xlsx_path, list):
                patent_xlsx_path = patent_xlsx_path[0]
            else:
                await self.async_communicate_with_user(
                    f"Не удалось получить путь к файлу с патентами: {patent_xlsx_path}")
                patent_xlsx_path = self.__default_patent_xlsx_path

        if not isinstance(monitoring_xlsx_path, str):
            if isinstance(monitoring_xlsx_path, list):
                monitoring_xlsx_path = monitoring_xlsx_path[0]
            else:
                await self.async_communicate_with_user(
                    f"Не удалось получить путь к файлу с платёжными поручениями: {monitoring_xlsx_path}")
                monitoring_xlsx_path = self.__default_monitoring_xlsx_path

        await self.async_communicate_with_user("Файлы xlsx: ", payment_xlsx_path, patent_xlsx_path,
                                               monitoring_xlsx_path)

        # Ищем в xlsx с платёжными поручения строки по которые подходят под фильтры указанные пользователем
        rows_from_xlsx = []
        try:
            # Если пользователь указал хотя бы одно поле которое может быть фильтром,
            # то открываем xlsx с платёжными поручениями
            if any((field_from_gpt in self.__can_find_in_payment_xlsx for field_from_gpt in res.keys())):
                filters = {field: res[field] for field in res if field in self.__can_find_in_payment_xlsx}
                await self.async_communicate_with_user("Фильтр: ", filters)

                payment_xlsx_datasource = LetterMaintenancePaymentXlsxDataSource(payment_xlsx_path)

                rows_from_xlsx = payment_xlsx_datasource.get(filter_dict=filters)
                await self.async_communicate_with_user("Подходящие строки: ", rows_from_xlsx)
            else:
                await self.async_communicate_with_user(
                    "GPT не обнаружил поля по которым можно было бы отфильтровать строки!!!")
        except Exception as e:
            await self.async_communicate_with_user("Не удалось открыть файл с платёжными поручениями: ",
                                                   payment_xlsx_path)
            await self.async_communicate_with_user(e)

        # Если пользователь не указал поля по которым можно было бы найти строки в xlsx,
        # то просим пользователя заполнить все поля самому
        if len(rows_from_xlsx) == 0:
            return [await self.get_fields_from_user(res)]

        # Заносим в строки те поля, которые переданы пользователем, но которых нет в xlsx
        # такие поля будут одинаковыми во всех полях!!!!
        for row in rows_from_xlsx:
            for field in fields_cant_find_in_xlsx:
                row[field] = res[field]

        patent_datasource: None | LetterMaintenancePatentXlsxDataSource = None
        try:
            patent_datasource = LetterMaintenancePatentXlsxDataSource(patent_xlsx_path)
        except Exception as e:
            await self.async_communicate_with_user("Не удалось открыть файл с патентами: ", patent_xlsx_path)
            await self.async_communicate_with_user(e)

        monitoring_datasource: None | LetterMaintenanceMonitoringXlsxDataSource = None
        try:
            monitoring_datasource = LetterMaintenanceMonitoringXlsxDataSource(monitoring_xlsx_path)
        except Exception as e:
            await self.async_communicate_with_user("Не удалось открыть файл с патентами: ", monitoring_xlsx_path)
            await self.async_communicate_with_user(e)

        fips_fetcher_datasource = FipsFetcherDataSource()

        # Заполняем поля, которые остались пустыми в строках
        for row in rows_from_xlsx:
            # Если в строке осталось не заполненное поле
            empty_fields = [field for field in self.__fields if field not in row]
            founded_fields_on_past_iterations: list = list(row.keys())
            if len(empty_fields) != 0:
                await self.async_communicate_with_user("Не все поля заполнены в строке: ", row)
                for field in empty_fields:
                    # Если мы обнаружили это поле где-то на предыдущих итерациях, пока искали другие поля
                    if field in founded_fields_on_past_iterations:
                        continue
                    # Если это поле может быть фильтром в xlsx с патентами, то ищем в нём
                    if (field in self.__can_find_in_patent_xlsx and
                            patent_datasource is not None and
                            any((field_ in row for field_ in self.__can_find_in_patent_xlsx))):
                        field_filter_for_patent_xlsx = {field_: row[field_] for field_ in row
                                                        if field_ in self.__can_find_in_patent_xlsx}
                        await self.async_communicate_with_user("Поля для фильтрации в xlsx с патентами: ",
                                                               field_filter_for_patent_xlsx)
                        found_rows_in_patent_for_row = patent_datasource.get(filter_dict=field_filter_for_patent_xlsx)
                        if len(found_rows_in_patent_for_row) == 1:
                            row_from_patent = found_rows_in_patent_for_row[0]
                            for patent_field in row_from_patent:
                                if patent_field not in row:
                                    await self.async_communicate_with_user(
                                        f"Заполняем поле: {patent_field} значением: {row_from_patent[patent_field]}")
                                    row[patent_field] = row_from_patent[patent_field]
                                    founded_fields_on_past_iterations.append(patent_field)
                        elif len(found_rows_in_patent_for_row) > 1:
                            await self.async_communicate_with_user("Найдено несколько строк с патентами: ",
                                                                   found_rows_in_patent_for_row)
                            await self.async_communicate_with_user("используем первое значение: ",
                                                                   found_rows_in_patent_for_row[0])
                            row_from_patent = found_rows_in_patent_for_row[0]
                            for patent_field in row_from_patent:
                                if patent_field not in row:
                                    await self.async_communicate_with_user(
                                        f"Заполняем поле: {patent_field} значением: {row_from_patent[patent_field]}")
                                    row[patent_field] = row_from_patent[patent_field]
                                    founded_fields_on_past_iterations.append(patent_field)
                        elif len(found_rows_in_patent_for_row) == 0:
                            await self.async_communicate_with_user("Ничего не нашли")

                    if field in self.__can_find_in_monitoring_xlsx and field not in founded_fields_on_past_iterations:
                        await self.async_communicate_with_user("Ищем в xlsx с мониторингом")
                        found_rows = monitoring_datasource.get(filter_dict={'patent_id': row['patent_id']})
                        new_data: None | dict = None
                        if isinstance(found_rows, list):
                            if len(found_rows) == 0:
                                await self.async_communicate_with_user("Ничего не нашли")
                            else:
                                await self.async_communicate_with_user("Найдено несколько строк с мониторингом: ",
                                                                       found_rows)
                                await self.async_communicate_with_user("Используется первая строка: ", found_rows[0])
                                new_data = found_rows[0]
                        if new_data is not None:
                            for monitoring_field in new_data:
                                if monitoring_field not in row:
                                    founded_fields_on_past_iterations.append(monitoring_field)
                                    await self.async_communicate_with_user(
                                        "В файле с мониторингом обнаруженною поле : ", monitoring_field)
                                    row[monitoring_field] = new_data[monitoring_field]

                    # Ищем информацию о поле патента на сайте ФИПС если не нашли её до этого
                    if field in self.__can_find_in_fips_fetcher and field not in founded_fields_on_past_iterations:
                        patent_id = row.get("patent_id")
                        if patent_id is not None:
                            await self.async_communicate_with_user("Обращение к ФИПС по номеру патента: ", patent_id)
                            found_rows_in_fips = fips_fetcher_datasource.get(patent_id)
                            if found_rows_in_fips is not None:
                                if "main_application" not in row:
                                    main_application = found_rows_in_fips.get("application_id_21")
                                    if main_application is not None:
                                        row["main_application"] = main_application
                                        founded_fields_on_past_iterations.append('main_application')
                                    else:
                                        await self.async_communicate_with_user(
                                            "В ответе ФИПС не обнаружены поле application_id_21")
                                if "patent_name" not in row:
                                    patent_name = found_rows_in_fips.get("patent_name_54")
                                    if patent_name is not None:
                                        row["patent_name"] = patent_name
                                        founded_fields_on_past_iterations.append('patent_name')
                                    else:
                                        await self.async_communicate_with_user(
                                            "В ответе ФИПС не обнаружены поле patent_name")

                            else:
                                await self.async_communicate_with_user("Ничего не нашли")
                        else:
                            await self.async_communicate_with_user(
                                "Незаполнен номер патента, обращение к ФИПС невозможно")
                    if field not in row or row[field] is None:
                        row[field] = await self.__fields_default_datasource[field].get()

        # Генерируем файлы
        res_files = []
        for row in rows_from_xlsx:
            res_file = self.template.fill(row)
            res_files.append(res_file)
        return res_files
