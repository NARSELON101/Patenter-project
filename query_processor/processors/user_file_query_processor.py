import json
import logging
import re

from aiogram import Dispatcher

from query_processor.data_source.telegram_data_source import TelegramDataSource
from query_processor.gpt.yagpt import yagpt
from query_processor.processors.processor import QueryProcessor
from query_processor.templates.user_file_templater import UserFileTemplate
from utils.models import Document

logger = logging.getLogger(__name__)


class UserQueryProcessor(QueryProcessor):
    __name = 'UserQueryProcessor'
    __default_data_source = TelegramDataSource

    def __init__(self, use_gpt: bool, file: Document):
        self.prompt = None
        self.use_gpt = use_gpt
        self.file = file
        self.fields_metadata = self.file.get_field_metadate_dict()
        self.__fields = [field['field'] for field in self.fields_metadata]
        self.template_file = file.document
        self.template = UserFileTemplate(self.template_file)
        self.__name = file.name or file.document
        self.tg_dispatcher = Dispatcher.get_current()

    @staticmethod
    def get_name():
        return UserQueryProcessor.__name

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
                        raise
                    res[field] = found_fields[field][0]
                else:
                    res[field] = found_fields[field]
            else:
                res[field] = await self.__default_data_source(f"Введите данные для {field}").get()
        return self.template.fill(res)

    async def async_process_query(self, query: str) -> list[str]:
        if not self.use_gpt:
            return [await self.get_fields_from_user()]
        fields_desc = "; ".join(
            [f"{field['field']} - {field['gpt_description']}" for field in self.fields_metadata])

        #  Формируем запрос к GPT
        if query is not None:
            self.prompt = (f"В документе есть эти поля:"
                           f"{fields_desc} "
                           f"Запрос пользователя: {query}")
            res = {}
        else:
            logger.error("Не передан запрос!")
            raise RuntimeError("Не передан запрос!")

        #  Отправляем запрос к GPT
        gpt_ans = await yagpt(self.prompt)
        # Получаем ответ GPT
        json_data: dict = json.loads(gpt_ans)

        logger.info(f"{self.__name} Ответ GPT: {json.dumps(gpt_ans, indent=4)}")

        gpt_ans_txt: str = json_data.get('result', {}).get('alternatives', [{}])[0].get('message', {}).get('text')
        if gpt_ans_txt is None:
            raise RuntimeError(f"Не удалось получить ответ от GPT: {gpt_ans}")
        gpt_ans_txt = re.search(r"\{[\n\s\S]*\}", gpt_ans_txt).group(0)
        gpt_res: dict | None = json.loads(gpt_ans_txt)
        if gpt_res is None:
            await self.async_communicate_with_user(f"Ошибка работы GPT!!!! {gpt_ans}")
            return []

        for field, val in gpt_res.items():
            if val != "null":
                await self.async_communicate_with_user(f"Gpt обнаружил поле {field} - {val}")

        all_resolved = all((field in gpt_res.keys() for field in self.__fields))
        if not all_resolved:
            await self.async_communicate_with_user("Заполнены не все поля! Нужно их заполнить.")

        return [await self.get_fields_from_user(gpt_res)]
