import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase

from AccessControl import Unauthorized
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

    def testAccessForMember(self):
        self.login('member')
        assert self.member_ws.folder_contents()
        assert self.member_ws.folder_view()
        self.assertRaises(
            Unauthorized, self.portal.portal_repository.folder_view, ())

    def testAccessForReviewer(self):
        self.login('reviewer')
        assert self.portal.sections.folder_contents()
        assert self.portal.sections.folder_view()
        self.assertRaises(
            Unauthorized, self.portal.portal_repository.folder_view, ())

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

        self.login('reviewer')

        published_proxy = self.portal.sections.news
        info = published_proxy.getContentInfo(level=3)
        self.assertEquals(info['review_state'], 'pending')

        # Now accept it
        published_proxy.content_status_modify(workflow_action='accept')
        info = published_proxy.getContentInfo(level=3)
        self.assertEquals(info['review_state'], 'published')

        self.login('member')

        # Non-reviewer can't unpublish his own stuff
        published_proxy = self.portal.sections.news
        self.assertRaises(WorkflowException,
            published_proxy.content_status_modify, workflow_action='unpublish')

        self.login('reviewer')

        info = published_proxy.getContentInfo(level=3)
        published_proxy = self.portal.sections.news
        published_proxy.content_status_modify(workflow_action='unpublish')
        
        self.login('root')

        assert not 'news' in self.portal.sections.objectIds()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPublication))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

