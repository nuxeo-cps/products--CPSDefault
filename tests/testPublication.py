import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase

from Products.CMFCore.WorkflowCore import WorkflowException


class TestPublication(CPSDefaultTestCase.CPSDefaultTestCase):
    def afterSetUp(self):
        self.login('root')

        members = self.portal.portal_directories.members
        members.createEntry({'id': 'member', 'roles': ['Member']})
        members.createEntry({'id': 'reviewer', 'roles': ['Member']})
        self.member_ws = self.portal.workspaces.members.member

        pmtool = self.portal.portal_membership
        pmtool.setLocalRoles(obj=self.portal.sections, 
            member_ids=['member'], member_role='SectionReader')
        pmtool.setLocalRoles(obj=self.portal.sections, 
            member_ids=['reviewer'], member_role='SectionReviewer')

        # Some ZPTs need a session. 
        # XXX: this might be moved to a more generic place someday.
        self.portal.REQUEST.SESSION = {}

    def beforeTearDown(self):
        self.logout()

    def testSubmit(self):
        self.login('member')

        # Create some document
        self.member_ws.invokeFactory('News', 'news')
        proxy = self.member_ws.news
        doc = proxy.getContent()
        doc.edit()

        info = proxy.getContentInfo(level=3)
        self.assertEquals(info['review_state'], 'work')

        # Then submit it (using skin script)
        proxy.content_status_modify(
            submit='sections', workflow_action='copy_submit')
        info = proxy.getContentInfo(level=3)
        self.assertEquals(info['review_state'], 'work')

        self.logout()
        self.login('reviewer')

        published_proxy = self.portal.sections.news
        info = published_proxy.getContentInfo(level=3)
        self.assertEquals(info['review_state'], 'pending')

        # Now accept it
        published_proxy.content_status_modify(workflow_action='accept')
        info = published_proxy.getContentInfo(level=3)
        self.assertEquals(info['review_state'], 'published')

        self.logout()
        self.login('member')

        # Non-reviewer can't unpublish his own stuff
        published_proxy = self.portal.sections.news
        self.assertRaises(WorkflowException,
            published_proxy.content_status_modify, workflow_action='unpublish')

        self.logout()
        self.login('reviewer')

        published_proxy = self.portal.sections.news
        published_proxy.content_status_modify(workflow_action='unpublish')
        info = published_proxy.getContentInfo(level=3)
        #self.assertEquals(info['review_state'], 'pending')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPublication))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

