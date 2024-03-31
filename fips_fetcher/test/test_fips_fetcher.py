from pprint import pprint
from unittest import TestCase

import fips_fetcher


class Test(TestCase):
    def test_get_doc_224305(self):
        res = fips_fetcher.get_doc(224305)
        pprint(res)
        self.assertEqual(len(res['authors_72']), 2)

    def test_get_doc_invalid_id(self):
        res = fips_fetcher.get_doc(123123123123)
        self.assertIsNone(res)

