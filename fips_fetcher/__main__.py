from fips_fetcher import *

if __name__ == '__main__':
    import sys
    from pprint import pprint
    if len(sys.argv) < 2:
        exit('Использование: python -m fips_fetcher {id-документа} {db} {rn}')
    id_ = sys.argv[1]
    print(f"Получаем данные по ссылке {get_final_url(id_, FipsFetcher.default_db, FipsFetcher.default_rn)}")
    res = get_doc(int(id_))
    if res is not None:
        print("Результат:")
        pprint(res)
    else:
        print("Ничего не найдено 😭")
