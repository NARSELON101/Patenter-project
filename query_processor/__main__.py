from query_processor.processors.letter_maintenance_query_processor import LetterMaintenanceQueryProcessor
from query_processor.processors.processing_of_personal_data_query_processor import PersonalDataQueryProcessor
from query_processor.templates.personal_data_string_template import PersonalDataStringTemplate

if __name__ == '__main__':
    processors = [PersonalDataQueryProcessor, LetterMaintenanceQueryProcessor]
    print("Доступные процессоры: \n")
    for i, processor in enumerate(processors, start=1):
        print(i, processor.get_name())

    print()

    which_processor = int(input("Выберите процессор (числом): ")) - 1
    if which_processor < 0 or which_processor > len(processors):
        exit("Неправильный процессор!")
    use_gpt = input("Использовать GPT? (Y/Д если да - пробел если нет): ")
    if use_gpt in ['Y', 'y', 'Д', 'д']:
        use_gpt = True
    else:
        use_gpt = False
    processor = processors[which_processor](use_gpt=use_gpt)
    query = ''
    if use_gpt:
        query = input("Введите запрос для GPT: ")
    res = processor.process_query(query)
    print(res)

