import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase

from pprint import pprint


class TestNonRegression(CPSDefaultTestCase.CPSDefaultTestCase):
    def afterSetUp(self):
        self.login('root')

        # Some ZPTs need a session. 
        # XXX: this might be moved to a more generic place someday.
        self.portal.REQUEST.SESSION = {}
        #self.portal.REQUEST.form = {}

    def beforeTearDown(self):
        self.logout()

    #
    #
    #
    def testIdCollision(self):
        sections = self.portal.sections
        self.assertEquals(
            sections.content_create('Section', title='sections'),
            'sections')
        self.assertNotEquals(
            sections.content_create('Section', title='sections'),
            'sections')

        workspaces = self.portal.workspaces
        self.assertEquals(
            workspaces.content_create('Workspace', title='workspaces'),
            'workspaces')
        self.assertNotEquals(
            workspaces.content_create('Workspace', title='workspaces'),
            'workspaces')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNonRegression))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

