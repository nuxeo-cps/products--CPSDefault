#
# CPS ZopeTestCase
#
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

os.environ['STUPID_LOG_SEVERITY'] = '-200'
os.environ['ZOPE_SECURITY_POLICY'] = 'PYTHON'

from Testing import ZopeTestCase

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from AccessControl.User import UserFolder, manage_addUserFolder
from OFS.Folder import Folder, manage_addFolder
from AccessControl.Permissions import access_contents_information, view

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


# create a CPS from scratch
app = ZopeTestCase.app()
app.manage_addFolder(_folder_name)
folder = app._getOb(_folder_name)
folder._addRole(_user_role)
folder.manage_addUserFolder()
uf = folder.acl_users
uf._addUser(_user_name, 'secret', 'secret', (_user_role,), ())
_user = uf.getUserById(_user_name).__of__(uf)
folder.manage_role(_user_role, _standard_permissions)
newSecurityManager(None, _user)
uf._changeUser(ZopeTestCase._user_name,
               'secret', 'secret',
               ('Manager', _user_role), ())
dispatcher = folder.manage_addProduct['SSS3']
dispatcher.manage_addSss3Site('cps', title='The test case Site')
cps = folder['cps']



class TestSSS3(ZopeTestCase.ZopeTestCase):
    
    def setUp(self):
        self.cps = cps
        get_transaction().begin()
            
    def tearDown(self):
        get_transaction().abort()

    def test_01_sections_folder(self):
        self.assertEqual(self.cps['sections'].getPortalTypeName(), 'Section')

    def test_02_workspaces_folder(self):
        self.assertEqual(self.cps['workspaces'].getPortalTypeName(), 'Workspace')
        

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestSSS3))
        return suite

