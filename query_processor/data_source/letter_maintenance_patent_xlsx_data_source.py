import openpyxl
from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from query_processor.data_source.xlsx_data_source import XlsxDataSource


class LetterMaintenancePatentXlsxDataSource(XlsxDataSource):
    _fields_to_xlsx_column = {'patent_name': 4, 'patent_id': 2}

    def __init__(self, xlsx_file_path):
        super().__init__(xlsx_file_path=xlsx_file_path)

