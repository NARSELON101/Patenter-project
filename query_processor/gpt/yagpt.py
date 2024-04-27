import asyncio
import logging
import time

import aiohttp

from loader import config

logger = logging.getLogger(__name__)

prev_req_time: float | None = None


class YaGptTimer:

    def __init__(self, time_to_sleep=None):
        self.time_to_sleep = time_to_sleep or config.ya_gpt.time_to_sleep
        self.prev_req_time = None

    async def __aenter__(self):
        current_time = time.time()
        if True or self.prev_req_time is not None:
            while True or current_time - self.prev_req_time < self.time_to_sleep:
                await asyncio.sleep(self.time_to_sleep)
        self.prev_req_time = current_time

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


async def yagpt(query):
    prompt = {"modelUri": f"gpt://{config.ya_gpt.catalog_id}/yandexgpt",
              "completionOptions": {"stream": False, "temperature": 0.1, "maxTokens": "2000"},
              "messages": [{"role": "user", "text": query},
                           {"role": "system",
                            "text": "Ты цифровой помощник заполнителя документов: "
                                    "пользователь отправляет тебе свой запрос и "
                                    "поля документа которые нужно заполнить, "
                                    "ты разбираешь запрос на эти поля документа по смыслу."
                                    "Ты должен вернуть JSON, где ключи этих полей являются названиями полей документа,"
                                    " а значения этих полей - значениями полей документа, которые ты нашёл в запросе. "
                                    "Если тебе не удалось заполнить поле информацией из запроса,"
                                    " напиши в его поле в JSON null."
                                    " Не нужно отвечать лишнего только JSON, не нужно писать слово JSON в начале. "
                                    "Напиши только один JSON, который содержит ключами поля документа, "
                                    "а значениями, или"
                                    "массив значений которые ты нашёл в запросе пользователя если их несколько,"
                                    " или одно значение если оно одно"}]}

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {"Content-Type": "application/json", "Authorization": f"Api-Key {config.ya_gpt.api_key}"}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=prompt) as response:
            result = await response.text()
            return result
