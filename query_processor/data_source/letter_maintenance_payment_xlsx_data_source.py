import re

from openpyxl.cell import Cell

from query_processor.data_source.xlsx_data_source import XlsxDataSource


class LetterMaintenancePaymentXlsxDataSource(XlsxDataSource):
    _fields_to_xlsx_column = {'timestamp': 20, 'patent_id': 20, 'payment_order': 18,
                              'payment_date': 13, 'payment_count': 17}

    def __init__(self, xlsx_file_path):
        super().__init__(xlsx_file_path=xlsx_file_path)

    def parse_row(self, row: tuple[Cell, ...]) -> dict:
        res = {}
        for field, column in self._fields_to_xlsx_column.items():
            if field == "timestamp":
                timestamp_str = row[column - 1].value
                if timestamp_str is None:
                    return {}
                res[field] = int(re.search(r"\(за (\d+)", timestamp_str).group(1))
                continue
            if field == "patent_id":
                patent_str = row[column - 1].value
                try:
                    res[field] = int(re.search(r"(\d+)\s*$", patent_str).group(1))
                except AttributeError as e:
                    print(e)
                    res[field] = None
                continue
            res[field] = row[column - 1].value
        return res
