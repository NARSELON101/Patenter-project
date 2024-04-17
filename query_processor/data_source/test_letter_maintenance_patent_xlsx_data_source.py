from unittest import TestCase

from query_processor.data_source.letter_maintenance_patent_xlsx_data_source import LetterMaintenancePatentXlsxDataSource


class TestLetterMaintenancePatentXLSXDataSource(TestCase):
    def test_get(self):
        datasource = LetterMaintenancePatentXlsxDataSource("./docs/LetterMaintenancePathentNTMK.xlsx")
        datasource.get(2811313, 2800641, 2787298)
