import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSTestCase

class TestSimple(CPSTestCase.CPSTestCase):
    def test1(self):
        assert self.portal.getId() == 'portal'
        assert self.portal.title == ''


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSimple))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

