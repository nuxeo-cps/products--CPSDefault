# CPS Unit Test
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
ZopeTestCase.installProduct('NuxCPS3')

ZopeTestCase.installProduct('SSS3')


_folder_name          = 'testFolder_1_'
_user_name            = 'testUser_1_'
_user_role            = 'testRole_1_'
_standard_permissions = [access_contents_information, view]
 

# create a CPS Site fixture
# XXX TODO this fixture should be run when running tests
# not while loading the test suite 
_print('Initialize Zope Server ... ')
_start = time.time()
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
_print('done (%.3fs)\n' % (time.time() - _start))

_print('Creating a CPS Site ... ')
_start = time.time()
_dispatcher = _folder.manage_addProduct['SSS3']
_dispatcher.manage_addSss3Site('cps', title='The test case Site')
_portal = _folder['cps']
_print('done (%.3fs)\n' % (time.time() - _start))


class TestSSS3(unittest.TestCase):
    
    def setUp(self):
        self.portal = _portal
        self.wftool =  getToolByName(_portal, 'portal_workflow')
        get_transaction().begin()
            
    def tearDown(self):
        get_transaction().abort()

    def test_01_workflow(self):
        self.assertNotEqual(self.wftool, None)
        
    def test_10_sections_folder(self):
        ob = self.portal['sections']
        self.assertEqual(ob.getPortalTypeName(), 'Section')

    def test_11_sections_folder(self):
        ob = self.portal['sections']
        wfid = self.wftool.getChainFor(ob)
        self.assertEqual(wfid[0], 'wf_section')

    def test_12_sections_folder(self):
        ob = self.portal['sections']
        wf = self.wftool.getWorkflowById(self.wftool.getChainFor(ob)[0])
        self.assertEqual(wf._getWorkflowStateOf(ob, id_only=1), 'work')

    def test_20_workspaces_folder(self):
        ob = self.portal['workspaces']
        self.assertEqual(ob.getPortalTypeName(), 'Workspace')

    def test_21_workspaces_folder(self):
        ob = self.portal['workspaces']
        wfid = self.wftool.getChainFor(ob)
        self.assertEqual(wfid[0], 'wf_workspace')

    def test_22_workspaces_folder(self):
        ob = self.portal['workspaces']
        wf = self.wftool.getWorkflowById(self.wftool.getChainFor(ob)[0])
        self.assertEqual(wf._getWorkflowStateOf(ob, id_only=1), 'work')
        

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestSSS3))
        return suite

