# (C) Copyright 2006-2007 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Stefane Fermigier <sf@nuxeo.com>
# M.-A. Darche
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
from AccessControl.SecurityManagement import newSecurityManager
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase

class TestNonRegression(CPSTestCase):
    def afterSetUp(self):
        self.login('manager')

    def beforeTearDown(self):
        self.logout()

    def testIdCollision(self):
        workspaces = self.portal.workspaces
        sections = self.portal.sections

        # Test that object with reserved names such as 'content' and 'icon' can
        # be created nevertheless but their id will not be a reserved id.

        # TODO: somewhat Obsoleted in CMF 1.5, it seems
        new_id = workspaces.content_create('Workspace', title='content')
        #self.assertNotEquals(new_id, 'content')
        self.assert_(new_id.startswith('content'))

        new_id = workspaces.content_create('Workspace', title='icon')
        #self.assertNotEquals(new_id, 'icon')
        self.assert_(new_id.startswith('icon'))
        # TODO: need to check if the portal is functional "live"

        # Test that we can create an object with id 'index_html', 'sections'
        # or 'workspaces'.
        # But note that a subobject with same id as its container is not
        # possible in other case. This is a case where acquisition is a pain.
        # WARNING content_create is not used for a CPSDocument
        new_id = sections.content_create('Section', title='sections')
        self.assertEquals(new_id, 'sections')

        # But if we do it twice, we get another id
        new_id = sections.content_create('Section', title='sections')
        self.assertNotEquals(new_id, 'sections')
        self.assert_(new_id.startswith('sections'))

        # Same for workspaces (just for fun)
        new_id = workspaces.content_create('Workspace', title='workspaces')
        self.assertEquals(new_id, 'workspaces')
        new_id = workspaces.content_create('Workspace', title='workspaces')
        self.assertNotEquals(new_id, 'workspaces')
        self.assert_(new_id.startswith('workspaces'))

    def testDuplicatePortlets(self):
        portlets = getattr(self.portal, '.cps_portlets')
        count = 0
        for portlet in portlets.objectValues():
            if portlet.portal_type == 'Text Portlet' and \
              portlet.text == 'welcome_body':
                count += 1
        self.assertEquals(count, 1)

    # XXX disabled because it fails to setup some types correctly.
    def XXXtestUpdater(self):
        # Test that installer can be also called as updater
        self.assert_(self.portal.cpsupdate())

    # FIXME: this test must pass someday !!!
    def _testExportImport(self):
        # Log in as Zope root manager
        root = self.portal.aq_parent
        uf = root.acl_users
        user = uf.getUser('CPSTestCase').__of__(uf)
        newSecurityManager(None, user)

        # Export portal to temp file
        import tempfile
        zexp = root.manage_exportObject('portal', download=1)
        temp_file_name = tempfile.mktemp() + '.zexp'
        fd = open(temp_file_name, 'w')
        fd.write(zexp)
        fd.close()

        # Delete and try to reimport portal
        root.manage_delObjects(['portal'])
        root._importObjectFromFile(temp_file_name)

    def testPortalTypesZMI(self):
        # Broke between Zope 2.6.1 and 2.6.3
        self.assert_(
            self.portal.portal_types['News Item'].manage_propertiesForm(URL1=""))

    def testZopeExport(self):
        # These tests should catch an error that occur during XML export of
        # a CPS instance. Unfortunately, the problem lies in TranslationService, which
        # isn't really instanciated during unit tests. They could catch other
        # problems in the future, though.
        zexp = self.portal.manage_exportObject(id='', download=1, toxml=0)
        self.assert_(zexp)

        # XXX This is currently broken in Zope !
        # (http://collector.zope.org/Zope/1219)
        #xml = self.portal.manage_exportObject(id='', download=1, toxml=1)
        #assert xml

    def testRootFirstLogin(self):
        self.login("manager")
        self.portal.logged_in()

    def testRoot2FirstLogin(self):
        self.login("manager")
        members_directory = self.portal.portal_directories.members
        members_directory.createEntry(
            {'id': 'manager2', 'roles': ('Member', 'Manager')})
        self.logout()
        self.login('manager2')
        self.portal.logged_in()

    def testMemberLogin(self):
        self.login("manager")
        members_directory = self.portal.portal_directories.members
        members_directory.createEntry(
            {'id': 'joeuser', 'roles': ('Member',)})
        self.logout()
        # Testing that the user can log in multiple times to test the setting
        # of login_time and last_login_time.
        self.login('joeuser')
        self.portal.logged_in()
        self.logout()
        self.login('joeuser')
        self.portal.logged_in()
        self.logout()


    def testMagicDates(self):
        # To ensure that finer granularity in write process
        # doesn't break CreationDate et al
        self.login("manager")
        ws = self.portal.workspaces
        self.portal.portal_workflow.invokeFactoryFor(ws,
                                                     'File', 'afile',
                                                     Title="CreationDate test")
        proxy = ws.afile
        doc=proxy.getContent()
        # don't need to test the actual time
        self.failIf(doc.created() is None)

        from DateTime import DateTime
        old = DateTime('2007/01/29')
        doc.modification_date = old
        doc.edit(Title="ModifDate", proxy=proxy) # new title to catch in pdb
        self.failIfEqual(doc.modified(), old)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNonRegression))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
