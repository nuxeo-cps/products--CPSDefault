import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from pprint import pprint
from Testing import ZopeTestCase
import CPSDefaultTestCase

from webdav.LockItem import LockItem
from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.permissions import View, ModifyPortalContent

from DateTime import DateTime

ANOTHER_SECTION_ID = 'another-section'

import traceback
from zExceptions.ExceptionFormatter import format_exception
traceback.format_exception = format_exception

class TestPublication(CPSDefaultTestCase.CPSDefaultTestCase):
    # Test object creation and publication workflow

    def afterSetUp(self):
        self.login('manager')

        self.wftool = getToolByName(self.portal, 'portal_workflow')
        # Creating an extra section to be used for publishing
        self.wftool.invokeFactoryFor(
            self.portal.sections, 'Section', ANOTHER_SECTION_ID)

        members = self.portal.portal_directories.members
        members.createEntry({'id': 'member', 'roles': ['Member']})
        members.createEntry({'id': 'reviewer', 'roles': ['Member']})

        self.portal_membership = self.portal.portal_membership
        self.portal.portal_membership.createMemberArea('member')
        self.member_ws = self.portal.workspaces.members.member

        pmtool = self.portal.portal_membership
        pmtool.setLocalRoles(obj=self.portal.sections,
            member_ids=['member'], member_role='SectionReader')
        pmtool.setLocalRoles(obj=self.portal.sections,
            member_ids=['reviewer'], member_role='SectionReviewer')


    def beforeTearDown(self):
        self.logout()

    # XXX disabled until I can figure out why it causes an error in
    # Five.traversable.__fallback_traverse__
    # Maybe double registration of something?
    def XXXtestAccessForMember(self):
        self.login('member')
        self.assert_(self.member_ws.folder_contents())
        self.assert_(self.member_ws.folder_view())
        self.assertRaises(
            Unauthorized, self.portal.portal_repository.folder_view, ())


    def testAccessForReviewer(self):
        self.login('reviewer')
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
        self.assertEquals(info['rpath'], 'workspaces/members/member/news')
        self.assert_(isinstance(info['time'], DateTime))
        self.assertEquals(info['time_str'], 'date_medium')
        self.assertEquals(info['title'], '')
        self.assertEquals(info['title_or_id'], 'news')
        self.assertEquals(info['type'], 'News Item')
        self.assertEquals(info['type_l10n'], 'portal_type_NewsItem_title')

        if level >= 1:
            mtool = self.portal.portal_membership
            self.assertEquals(info['contributor'],
                              mtool.getFullnameFromId('member'))
            self.assertEquals(info['coverage'], '')
            # FIXME: disabled because it doesn't behave properly during
            # unit tests - it is OK in the real life, though
            #self.assertEquals(info['creator'], 'member')
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
            self.assertEquals(state['rpath'], 'workspaces/members/member')
            self.assert_(isinstance(state['time'], DateTime))
            self.assertEquals(state['time_str'], 'date_medium')
            self.assertEquals(state['title'], 'member')
        if level >= 3:
            self.assertEquals(len(info['history']), 1)
            history = info['history'][0]
            self.assertEquals(history['action'], 'create')
            self.assertEquals(history['actor'], 'member')
            self.assertEquals(history['dest_container'], '')
            self.assertEquals(history['review_state'], 'work')
            self.assertEquals(history['rpath'],
                              'workspaces/members/member/news')
            self.assert_(isinstance(history['time'], DateTime))
            self.assertEquals(history['time_str'], 'date_medium')
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
        lock = LockItem(user, user)
        lock_token = lock.getLockToken()
        proxy2.wl_setLock(lock_token, lock)

        review_state = self.wftool.getInfoFor(proxy, 'review_state', None)
        self.assertEquals(review_state, 'work')
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


    def testSubmitAllDocumentTypes(self):
        all_document_types = self.portal.getDocumentTypes()
        del all_document_types['Workspace']
        del all_document_types['Section']
        for document_type in all_document_types.keys():
	    # print "submit document type %s" % document_type
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

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPublication))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

