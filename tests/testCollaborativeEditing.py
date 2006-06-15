# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

import unittest

import traceback
from zExceptions.ExceptionFormatter import format_exception
traceback.format_exception = format_exception

from DateTime import DateTime

from webdav.LockItem import LockItem
from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.CPSDefault.tests.CPSTestCase import CPSTestCase

WORKSPACE_ID = "test-collaborative-workspace"

class TestCollaborativeEditionWorkflow(CPSTestCase):
    # Test object creation and collaborative edition workflow in the workspaces

    def afterSetUp(self):
        self.login('manager')

        self.wftool = getToolByName(self.portal, 'portal_workflow')
        # Creating an extra section to be used for publishing
        self.wftool.invokeFactoryFor(
            self.portal.workspaces, 'Workspace', WORKSPACE_ID)
        self.ws = self.portal.workspaces[WORKSPACE_ID]

        members = self.portal.portal_directories.members
        members.createEntry({'id': 'member1', 'roles': ['Member']})
        members.createEntry({'id': 'member2', 'roles': ['Member']})
        members.createEntry({'id': 'wsmanager', 'roles': ['Member']})

        pmtool = self.portal.portal_membership
        pmtool.setLocalRoles(obj=self.ws,
            member_ids=['member1', 'member2'], member_role='WorkspaceMember')
        pmtool.setLocalRoles(obj=self.ws,
            member_ids=['wsmanager'], member_role='WorkspaceManager')

    def beforeTearDown(self):
        self.logout()

    def testAccessForManager(self):
        self.login('manager')
        self.assert_(self.ws.folder_contents())
        self.assert_(self.ws.folder_view())
        self.assert_(self.portal.portal_repository.folder_view())

    def testAccessForMember(self):
        self.login('member1')
        self.assert_(self.ws.folder_contents())
        self.assert_(self.ws.folder_view())
        self.assertRaises(
            Unauthorized, self.portal.portal_repository.folder_view, ())

    def _checkPerm(self, perm, ob):
        return getToolByName(self.portal, 'portal_membership').checkPermission(
            perm, ob)

    def _testCollaborativeEdit(self, document_type):
        """Play with the standard workspace wf (with drafts)"""

        self.login('member1')

        # create two documents to simulate // editing
        self.ws.invokeFactory(document_type, 'doc-a')
        proxy_a = self.ws['doc-a']
        self.ws.invokeFactory(document_type, 'doc-b')
        proxy_b = self.ws['doc-b']

        review_state_a = self.wftool.getInfoFor(proxy_a, 'review_state')
        self.assertEquals(review_state_a, 'work')
        review_state_b = self.wftool.getInfoFor(proxy_b, 'review_state')
        self.assertEquals(review_state_b, 'work')

        # member1 edit doc-a them directly in the work state
        doc_def_a = {'Description': "New description for a"}
        doc_edit_a = proxy_a.getEditableContent()
        doc_edit_a.edit(doc_def_a, proxy=proxy_a)
        self.assertEquals(proxy_a.getContent().getDataModel()['Description'],
                          "New description for a")

        # similarly for doc-b and member2
        self.login('member2')
        doc_def_b = {'Description': "New description for b"}
        doc_edit_b = proxy_b.getEditableContent()
        doc_edit_b.edit(doc_def_b, proxy=proxy_b)
        self.assertEquals(proxy_b.getContent().getDataModel()['Description'],
                          "New description for b")

        # member2 creates a version on proxy_b (using the skin script)
        proxy_b.content_checkout_draft()
        draft_b = self.ws['doc-b_1']

        review_state = self.wftool.getInfoFor(proxy_a, 'review_state')
        self.assertEquals(review_state, 'work')
        review_state = self.wftool.getInfoFor(proxy_b, 'review_state')
        self.assertEquals(review_state, 'locked')
        review_state = self.wftool.getInfoFor(draft_b, 'review_state')
        self.assertEquals(review_state, 'draft')

        # member2 edit the draft
        doc_def_b = {'Description': "New New description for b"}
        doc_edit_b = draft_b.getEditableContent()
        doc_edit_b.edit(doc_def_b, proxy=draft_b)
        self.assertEquals(draft_b.getContent().getDataModel()['Description'],
                          "New New description for b")

        # member2 cannot edit the locked proxy
        self.failIf(self._checkPerm(ModifyPortalContent, proxy_b))

        # member1 cannot edit any of those
        self.login('member1')
        self.failIf(self._checkPerm(ModifyPortalContent, proxy_b))
        self.failIf(self._checkPerm(ModifyPortalContent, draft_b))

        # but member1 can still see them
        self.assert_(self._checkPerm(View, proxy_b))
        self.assert_(self._checkPerm(View, draft_b))

        # member1 creates a draft to work on proxy_a
        proxy_a.content_checkout_draft()
        draft_a = self.ws['doc-a_1']

        review_state = self.wftool.getInfoFor(proxy_a, 'review_state')
        self.assertEquals(review_state, 'locked')
        review_state = self.wftool.getInfoFor(draft_a, 'review_state')
        self.assertEquals(review_state, 'draft')

        # member1 edit his draft
        doc_def_a = {'Description': "New New description for a"}
        doc_edit_a = draft_a.getEditableContent()
        doc_edit_a.edit(doc_def_a, proxy=draft_a)
        self.assertEquals(draft_a.getContent().getDataModel()['Description'],
                          "New New description for a")

        # member1 cannot edit the locked proxy
        self.failIf(self._checkPerm(ModifyPortalContent, proxy_a))

        # member2 cannot edit member1's work
        self.login('member2')
        self.failIf(self._checkPerm(ModifyPortalContent, proxy_a))
        self.failIf(self._checkPerm(ModifyPortalContent, draft_a))

        # member2 can see them
        self.assert_(self._checkPerm(View, proxy_a))
        self.assert_(self._checkPerm(View, draft_a))

        # member2 checks that proxy_b is the target of the checkin
        locked_b = draft_b.getLockedObjectFromDraft()
        self.assertEquals(locked_b.absolute_url(), proxy_b.absolute_url())

        # member2 checks his draft back in
        draft_b.content_checkin_draft()

        self.assert_('doc-b_1' not in self.ws.objectIds())
        proxy_b = self.ws['doc-b']
        review_state = self.wftool.getInfoFor(proxy_b, 'review_state')
        self.assertEquals(review_state, 'work')

        # before checking the draft_a backing, let us articficially remove
        # member1 right to see proxy_b to check that getLocakFromDraft is robust
        # enough: this script indeed scans the content of the current folder
        # looking for the original proxy and should raise Unauthorized by
        # inspecting proxies that the user is not allowed to View
        self.login('wsmanager')
        proxy_b.folder_localrole_block(lr_block=True)

        self.login('member1')
        self.failIf(self._checkPerm(View, proxy_b))
        self.assert_(self._checkPerm(View, proxy_a))
        self.assert_(self._checkPerm(View, draft_a))

        # now member1 checks the draft_a back in
        locked_a = draft_a.getLockedObjectFromDraft()
        self.assertEquals(locked_a.absolute_url(), proxy_a.absolute_url())
        draft_a.content_checkin_draft()

        self.assert_('doc-a_1' not in self.ws.objectIds())
        proxy_a = self.ws['doc-a']
        review_state = self.wftool.getInfoFor(proxy_a, 'review_state')
        self.assertEquals(review_state, 'work')

        # cleanup
        self.login('wsmanager')
        self.ws.manage_delObjects([id for id in self.ws.objectIds()
                                      if not id.startswith('.')])

    def testCollaborativeEditWithAllDocumentTypes(self):
        document_types = [k for k, v in self.portal.getDocumentTypes().items()
                            if v['cps_proxy_type']=='document']
        for document_type in document_types:
            self._testCollaborativeEdit(document_type)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCollaborativeEditionWorkflow))
    return suite

