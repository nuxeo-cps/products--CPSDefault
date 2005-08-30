import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase

from Products.CPSDefault import utils

class TestUtils(ZopeTestCase.ZopeTestCase):
    def test_getNonArchivedVersionContextUrl(self):
        url0 = 'http://toto.com/titi/archivedRevision/123'
        url1 = 'http://toto.com/titi'
        self.assertEquals(utils.getNonArchivedVersionContextUrl(url0), url1)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    return suite

