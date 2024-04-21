import requests


class YaGptConfig:
    catalog_id = 'b1g659p7ld8o2k31g37c'
    api_key = 'AQVN0ZRFbyqk97EWUy0KAG9jzqs6oUdcXrNYjYJ-'


def yagpt(query):
    prompt = {"modelUri": f"gpt://{YaGptConfig.catalog_id}/yandexgpt",
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
    headers = {"Content-Type": "application/json", "Authorization": f"Api-Key {YaGptConfig.api_key}"}

    response = requests.post(url, headers=headers, json=prompt)
    result = response.text
    with open('./log.txt', 'a') as f:
        f.write(result)
    return result
