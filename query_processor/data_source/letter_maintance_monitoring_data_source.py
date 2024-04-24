import openpyxl
from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from query_processor.data_source.xlsx_data_source import XlsxDataSource


class LetterMaintenanceMonitoringXlsxDataSource(XlsxDataSource):
    _fields_to_xlsx_column = {'patent_id': 6, 'patent_name': 3,
                              'main_application': 5, 'timestamp': 10, 'payment_count': 12}

    def __init__(self, xlsx_file_path):
        super().__init__(xlsx_file_path=xlsx_file_path)

