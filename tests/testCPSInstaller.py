#
# unit test for cpsinstall script
#
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

os.environ['STUPID_LOG_SEVERITY'] = '-200'
os.environ['ZOPE_SECURITY_POLICY'] = 'PYTHON'

from Testing import ZopeTestCase
import CPSDefaultTestCase

class TestCPSInstaller(CPSDefaultTestCase.CPSDefaultTestCase):

    def testInstallCPSDefault(self):
        roles = ['Manager', ZopeTestCase._user_role]
        uf = self.folder.acl_users
        uf._changeUser(ZopeTestCase._user_name,
                       'password', 'pconfirm',
                       roles, ())

        dispatcher = self.folder.manage_addProduct['CPSDefault']
        dispatcher.manage_addCPSDefaultSite('cps', 
            title='The test case Site', 
            root_password1='root', root_password2='root')
        self.cps = self.folder['cps']

        # checking for root folders
        self.assertEqual(self.cps['sections'].getPortalTypeName(), 'Section')
        self.assertEqual(self.cps['workspaces'].getPortalTypeName(), 
                         'Workspace')
        

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCPSInstaller))
        return suite

