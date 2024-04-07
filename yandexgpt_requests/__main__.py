import requests

from request import yagptexample

if __name__ == '__main__':
    start_yagpt = input("Хотите задать запрос?(Y/N) \n")
    if start_yagpt in ['Y']:
        start_yagpt = True
    else:
        start_yagpt = False
    gptcommand = ''
    if start_yagpt:
        gptcommand = input("Введите запрос для YaGPT: ")
    result = yagptexample(gptcommand)
    print(result)