import os

from letter_maintenance_template import LetterMaintenanceDocxTemplate

from unittest import TestCase


class TestLetterMaintenance(TestCase):
    def test_fill(self):
        print(os.getcwd())
        template = LetterMaintenanceDocxTemplate()
        data = {field: f"test {field}" for field in template.get_fields()}
        template.fill(data)
