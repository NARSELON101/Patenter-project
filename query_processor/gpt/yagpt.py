import asyncio
import logging
import time

import aiohttp

from loader import config

logger = logging.getLogger(__name__)

__time_for_req_condition: asyncio.Condition = asyncio.Condition()
__wakeup_task: asyncio.Task | None = None


async def __notify_when_can_req():
    prev_req_time: float | None = None
    while True:
        curr_time = time.time()
        if prev_req_time is not None and curr_time - prev_req_time < config.ya_gpt.time_to_sleep:
            while curr_time - prev_req_time < config.ya_gpt.time_to_sleep:
                curr_time = time.time()
                await asyncio.sleep(config.ya_gpt.time_to_sleep)
                pass
        prev_req_time = time.time()
        async with __time_for_req_condition:
            __time_for_req_condition.notify()


async def yagpt(query):
    global __wakeup_task

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

    if __wakeup_task is None:
        __wakeup_task = asyncio.create_task(__notify_when_can_req())

    async with __time_for_req_condition:
        await __time_for_req_condition.wait()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=prompt) as response:
                result = await response.text()
                return result
