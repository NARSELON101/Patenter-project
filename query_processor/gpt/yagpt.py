import logging

import aiohttp
import requests

from loader import config

logger = logging.getLogger(__name__)


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
