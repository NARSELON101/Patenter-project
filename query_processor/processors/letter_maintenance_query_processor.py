from query_processor.processors.processor import QueryProcessor


class LetterMaintenanceQueryProcessor(QueryProcessor):

    __name = 'Обслуживание писем'

    def get_name(self):
        return LetterMaintenanceQueryProcessor.__name

    def process_query(self, query: str):
        pass