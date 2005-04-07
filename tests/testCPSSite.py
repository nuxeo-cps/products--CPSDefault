# CPS Unit Test
#
# this suite is much more a functional suite than unit test suite
# 
import os, sys, time
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase

from AccessControl.Permissions import access_contents_information, view
from Products.CMFCore.utils import getToolByName

_folder_name          = 'testFolder_1_'
_user_name            = 'testUser_1_'
_user_role            = 'Member'
_standard_permissions = [access_contents_information, view]

_user_name1           = 'testCPSUser1'
_user_name2           = 'testCPSUser2'
_sections             = 'sections'
_workspaces           = 'workspaces'
_doc_name             = 'testCPSDoc'

class TestCPSDefault(CPSDefaultTestCase.CPSDefaultTestCase):
    
    def afterSetUp(self):
        self.wftool = getToolByName(self.portal, 'portal_workflow')
        self.work = self.portal[_workspaces]
        self.pub = self.portal[_sections]
        self.login("manager")

        # create cps test users
        for u in (_user_name1, _user_name2):
            self.portal.acl_users._addUser(name=u, password=u, confirm=u,
                roles=('Member',), domains=None)

        self.portal[_sections].manage_setLocalRoles(_user_name1, 
            ('SectionReader',))
        self.portal[_sections].manage_setLocalRoles(_user_name2, 
            ('SectionReviewer',))
        self.portal[_workspaces].manage_setLocalRoles(_user_name1, 
            ('WorkspaceMember',))
        self.portal[_workspaces].manage_setLocalRoles(_user_name2, 
            ('WorkspaceMember',))


    def beforeTearDown(self):
        self.logout()
            
    def test_01_workflow(self):
        self.assertNotEqual(self.wftool, None)

    def test_02_users(self):
        self.assertEqual(
            str(self.portal.acl_users.getUserById(_user_name1)), 
            _user_name1)
        
    def test_10_sections_folder(self):
        ob = self.pub
        self.assertEqual(ob.getPortalTypeName(), 'Section')

    def test_11_sections_folder(self):
        ob = self.pub
        wfid = self.wftool.getChainFor(ob)
        self.assertEqual(wfid[0], 'section_folder_wf')

    def test_12_sections_folder(self):
        ob = self.pub
        wf = self.wftool.getWorkflowById(self.wftool.getChainFor(ob)[0])
        self.assertEqual(wf._getWorkflowStateOf(ob, id_only=1), 'work')

    def test_20_workspaces_folder(self):
        ob = self.work
        self.assertEqual(ob.getPortalTypeName(), 'Workspace')

    def test_21_workspaces_folder(self):
        ob = self.work
        wfid = self.wftool.getChainFor(ob)
        self.assertEqual(wfid[0], 'workspace_folder_wf')

    def test_22_workspaces_folder(self):
        ob = self.work
        wf = self.wftool.getWorkflowById(self.wftool.getChainFor(ob)[0])
        self.assertEqual(wf._getWorkflowStateOf(ob, id_only=1), 'work')
        
        #roles = list(get_local_roles_for_userid(_user))

    def testPortalTrees(self):
        # Test that portal_trees has the right default values
        ttool = self.portal.portal_trees
        self.assertEquals(ttool.objectIds(), ['sections', 'workspaces'])
        for tree_id in ('sections', 'workspaces'):
            tree = ttool[tree_id]
            # FIXME why do I need to rebuild here with portlets ?
            tree.rebuild()
            l = tree.getList(filter=0)
            self.assert_(len(l) > 0)
        
    def tofix_test_30_create_doc(self):
        self.wftool.invokeFactoryFor(self.work.this(), 
                                     'Dummy', _doc_name)
        ob = self.work[_doc_name]
        self.assertEqual(ob.getPortalTypeName(), 'Dummy')


if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCPSDefault))
        return suite

