# CPS Unit Test
#
# this suite is much more a functional suite than unit test suite
# 
import os, sys, time
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

os.environ['STUPID_LOG_SEVERITY'] = '-200'
os.environ['ZOPE_SECURITY_POLICY'] = 'PYTHON'

import unittest
from Testing import ZopeTestCase
from Testing.ZopeTestCase.ZopeLite import _print

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from AccessControl.User import UserFolder, manage_addUserFolder
from OFS.Folder import Folder, manage_addFolder
from AccessControl.Permissions import access_contents_information, view
from Products.CMFCore.utils import getToolByName


ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('DCWorkflow')
ZopeTestCase.installProduct('BTreeFolder2')
ZopeTestCase.installProduct('NuxUserGroups')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('OrderedFolderSupportPatch')
ZopeTestCase.installProduct('TranslationService')
ZopeTestCase.installProduct('MailHost')
ZopeTestCase.installProduct('VerboseSecurity')
ZopeTestCase.installProduct('CPSCore')

ZopeTestCase.installProduct('CPSDefault')



init_suite_flag = 0

_folder_name          = 'testFolder_1_'
_user_name            = 'testUser_1_'
_user_role            = 'Member'
_standard_permissions = [access_contents_information, view]

_user_name1           = 'testCPSUser1'
_user_name2           = 'testCPSUser2'
_sections             = 'sections'
_workspaces           = 'workspaces'
_doc_name             = 'testCPSDoc'


def init_suite():
    global init_suite_flag, _portal, _app
    if init_suite_flag:
        return
    init_suite_flag = 1

    # create a CPS Site fixture
    _app = ZopeTestCase.app()
    _app.manage_addFolder(_folder_name)
    _folder = _app._getOb(_folder_name)
    _folder._addRole(_user_role)
    _folder.manage_addUserFolder()
    _uf = _folder.acl_users
    _uf._addUser(_user_name, 'secret', 'secret', (_user_role,), ())
    _user = _uf.getUserById(_user_name).__of__(_uf)
    _folder.manage_role(_user_role, _standard_permissions)
    newSecurityManager(None, _user)
    _uf._changeUser(ZopeTestCase._user_name,
               'secret', 'secret',
               ('Manager', _user_role), ())

    _dispatcher = _folder.manage_addProduct['CPSDefault']
    _dispatcher.manage_addCPSDefaultSite('cps', title='The test case Site')
    _portal = _folder['cps']

    # create cps test users
    for u in (_user_name1, _user_name2):
        _portal.acl_users._addUser(name=u, password=u, confirm=u,
                                   roles=('Member', ), domains=None)
    _portal[_sections].manage_setLocalRoles(_user_name1, ('SectionReader',))
    _portal[_sections].manage_setLocalRoles(_user_name2, ('SectionReviewer',))
    _portal[_workspaces].manage_setLocalRoles(_user_name1, ('WorkspaceMember',))
    _portal[_workspaces].manage_setLocalRoles(_user_name2, ('WorkspaceMember',))


class TestCPSDefault(unittest.TestCase):
    
    def setUp(self):
        if init_suite_flag:
            self.portal = _portal
            self.wftool =  getToolByName(_portal, 'portal_workflow')
            self.work = self.portal[_workspaces]
            self.pub = self.portal[_sections]
            get_transaction().begin()
            
    def tearDown(self):
        if init_suite_flag:
            get_transaction().abort()

    def test_00_init_suite(self):
        # create a CPS used for other unit tests
        init_suite()
        self.assertNotEqual(_portal, None)        
       
    def test_01_workflow(self):
        self.assertNotEqual(self.wftool, None)

    def test_02_users(self):
        self.assertEqual(str(self.portal.acl_users.getUserById(_user_name1)), _user_name1)
        
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

