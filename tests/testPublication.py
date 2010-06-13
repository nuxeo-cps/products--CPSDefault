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

from Products.CPSDefault.tests.CPSTestCase import CPSPermWorkflowTestCase
from Products.CPSDocument.tests.testDefaultDocuments import DOCUMENT_TYPES

ANOTHER_SECTION_ID = 'another-section'

class TestPublication(CPSPermWorkflowTestCase):
    # Test object creation and publication workflow

    def afterSetUp(self):
        # avoid pollution from earlier tests
        self.portal.acl_users._clearUserCache()

        CPSPermWorkflowTestCase.afterSetUp(self)
        self.login('manager')

        # Creating an extra section to be used for publishing
        self.wftool.invokeFactoryFor(
            self.portal.sections, 'Section', ANOTHER_SECTION_ID)

        members = self.portal.portal_directories.members
        members.createEntry({'id': 'member', 'roles': ['Member']})
        members.createEntry({'id': 'reviewer', 'roles': ['Member']})

        self.portal_membership = self.portal.portal_membership
        self.portal.portal_membership.createMemberArea('member')
        self.member_ws = self.portal.members.member

        pmtool = self.portal.portal_membership
        pmtool.setLocalRoles(obj=self.portal.sections,
            member_ids=['member'], member_role='SectionReader')
        pmtool.setLocalRoles(obj=self.portal.sections,
            member_ids=['reviewer'], member_role='SectionReviewer')

    def beforeTearDown(self):
        self.logout()

    def testAccessForManager(self):
        self.login('manager')
        self.assert_(self.member_ws.folder_contents())
        self.assert_(self.member_ws.folder_view())
        self.assert_(self.portal.portal_repository.folder_view())

    def testAccessForMember(self):
        self.login('member')
        self.assert_(self.member_ws.folder_contents())
        self.assert_(self.member_ws.folder_view())
        self.assertRaises(
            Unauthorized, self.portal.portal_repository.folder_view, ())

    def testAccessForReviewer(self):
        self.login('reviewer')
        self.assertPerm(View, self.portal.sections)
        # GR: just introduced assertPerm, but keeping these below since
        # testing the method themselves is more than testing the permission
        self.assert_(self.portal.sections.folder_contents())
        self.assert_(self.portal.sections.folder_view())
        self.assertRaises(
            Unauthorized, self.portal.portal_repository.folder_view, ())

    def _checkGetContentInfo(self, info, level):
        self.assertEquals(info['icon'], 'newsitem_icon.png')
        self.assertEquals(info['id'], 'news')
        self.assertEquals(info['lang'], 'en')
        self.assertEquals(info['level'], level)
        self.assertEquals(info['rev'], '1')
        self.assertEquals(info['review_state'], 'work')
        self.assertEquals(info['rpath'], 'members/member/news')
        self.assert_(isinstance(info['time'], DateTime))
        self.assertEquals(info['title'], '')
        self.assertEquals(info['title_or_id'], 'news')
        self.assertEquals(info['type'], 'News Item')
        # XXX: what do we want here during the tests ?
        #self.assertNotEquals(info['time_str'], 'date_medium') # i18ned
        #self.assertNotEquals(info['type_l10n'], 'portal_type_NewsItem_title')

        if level >= 1:
            mtool = self.portal.portal_membership
            self.assertEquals(info['contributor'],
                              mtool.getFullnameFromId('member'))
            self.assertEquals(info['coverage'], '')
            self.assertEquals(info['creator'], 'member')
            self.assertEquals(info['description'], '')
            self.assertEquals(info['hidden'], 0)
            self.assertEquals(info['icon'], 'newsitem_icon.png')
            self.assertEquals(info['rights'], '')
            self.assertEquals(info['size'], '1 K')
            self.assertEquals(info['source'], '')
        if level >= 2:
            self.assertEquals(len(info['states']), 1)
            state = info['states'][0]
            self.assertEquals(state['lang'], 'en')
            self.assertEquals(state['language'], 'en')
            self.assertEquals(state['rev'], '1')
            self.assertEquals(state['review_state'], 'work')
            self.assertEquals(state['rpath'], 'members/member')
            self.assert_(isinstance(state['time'], DateTime))
            # XXX: what do we want here during the tests ?
            #self.assertNotEquals(state['time_str'], 'date_medium') # i18ned
            self.assertEquals(state['title'], 'member')
        if level >= 3:
            self.assertEquals(len(info['history']), 1)
            history = info['history'][0]
            self.assertEquals(history['action'], 'create')
            self.assertEquals(history['actor'], 'member')
            self.assertEquals(history['dest_container'], '')
            self.assertEquals(history['review_state'], 'work')
            self.assertEquals(history['rpath'], 'members/member/news')
            self.assert_(isinstance(history['time'], DateTime))
            # XXX: what do we want here during the tests ?
            #self.assertNotEquals(history['time_str'], 'date_medium') # i18ned
            self.assertEquals(history['workflow_id'], 'workspace_content_wf')
        if level >= 4:
            self.assertEquals(info['archived'], [])

    def testGetContentInfo(self):
        # Test the getContentInfo script

        self.login('member')
        self.member_ws.invokeFactory('News Item', 'news')
        proxy = self.member_ws.news
        self.portal.portal_trees.flushEvents()

        for level in range(0, 5):
            info = proxy.getContentInfo(level=level)
            self._checkGetContentInfo(info, level)

    def _testSubmit(self, document_type):
        self.login('member')

        # Create some documents with the second document having lock on it. This
        # kind of lock is used for example for WebDAV.
        self.member_ws.invokeFactory(document_type, 'doc')
        proxy = self.member_ws.doc
        self.member_ws.invokeFactory(document_type, 'doc2')
        proxy2 = self.member_ws.doc2
        member = self.portal_membership.getAuthenticatedMember()
        user = member.getUser()
        lock = LockItem(user)
        lock_token = lock.getLockToken()
        proxy2.wl_setLock(lock_token, lock)

        self.assertReviewState(proxy, 'work')
        review_state2 = self.wftool.getInfoFor(proxy2, 'review_state', None)
        self.assertEquals(review_state2, 'work')

        # Then submit it (using skin script)
        proxy.content_status_modify(
            submit=['sections', 'sections/' + ANOTHER_SECTION_ID],
            workflow_action='copy_submit')
        proxy2.content_status_modify(
            submit=['sections', 'sections/' + ANOTHER_SECTION_ID],
            workflow_action='copy_submit')

        review_state = self.wftool.getInfoFor(proxy, 'review_state', None)
        self.assertEquals(review_state, 'work')
        review_state2 = self.wftool.getInfoFor(proxy2, 'review_state', None)
        self.assertEquals(review_state2, 'work')

        self.login('reviewer')

        published_proxy = self.portal.sections.doc
        review_state = self.wftool.getInfoFor(published_proxy,
                                              'review_state', None)
        self.assertEquals(review_state, 'pending')
        published_proxy2 = self.portal.sections.doc2
        review_state2 = self.wftool.getInfoFor(published_proxy2,
                                               'review_state', None)
        self.assertEquals(review_state2, 'pending')

        self.assertEquals(published_proxy2.wl_isLocked(), False,
                          "A locked document in the workspaces should not "
                          "produce a locked document in the sections.")

        # Now accept it
        published_proxy.content_status_modify(workflow_action='accept')
        review_state = self.wftool.getInfoFor(published_proxy,
                                              'review_state', None)
        self.assertEquals(review_state, 'published')

        self.login('member')

        # Non-reviewer can't unpublish his own stuff
        self.assertRaises(WorkflowException,
            published_proxy.content_status_modify, workflow_action='unpublish')

        self.login('reviewer')

        published_proxy.content_status_modify(workflow_action='unpublish')

        self.login('manager')

        self.assert_(not 'doc' in self.portal.sections.objectIds())

        # Cleanup
        self.member_ws.manage_delObjects(['doc'])
        # Remove the lock before deleting otherwise the lock would prevent the
        # deletion.
        proxy2.wl_delLock(lock_token)
        self.member_ws.manage_delObjects(['doc2'])

    def _testSubmitWithModifiedWorkflow(self, document_type):
        self.login('member')

        # Create some document
        self.member_ws.invokeFactory(document_type, 'doc')
        proxy = self.member_ws.doc

        review_state = self.wftool.getInfoFor(proxy, 'review_state', None)
        self.assertEquals(review_state, 'work')

        # Then submit it (using skin script)
        proxy.content_status_modify(
            submit=['sections', 'sections/' + ANOTHER_SECTION_ID],
            workflow_action='copy_submit')

        review_state = self.wftool.getInfoFor(proxy, 'review_state', None)
        self.assertEquals(review_state, 'submitted')

        self.login('reviewer')

        published_proxy = self.portal.sections.doc
        review_state = self.wftool.getInfoFor(published_proxy,
                                              'review_state', None)
        self.assertEquals(review_state, 'pending')

        # Now accept it
        published_proxy.content_status_modify(workflow_action='accept')
        review_state = self.wftool.getInfoFor(published_proxy,
                                              'review_state', None)
        self.assertEquals(review_state, 'published')

        self.login('member')

        # Non-reviewer can't unpublish his own stuff
        self.assertRaises(WorkflowException,
            published_proxy.content_status_modify, workflow_action='unpublish')

        self.login('reviewer')

        published_proxy.content_status_modify(workflow_action='unpublish')

        self.login('manager')

        self.assert_(not 'doc' in self.portal.sections.objectIds())

        # Cleanup
        self.member_ws.manage_delObjects(['doc'])

    def _testSubmitFolderish(self, document_type, subdocument_type):
        self.login('member')

        # Create some documents with the second document having lock on it. This
        # kind of lock is used for example for WebDAV.
        self.member_ws.invokeFactory(document_type, 'doc')
        proxy = self.member_ws.doc
        proxy.invokeFactory(subdocument_type, 'doc2')
        proxy2 = proxy.doc2
        member = self.portal_membership.getAuthenticatedMember()

        review_state = self.wftool.getInfoFor(proxy, 'review_state', None)
        self.assertEquals(review_state, 'work')
        review_state2 = self.wftool.getInfoFor(proxy2, 'review_state', None)
        self.assertEquals(review_state2, 'work')

        # Then submit it (using skin script)
        proxy.content_status_modify(
            submit=['sections', 'sections/' + ANOTHER_SECTION_ID],
            workflow_action='copy_submit')

        review_state = self.wftool.getInfoFor(proxy, 'review_state', None)
        self.assertEquals(review_state, 'work')
        review_state2 = self.wftool.getInfoFor(proxy2, 'review_state', None)
        self.assertEquals(review_state2, 'work')

        self.login('reviewer')

        published_proxy = self.portal.sections.doc
        review_state = self.wftool.getInfoFor(published_proxy,
                                              'review_state', None)
        self.assertEquals(review_state, 'pending')
        published_proxy2 = published_proxy.doc2
        review_state2 = self.wftool.getInfoFor(published_proxy2,
                                               'review_state', None)
        self.assertEquals(review_state2, 'pending')

        # Now accept it
        published_proxy.content_status_modify(workflow_action='accept')
        review_state = self.wftool.getInfoFor(published_proxy,
                                              'review_state', None)
        self.assertEquals(review_state, 'published')
        review_state = self.wftool.getInfoFor(published_proxy2,
                                              'review_state', None)
        self.assertEquals(review_state, 'published')

        self.login('member')

        # Non-reviewer can't unpublish his own stuff
        self.assertRaises(WorkflowException,
            published_proxy.content_status_modify, workflow_action='unpublish')

        # Member modifies the subdoc and resubmits
        proxy2.getEditableContent().edit(Title='New title')
        proxy.content_status_modify(
            submit=['sections', 'sections/' + ANOTHER_SECTION_ID],
            workflow_action='copy_submit')

        # Reviewer checks the resubmission
        # GR: resubmission in the case where the folderish itself is untouched
        # may change in the future.
        self.login('reviewer')
        sections = self.portal.sections
        ids = sections.objectIds([proxy.meta_type])
        self.assertEquals(len(ids), 2)
        submitted_proxy = sections[[i for i in ids if 'doc' != i][0]]
        review_state = self.wftool.getInfoFor(submitted_proxy,
                                              'review_state', None)
        self.assertEquals(review_state, 'pending')
        submitted_proxy2 = submitted_proxy.doc2
        review_state2 = self.wftool.getInfoFor(submitted_proxy2,
                                               'review_state', None)
        self.assertEquals(review_state2, 'pending')
        self.assertEquals(submitted_proxy2.Title(), 'New title')

        # Now accept it
        submitted_proxy.content_status_modify(workflow_action='accept')
        published_proxy = sections.doc
        published_proxy2 = published_proxy.doc2
        review_state = self.wftool.getInfoFor(published_proxy,
                                              'review_state', None)
        self.assertEquals(review_state, 'published')
        review_state = self.wftool.getInfoFor(published_proxy2,
                                              'review_state', None)
        self.assertEquals(review_state, 'published')
        self.assertEquals(published_proxy2.Title(), 'New title')

        # Now unpublishing
        self.login('reviewer')

        published_proxy.content_status_modify(workflow_action='unpublish')

        self.login('manager')

        self.assert_(not 'doc' in self.portal.sections.objectIds())

        # Cleanup
        self.member_ws.manage_delObjects(['doc'])

    def testSubmitAllDocumentTypes(self):
        ttool = self.portal.portal_types
        for document_type in (tid for tid in DOCUMENT_TYPES
                         if ttool._getOb(tid).cps_proxy_type != 'folder'):
            self._testSubmit(document_type)

    def testSubmitWithModifiedWorkflow(self):
        # Now test publication with a modified workflow
        wf_workspace_content_id = 'workspace_content_wf'
        wf_workspace_content = getattr(self.wftool,
                                       wf_workspace_content_id, None)

        # Adding the new state "submitted"
        state_id = 'submitted'
        if wf_workspace_content.states.get(state_id) is not None:
            wf_workspace_content.states.manage_delObjects([state_id])
        wf_workspace_content.states.addState(state_id)
        state = wf_workspace_content.states.get(state_id)
        state.setProperties(title="Submitted",
                            transitions=('modify', 'copy_submit',))
        state.setPermission(ModifyPortalContent, 0,
                            ('Manager', 'WorkspaceManager', 'Owner'))
        state.setPermission(View, 0,
                            ('Manager', 'WorkspaceManager',
                             'Owner', 'WorkspaceMember', 'WorkspaceReader'))

        # Modifying the already existing transition modify so that this
        # transition goes to the "work" state.
        trans_id = 'modify'
        if wf_workspace_content.transitions.get(trans_id):
            wf_workspace_content.transitions.manage_delObjects([trans_id])
        wf_workspace_content.transitions.addTransition(trans_id)
        trans = wf_workspace_content.transitions.get(trans_id)
        trans.new_state_id='work'

        # Modifying the already existing state "work"
        state_id = 'work'
        state = wf_workspace_content.states.get(state_id)
        trans_id = 'copy_submit'
        trans = wf_workspace_content.transitions.get(trans_id)
        trans.new_state_id = 'submitted'
        self._testSubmitWithModifiedWorkflow('File')

    # Same as test as above, but here we know what document type causes
    # trouble
    def testSubmitImageGallery(self):
        self._testSubmit("ImageGallery")

    def testSubmitImageGallerySubdocs(self):
        self._testSubmitFolderish("ImageGallery", 'Image')

    # Test the renamming of a published object
    # Trac(#793)
    def testSubmitAndRename(self):
        type_name = 'File'
        id_file = 'file'
        ws = self.portal.workspaces
        
        # Create a new File
        self.wftool.invokeFactoryFor(ws, type_name, id_file)
        proxy = getattr(ws, id_file)

        # Publish it
        proxy.content_status_modify(
            submit=['sections',],
            workflow_action='copy_submit')

        # Renamme
        sc = self.portal.sections
        new_id = 'id2'
        sc.manage_renameObjects([id_file], [new_id])

        # Check this
        self.assert_(new_id in sc.objectIds())
        self.assert_(id_file not in sc.objectIds())

    def testSeveralPublicationAndReindexation(self):
        # http://svn.nuxeo.org/trac/pub/ticket/1434
        # http://svn.nuxeo.org/trac/pub/ticket/1705

        sc = self.portal.sections
        ws = self.portal.workspaces

        # Cleanup the floor.
        sc.manage_delObjects([x.getId() for x in sc.objectValues() if
                              not x.getId().startswith('.')])
        self.assertEqual(len(sc.objectIds()), 1)

        ws.manage_delObjects([x.getId() for x in ws.objectValues() if
                              not x.getId().startswith('.')])
        self.assertEqual(len(ws.objectIds()), 1)

        type_name = 'File'
        id_file = 'file'

        query = {'cps_filter_sets': {'operator': 'and',
                                     'query': ['searchable']},
                 }
        
        # Create a new File
        self.wftool.invokeFactoryFor(ws, type_name, id_file, Title='rfoo')
        self.assertEqual(len(ws.objectIds()), 2)
        
        # Publish it
        proxy = getattr(ws, id_file)
        self.wftool.doActionFor(proxy, 'copy_submit',
                                dest_container='sections',
                                initial_transition='publish')

        self.assertEqual(len(sc.objectIds()), 2)

        # Searching and get 2 results (ws and sections)
        query['SearchableText'] = 'rfoo'
        brains = self.portal.search(query)
        self.assertEqual(len(brains), 2)

        # Change the title
        pxtool = getToolByName(self.portal, 'portal_proxies')
        pxtool.freezeProxy(proxy)

        proxy = getattr(ws, id_file)
        doc = proxy.getEditableContent()
        doc.edit(Title='rbar')
        doc.reindexObject()

        self.assertEqual(len(ws.objectIds()), 2)

        # Here only the one in sections now.
        query['SearchableText'] = 'rfoo'
        brains = self.portal.search(query)
        self.assertEqual(len(brains), 1)

        # Here only the one in workspaces
        query['SearchableText'] = 'rbar'
        brains = self.portal.search(query)
        self.assertEqual(len(brains), 1)

        # Republish.it.
        proxy = getattr(ws, id_file)
        evt_recorder = self.portal.event_recorder
        evt_recorder.clear()
        self.wftool.doActionFor(proxy, 'copy_submit',
                                dest_container='sections',
                                initial_transition='publish')

        self.assertEqual(len(sc.objectIds()), 2)
        events = evt_recorder.getRecords()
        for evt in events:
            if evt[0] == 'workflow_publish':
                self.assertEqual(evt[2]['rpath'], 'sections/%s' % id_file)

        # Here only the one in sections now.
        query['SearchableText'] = 'rfoo'
        brains = self.portal.search(query)
        self.assertEqual(len(brains), 0)

        # Here only the one in workspaces
        query['SearchableText'] = 'rbar'
        brains = self.portal.search(query)
        self.assertEqual(len(brains), 2)

        # Cleanup the floor.
        sc.manage_delObjects([x.getId() for x in sc.objectValues() if
                              not x.getId().startswith('.')])
        self.assertEqual(len(sc.objectIds()), 1)

        ws.manage_delObjects([x.getId() for x in ws.objectValues() if
                              not x.getId().startswith('.')])
        self.assertEqual(len(ws.objectIds()), 1)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPublication))
    return suite

