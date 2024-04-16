import requests


class YaGptConfig:
    catalog_id = 'b1g659p7ld8o2k31g37c'
    api_key = 'AQVN0ZRFbyqk97EWUy0KAG9jzqs6oUdcXrNYjYJ-'


def yagpt(query):
    prompt = {
        "modelUri": f"gpt://{YaGptConfig.catalog_id}/yandexgpt",
        "completionOptions": {
            "stream": False,
            "temperature": 0.2,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "user",
                "text": query
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YaGptConfig.api_key}"
    }

    response = requests.post(url, headers=headers, json=prompt)
    result = response.text
    with open('./log.txt', 'a') as f:
        f.write(result)
    return result
