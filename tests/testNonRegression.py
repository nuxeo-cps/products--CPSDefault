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
        # Test that we can create a subobject with same id as its
        # container
        sections = self.portal.sections
        self.assertEquals(
            sections.content_create('Section', title='sections'),
            'sections')
        # But if we do it twice, we get another id
        new_id = sections.content_create('Section', title='sections')
        self.assertNotEquals(new_id, 'sections')
        self.assert_(new_id.startswith('sections'))

        # Same for workspaces (just for fun)
        workspaces = self.portal.workspaces
        self.assertEquals(
            workspaces.content_create('Workspace', title='workspaces'),
            'workspaces')
        new_id = workspaces.content_create('Workspace', title='workspaces')
        self.assertNotEquals(new_id, 'workspaces')
        self.assert_(new_id.startswith('workspaces'))

    def testUpdater(self):
        # Test that installer can be also called as updater
        self.assert_(self.portal.cpsupdate())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNonRegression))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

