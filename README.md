# Patenter-project

## Использование парсера данных с ФИПС
Использование: `python -m fips_fetcher {id-документа}`


## Развертывание системы во внутреннем контуре
1. Поменять значения `BOT_TOKEN`, `YAGPT_CATALOG_ID`, `YAGPT_API_KEY` в файле `.env` на свои значения.
  * `BOT_TOKEN` - можно получить при создании своего TG bot в Telegram
  * `YAGPT_CATALOG_ID` и `YAGPT_API_KEY` - можно получить из сервиса Yandex Cloud (опционально, если хотите использовать при заполнении полей через запрос)
Остальные настройки можно менять по желанию
2. Запуск системы производится через команду `docker compose up`
