import re

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from query_processor.data_source.source import DataSource


class LetterMaintenanceXlsxDataSource(DataSource):
    __fields_to_xlsx_column = {'timestamp': 20, 'patent_id': 20, 'payment_order': 18,
                               'payment_date': 13, 'payment_count': 17}

    def __init__(self, xlsx_file_path):
        self.xlsx_file_path = xlsx_file_path

        workbook = openpyxl.load_workbook(self.xlsx_file_path)
        # Define variable to read the active sheet:
        worksheet: Worksheet = workbook.active
        res = {}
        for row in args:
            if not isinstance(row, int):
                continue
            row += 1
            for field, column in self.__fields_to_xlsx_column.items():
                if field == "timestamp":
                    timestamp_str = worksheet.cell(row=row, column=column).value
                    continue
                if field == "patent_id":
                    patent_str = worksheet.cell(row=row, column=column).value
                    continue
