import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from query_processor.data_source.source import DataSource


class LetterMaintenancePatentXlsxDataSource(DataSource):
    __fields_to_xlsx_column = {'patent_name': 3, 'patent_id': 1}

    def __init__(self, xlsx_file_path):
        self.xlsx_file_path = xlsx_file_path

    def get(self, *patents, **kwargs):
        """
        Получает список строк информацию о который нужно найти.
        """
        workbook = openpyxl.load_workbook(self.xlsx_file_path)
        worksheet: Worksheet = workbook.active
        rows_to_patent = {}
        for row in worksheet.iter_rows(min_row=2, ):
            row_patent_id = row[self.__fields_to_xlsx_column['patent_id']].value
            if row_patent_id in patents:
                rows_to_patent[row_patent_id] = row[
                    self.__fields_to_xlsx_column['patent_name']].value
        return rows_to_patent
