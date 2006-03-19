# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Stefane Fermigier <sf@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest

from Products.CMFCore.tests.base.utils import has_path
from Products.CMFCore.utils import getToolByName
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase

class TestSimple(CPSTestCase):

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
        self.assertValidXHTML(self.portal.index_html(), "index_html")
        self.assertValidXHTML(self.portal.login_form(), "login_form")
        self.assertValidXHTML(self.portal.join_form(), "join_form")
        self.assertValidXHTML(self.portal.accessibility(), "accessibility")

        self.assertValidXHTML(self.portal.search_form(), "search_form")

        self.assertValidXHTML(self.portal.advanced_search_form(), "advanced_search_form")
        self.assert_(self.portal.advanced_search_form())

        # TODO: add more ?

    def testCss(self):
        ALL_CSS = ['default.css', 'default_print.css', 'msie.css',
                   'atom.css', 'rss.css']
        for css_name in ALL_CSS:
            css_body = self.portal[css_name](self.portal)
            self.assert_(
                self.isValidCss(css_body), "%s is not valid CSS" % css_name)


class TestSimpleAsRoot(TestSimple):
    login_id = 'manager'

    def testAdminSkinsAtRoot(self):
        self.assertValidXHTML(self.portal.config_form(), "config_form")
        return
        # XXX: move this to CPSDirectory ?
        self.assert_(self.portal.cpsdirectory_view())
        for dirname in ('members', 'groups', 'roles'):
            self.portal.REQUEST['dirname'] = dirname
            self.assert_(self.portal.cpsdirectory_entry_search_form())
            self.assert_(self.portal.cpsdirectory_entry_create_form())
        # Boxes

    def testAdminSkinsAtSectionsAndWorkspaces(self):
        # FIXME: 'folder_edit_form', 'metadata_edit_form',
        # 'full_metadata_edit_form'
        # have validity problems
        view_ids = ('folder_view', 'folder_factories', 'folder_contents',
                    'cpsdocument_metadata_template', 'cpsdocument_edit_form',
                    'folder_localrole_form')
        for folder_id in ('sections', 'workspaces', 'members'):
            folder = getattr(self.portal, folder_id)
            for view_id in view_ids:
                method = getattr(folder, view_id)
                self.assertValidXHTML(method(), "%s/%s" % (folder_id, view_id))

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

