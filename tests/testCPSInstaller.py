#
# unit test for cpsinstall script
#
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

os.environ['STUPID_LOG_SEVERITY'] = '-200'
os.environ['ZOPE_SECURITY_POLICY'] = 'PYTHON'

from Testing import ZopeTestCase

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


class TestCPSInstaller(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        pass
    
    def afterClear(self):
        pass

    def testInstallSSS3(self):
        'Test SSS3 Install'
        roles = ['Manager', ZopeTestCase._user_role]
        uf = self.folder.acl_users
        uf._changeUser(ZopeTestCase._user_name,
                       'password', 'pconfirm',
                       roles, ())

        dispatcher = self.folder.manage_addProduct['SSS3']
        dispatcher.manage_addSss3Site('cps', title='The test case Site')
        self.cps = self.folder['cps']

        # checking for root folders
        self.assertEqual(self.cps['sections'].getPortalTypeName(), 'Section')
        self.assertEqual(self.cps['workspaces'].getPortalTypeName(), 'Workspace')
        

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCPSInstaller))
        return suite

