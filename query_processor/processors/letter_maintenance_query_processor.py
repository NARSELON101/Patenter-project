import openpyxl

from query_processor.processors.processor import QueryProcessor


class LetterMaintenanceQueryProcessor(QueryProcessor):
    __name = 'Обслуживание писем'

    def __init__(self):
        pass

    def get_name(self):
        return LetterMaintenanceQueryProcessor.__name

    def process_query(self, rows: list[int] | int):
        pass

