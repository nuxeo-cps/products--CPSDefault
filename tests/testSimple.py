import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase

from pprint import pprint


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

    def testAdminSkinsAtRoot(self):
        self.assertEquals(self.portal.directories(), '')
        #self.assertEquals(self.portal.box_manage_form(), '')
        #self.assertEquals(self.portal.create_box_form(), '')
        self.assertEquals(self.portal.reconfig_form(), '')

    def testAdminSkinsAtWorkspaces(self):
        ws = self.portal.workspaces
        self.assertEquals(ws.folder_view(), '')
        self.assertEquals(ws.folder_factories(), '')
        #self.assertEquals(ws.folder_contents(), '')
        self.assertEquals(ws.folder_localrole_form(), '')
        #self.assertEquals(ws.box_manage_form(), '')

    def testPlayWithBoxes(self):
        btool = self.portal.portal_boxes
        for box_name in ('action_user', 'action_portal'):
            box = getattr(self.portal['.cps_boxes_root'], box_name)
            box.minimize()
            # XXX: I should be able to test if the box is minimized now
            box.maximize()
            # XXX: I should be able to test if the box is maximized now
            box.close()
            # XXX: I should be able to test if the box is closed now
            box.maximize()
            # XXX: I should be able to test if the box is maximized now

            # XXX: raises an error, something is fishy here
            #box.render()


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

