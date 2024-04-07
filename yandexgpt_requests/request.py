import requests
class GptData:
    catalog_id = 'b1gn33bsgik2omd403v3'#'aje17bdctecq0dvhtgdn' #'ajenvb7l60smt8krul3s' #'aje214b35e13pf8ifp5c' #
    iam_token = 'AQVNwgkWMrgjy9En5KwrDQaL5-YBHM6oAkl4Qr4A'

def yagptexample(gptcommand):
    prompt = {
        "modelUri": f"gpt://{GptData.catalog_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "user",
                "text": gptcommand #"Выдай мне патент 276656 от 01.01.2023"
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {GptData.iam_token}" #t1.9euelZqTnI2UzsmXzYqLx8ySkoyKzu3rnpWakYmdyJPJz4ySi8eUjYqTzIzl8_cPPDVP-e85HVFF_3z909qMk_57zkdUUX-zef1656VmpLNzouOnImZzo2TzZGZycrJ7_zF656VmpLNzouOnImZzo2TzZGZycrJ.34ppQpfavp6DiqQ5xlbXa2tLtXGqwjCle7mQfbSDbOtOHcQJ1UhVdJSWY0Iv53yhX7vyw7MKU1W1dhM9-ChAAN}" #GptData.iam_token}"
    }

    response = requests.post(url, headers=headers, json=prompt)
    result = response.text
    return result