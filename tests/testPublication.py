import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase

from Products.CMFCore.tests.base.utils import has_path


class TestPublication(CPSDefaultTestCase.CPSDefaultTestCase):
    def afterSetUp(self):
        self.login('root')

        members = self.portal.portal_directories.members
        members.createEntry({'id': 'user', 'roles': ['Member']})
        self.user_ws = self.portal.workspaces.members.user

        pmtool = self.portal.portal_membership
        pmtool.setLocalRoles(obj=self.portal.sections, 
            member_ids=['user'], member_role='SectionReader')

        # Some ZPTs need a session. 
        # XXX: this might be moved to a more generic place someday.
        self.portal.REQUEST.SESSION = {}

    def beforeTearDown(self):
        self.logout()

    def testSubmit(self):
        self.login('user')

        # Create some document
        self.user_ws.invokeFactory('News', 'news')
        proxy = self.user_ws.news
        doc = proxy.getContent()
        doc.edit()

        # Then submit it (using skin script)
        proxy.content_status_modify(
            submit='sections', workflow_action='copy_submit')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPublication))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

