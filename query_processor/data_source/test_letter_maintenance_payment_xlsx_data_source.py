from unittest import TestCase

from query_processor.data_source.letter_maintenance_payment_xlsx_data_source import LetterMaintenanceXlsxDataSource


class TestLetterMaintenancePaymentXLSXDataSource(TestCase):
    def test_get(self):
        datasource = LetterMaintenanceXlsxDataSource("./docs/LetterMaintenancePayment.xlsx")
        datasource.get(1, 2, 3)
