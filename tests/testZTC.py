#
# Skeleton ZopeTestCase
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


class TestSSS3(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        pass
    
    def afterClear(self):
        pass

    def testInstallSS3(self):
        'Test SSS3 Instanciation'
        roles = ['Manager', ZopeTestCase._user_role]
        uf = self.folder.acl_users
        uf._changeUser(ZopeTestCase._user_name,
                       'password', 'pconfirm',
                       roles, ())

#        self.failUnless(0, self.folder.acl_users.getUserById(ZopeTestCase._user_name).getRoles())
        dispatcher = self.folder.manage_addProduct['SSS3']
        dispatcher.manage_addSss3Site('cps', title='The SSS3 Site',
                                      root_id='root',
                                      root_sn='Root',
                                      root_givenName='Nanard',
                                      root_email='ben@nuxeo.com',
                                      root_password1='a',
                                      root_password2='a')
        self.cps = self.folder['cps']
        self.assertEqual(1,0, self.cps.sections)

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestSSS3))
        return suite

