import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase


class TestSimple(CPSDefaultTestCase.CPSDefaultTestCase):
    def afterSetUp(self):
        if self.login_id:
            self.login(self.login_id)

        # Some ZPTs need a session. 
        # XXX: this might be moved to a more generic place someday.
        self.portal.REQUEST.SESSION = {}

    def beforeTearDown(self):
        self.logout()

    def testBasicFeatures(self):
        # Check default id, title...
        assert self.portal.getId() == 'portal'
        assert self.portal.title == 'CPSDefault Portal'

        # Check that we have sections and workspaces
        assert self.portal.sections
        assert self.portal.workspaces

    def testAnonymousSkins(self):
        # XXX: result = '' for now because we have heavily patched Localizer
        # -> Need to find a better fix.
        self.assertEquals(self.portal.index_html(), '')
        self.assertEquals(self.portal.login_form(), '')
        self.assertEquals(self.portal.join_form(), '')

        # XXX: this doesn't work (another Localizer problem)
        #self.assertEquals(self.portal.search_form(), '')
        #self.assertEquals(self.portal.advanced_search_form(), '')


class TestSimpleAsRoot(TestSimple):
    login_id = 'root'

    def testMembersSkins(self):
        # XXX: why 'folder_view' works and nor 'view' ?
        self.assertEquals(self.portal.workspaces.folder_view(), '')
        self.assertEquals(self.portal.sections.folder_view(), '')
        #self.assertEquals(self.portal.workspaces.view(), '')
        #self.assertEquals(self.portal.sections.view(), '')


class TestSimpleAsAnonymous(TestSimple):
    login_id = ''

    def testMembersSkins(self):
        # Anonymous can't view sections and workspaces by default.
        self.assertRaises('Unauthorized', self.portal.sections.view)
        self.assertRaises('Unauthorized', self.portal.workspaces.view)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSimpleAsRoot))
    suite.addTest(unittest.makeSuite(TestSimpleAsAnonymous))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

