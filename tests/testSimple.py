import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase

from Products.CMFCore.tests.base.utils import has_path


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
        self.assertEquals(self.portal.getId(), 'portal')
        self.assertEquals(self.portal.title, 'CPSDefault Portal')

        # Check that we have sections and workspaces
        self.assert_(self.portal.sections)
        self.assert_(self.portal.workspaces)

    def testAnonymousSkins(self):
        self.assert_(self.portal.index_html())
        self.assert_(self.portal.login_form())
        self.assert_(self.portal.join_form())
        self.assert_(self.portal.search_form())
        self.assert_(self.portal.advanced_search_form())


class TestSimpleAsRoot(TestSimple):
    login_id = 'root'

    def testMembersSkins(self):
        self.assert_(self.portal.workspaces.folder_view())
        self.assert_(self.portal.sections.folder_view())

    def testAdminSkinsAtRoot(self):
        self.assert_(self.portal.directories())
        self.assert_(self.portal.box_manage_form())
        self.assert_(self.portal.box_create_form())
        self.assert_(self.portal.reconfig_form())

    def testAdminSkinsAtSectionsAndWorkspaces(self):
        for folder in (self.portal.workspaces, self.portal.sections):
            self.assert_(folder.folder_view())
            self.assert_(folder.folder_factories())
            self.assert_(folder.folder_contents())
            self.assert_(folder.folder_edit_form())
            self.assert_(folder.metadata_edit_form())
            self.assert_(folder.full_metadata_edit_form())
            self.assert_(folder.folder_localrole_form())
            self.assert_(folder.box_manage_form())

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

    def testLocalRoles(self):
        # Change local roles using the skin script
        sections = self.portal.sections

        sections.folder_localrole_edit(change_type='add', 
            member_ids=['user:root'], member_role='SectionReader')
        self.assertEquals(
            sections.__ac_local_roles__['root'], ['SectionReader'])

        sections.folder_localrole_edit(change_type='delete', 
            member_ids=['user:root'])
        self.assertEquals(sections.__ac_local_roles__.get('root'), None)

    def testCopyPaste(self):
        ws = self.portal.workspaces
        ws.invokeFactory('Workspace', 'ws1')
        ws.invokeFactory('Workspace', 'ws2')

        cookie = ws.manage_copyObjects(('ws1'))
        ws.ws2.manage_pasteObjects(cookie)
        self.assert_('ws1' in ws.ws2.objectIds())

        ws.manage_pasteObjects(cookie)
        self.assert_('copy_of_ws1' in ws.objectIds())

        cookie = ws.manage_cutObjects(('ws1'))
        ws.ws2.manage_pasteObjects(cookie)
        self.assert_('copy_of_ws1' in ws.ws2.objectIds())
        self.assert_('ws1' not in ws.objectIds())

        # Check that catalog has been synchronized
        catalog = self.portal.portal_catalog
        self.assert_(has_path(catalog, "/portal/workspaces/ws2"))
        self.assert_(has_path(catalog, "/portal/workspaces/ws2/ws1"))
        self.assert_(has_path(catalog, "/portal/workspaces/ws2/copy_of_ws1"))
        self.assert_(has_path(catalog, "/portal/workspaces/copy_of_ws1"))
        self.assert_(not has_path(catalog, "/portal/workspaces/ws1"))


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

