from unittest import TestCase

import fips_fetcher


class Test(TestCase):
    def test_get_doc_224305(self):
        res = fips_fetcher.get_doc(224305)
        print(res)
        self.assertEqual(len(res['authors_72']), 2)

    def test_get_doc_2441856(self):
        res = fips_fetcher.get_doc(2441856, 'RUPAT', 9917)
        print(res)

    def test_get_final_url(self):
        print(fips_fetcher.get_final_url(224305))
