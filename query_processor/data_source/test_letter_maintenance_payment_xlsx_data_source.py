from unittest import TestCase

from query_processor.data_source.letter_maintenance_payment_xlsx_data_source import \
    LetterMaintenancePaymentXlsxDataSource


class TestLetterMaintenancePaymentXLSXDataSource(TestCase):
    def test_get(self):
        datasource = LetterMaintenancePaymentXlsxDataSource("./docs/LetterMaintenancePayment.xlsx")
        datasource.get(1, 2, 3)
