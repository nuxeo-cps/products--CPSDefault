import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
import CPSDefaultTestCase


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
        # WARNING content_create is not used for a CPSDocument
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
        assert self.portal.portal_types.News.manage_propertiesForm(URL1="")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNonRegression))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

