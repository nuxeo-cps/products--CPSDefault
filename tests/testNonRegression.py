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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNonRegression))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
