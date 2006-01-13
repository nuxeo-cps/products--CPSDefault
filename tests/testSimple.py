import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase

from Products.CMFCore.tests.base.utils import has_path
from Products.CMFCore.utils import getToolByName

class TestSimple(CPSDefaultTestCase.CPSDefaultTestCase):
    def afterSetUp(self):
        if self.login_id:
            self.login(self.login_id)
            self.portal.portal_membership.createMemberArea()

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

    # XXX: disabled for now because W3C CSS checker is bogus
    def _testCSS(self):
        ALL_CSS = ['default.css', 'default_print.css']
        for css_name in ALL_CSS:
            css_body = self.portal[css_name](self.portal)
            self.assert_(
                self.isValidCSS(css_body), "%s is not valid CSS" % css_name)


class TestSimpleAsRoot(TestSimple):
    login_id = 'manager'

    def testMembersSkins(self):
        self.assert_(self.portal.workspaces.folder_view())
        self.assert_(self.portal.sections.folder_view())

    def XXXtestAdminSkinsAtRoot(self):
        self.assert_(self.portal.config_form())
        # XXX: move this to CPSDirectory ?
        self.assert_(self.portal.cpsdirectory_view())
        for dirname in ('members', 'groups', 'roles'):
            self.portal.REQUEST['dirname'] = dirname
            self.assert_(self.portal.cpsdirectory_entry_search_form())
            self.assert_(self.portal.cpsdirectory_entry_create_form())
        # Boxes

    def testAdminSkinsAtSectionsAndWorkspaces(self):
        for folder in (self.portal.workspaces, self.portal.sections):
            self.assert_(folder.folder_view())
            self.assert_(folder.folder_factories())
            self.assert_(folder.folder_contents())
            self.assert_(folder.folder_edit_form())
            self.assert_(folder.metadata_edit_form())
            self.assert_(folder.full_metadata_edit_form())
            self.assert_(folder.folder_localrole_form())

    def testLocalRoles(self):
        # Change local roles using the skin scripts
        sections = self.portal.sections

        sections.folder_localrole_add(
            member_ids=['user:manager'], member_role='SectionReader')
        self.assertEquals(
            sections.__ac_local_roles__['manager'], ['SectionReader'])

        sections.folder_localrole_edit(edit_ids=['user:manager'],
                                       role_user_manager=['SectionReviewer'],
                                       edit_local_roles='ok')
        self.assertEquals(
            sections.__ac_local_roles__['manager'], ['SectionReviewer'])
        sections.folder_localrole_edit(delete_ids=['user:manager'])
        self.assertEquals(sections.__ac_local_roles__.get('manager'), None)


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

    def testToolsPresence(self):
        urltool = getToolByName(self.portal, 'portal_url')
        self.assertEquals(urltool.meta_type, 'CPS URL Tool')

class TestSimpleAsAnonymous(TestSimple):
    login_id = ''

    # FIXME: broken
    def _testMembersSkins(self):
        # Anonymous can't view sections and workspaces by default.
        try:
            # CMF >= 1.5
            from exceptions import AccessControl_Unauthorized as Unauthorized
        except:
            # CMF 1.4
            Unauthorized = 'Unauthorized'
        self.assertRaises(Unauthorized, self.portal.sections.view)
        self.assertRaises(Unauthorized, self.portal.workspaces.view)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSimpleAsRoot))
    suite.addTest(unittest.makeSuite(TestSimpleAsAnonymous))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

