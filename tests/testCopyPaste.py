# -*- coding: iso-8859-15 -*-
# Copyright (c) 2005 Nuxeo SAS <http://nuxeo.com>
# Author : Julien Anguenot <ja@nuxeo.com>
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
""" Test various Copy Paste (cpp) situations
"""

import unittest

from OFS.CopySupport import CopyError
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase

class TestCopyPasteBase(CPSTestCase):

    def afterSetUp(self):
        self._ws = self.portal.workspaces
        self._sc = self.portal.sections
        self._wftool = self.portal.portal_workflow
        self._ttool = self.portal.portal_types

        # Add a fake document type with folder type workflow
        self._addFakeType()

    def beforeTearDown(self):
        self.logout()

    def _addFakeType(self):
        ti = self._ttool.addFlexibleTypeInformation(id='fakeFolder')
        properties = {
            'content_meta_type': 'CPS Document',
            'product': 'CPSDocument',
            'factory': 'addCPSDocument',
            'immediate_view': 'cpsdocument_view',
            'allowed_content_types': ('fakeFolderItem',),
            'cps_proxy_type': 'folderishdocument',
            'schemas': ['metadata', 'common'],
            'layouts': ['common',],
            'cps_workspace_wf': 'workspace_folder_wf',
            }
        ti.manage_changeProperties(**properties)
        
        ti = self._ttool.addFlexibleTypeInformation(id='fakeFolderItem')
        properties = {
            'content_meta_type': 'CPS Document',
            'product': 'CPSDocument',
            'factory': 'addCPSDocument',
            'immediate_view': 'cpsdocument_view',
            'allowed_content_types': (),
            'cps_proxy_type': 'document',
            'schemas': ['metadata', 'common'],
            'layouts': ['common',],
            'cps_workspace_wf': 'workspace_content_wf',
            }
        ti.manage_changeProperties(**properties)

        # add the document's workflow to sections and workspaces
        wfc = getattr(self._sc, '.cps_workflow_configuration')
        wfc.setChain('fakeFolder', ('section_folder_wf',))
        wfc.setChain('fakeFolderItem', ('section_folder_wf',))
        
        wfc = getattr(self._ws, '.cps_workflow_configuration')
        wfc.setChain('fakeFolder', ('workspace_folder_wf',))
        wfc.setChain('fakeFolderItem', ('workspace_folder_wf',))

        # add the document type to the section/workspace allowed content types
        sectionACT = list(self._ttool.Section.allowed_content_types)
        sectionACT.append('fakeFolder')
        sectionACT.append('fakeFolderItem')
        self._ttool.Section.allowed_content_types = sectionACT

        workspaceACT = list(self._ttool.Workspace.allowed_content_types)
        workspaceACT.append('fakeFolder')
        workspaceACT.append('fakeFolderItem')
        self._ttool.Workspace.allowed_content_types = workspaceACT

    def _createObject(self, where, type_name):
        id_ = where.computeId()
        self._wftool.invokeFactoryFor(where, type_name, id_)
        return id_

class TestCopyPasteManager(TestCopyPasteBase):

    login_id = 'manager'

    def afterSetUp(self):
        self.login(self.login_id)
        TestCopyPasteBase.afterSetUp(self)
        
    #
    # Workspaces -> Workspaces
    #

    def test_workspace_2_workspace_document(self):

        # Copy paste a document from workspace to workspace and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws, 'File')
        cp = self._ws.manage_CPScopyObjects([id_])
        self._ws.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._ws, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'work')

    def test_workspace_2_workspace_folder(self):

        # Copy paste a folder from workspace to workspace and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws, 'Workspace')

        # Add a sub-object
        sub_id_ = self._createObject(getattr(self._ws, id_), 'File')

        cp = self._ws.manage_CPScopyObjects([id_])
        self._ws.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._ws, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'work')

        sub_ob = getattr(ws_ob, sub_id_)
        review_state = self._wftool.getInfoFor(sub_ob, 'review_state')
        self.assertEqual(review_state, 'work')

    def test_workspace_2_workspace_folderish(self):

        # Copy paste a folderish from workspace to workspace and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws, 'FAQ')

        # Add a sub-object
        sub_id_ = self._createObject(getattr(self._ws, id_), 'FAQitem')

        cp = self._ws.manage_CPScopyObjects([id_])
        self._ws.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._ws, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'work')

        sub_ob = getattr(ws_ob, sub_id_)
        review_state = self._wftool.getInfoFor(sub_ob, 'review_state')
        self.assertEqual(review_state, 'work')

    #
    # Workspaces -> sections
    #

    def test_workspaces_2_sections_document(self):

        # Copy paste a document from workspace to section and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws, 'File')
        cp = self._ws.manage_CPScopyObjects([id_])
        self._sc.manage_CPSpasteObjects(cp)

        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'published')

    def test_workspaces_2_sections_folder(self):

        # Copy paste a folder from workspace to section and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws, 'fakeFolder')
        cp = self._ws.manage_CPScopyObjects([id_])

        # Add a sub-object
        sub_id_ = self._createObject(getattr(self._ws, id_), 'fakeFolderItem')

        self._sc.manage_CPSpasteObjects(cp)

        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'work')

        sub_ob = getattr(sc_ob, sub_id_)
        review_state = self._wftool.getInfoFor(sub_ob, 'review_state')

        # This is not a folderish document so the children are not
        # gonna be workflowed
        self.assertEqual(review_state, 'work')

    def test_workspaces_2_sections_folderish(self):

        # Copy paste a folderish from workspace to section and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws, 'FAQ')
        cp = self._ws.manage_CPScopyObjects([id_])

        # Add a sub-object
        sub_id_ = self._createObject(getattr(self._ws, id_), 'FAQitem')

        self._sc.manage_CPSpasteObjects(cp)

        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'published')

        sub_ob = getattr(sc_ob, sub_id_)
        review_state = self._wftool.getInfoFor(sub_ob, 'review_state')

        # This is not a folderish document so the children are not
        # gonna be workflowed
        self.assertEqual(review_state, 'published')

    #
    # Sections -> Sections
    #

    def test_section_2_section_document(self):

        # Copy paste a document from section to section and check the
        # status of the pasted objects

        # First create one within the workspace and publish it
        id_ = self._createObject(self._ws, 'File')
        ws_ob_ = getattr(self._ws, id_)
        ws_ob_.content_status_modify(
            'copy_submit',
            submit=['sections', 'sections/'],
            )

        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'pending')

        # Copy and paste it within the same section
        cp = self._sc.manage_CPScopyObjects([id_])
        self._sc.manage_CPSpasteObjects(cp)

        sc_ob = getattr(self._sc, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'pending')

    def test_section_2_section_folder(self):

        # Copy paste a folder from section to section and check the
        # status of the pasted objects

        # First create one within the workspace and publish it
        id_ = self._createObject(self._sc, 'Section')
        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'work')

        # Copy and paste it within the same section
        cp = self._sc.manage_CPScopyObjects([id_])
        self._sc.manage_CPSpasteObjects(cp)

        sc_ob = getattr(self._sc, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'work')

    def test_section_2_section_folderish(self):

        # Copy paste a folderish from section to section and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws, 'FAQ')
        ob_ = getattr(self._ws, id_)

        # Add a sub-object
        sub_id_ = self._createObject(ob_, 'FAQitem')

        self.assertEqual('work',
                         self._wftool.getInfoFor(ob_, 'review_state'))
        self.assertEqual('work',
                         self._wftool.getInfoFor(getattr(ob_, sub_id_),
                                                 'review_state'))

        ob_.content_status_modify(
            'copy_submit',
            submit=['sections', 'sections/'],
            )

        sc_ob_ = getattr(self._sc, id_)
        self.assertEqual('pending',
                         self._wftool.getInfoFor(sc_ob_, 'review_state'))
        self.assertEqual('pending',
                         self._wftool.getInfoFor(
            getattr(sc_ob_, sub_id_), 'review_state'))


        cp = self._sc.manage_CPScopyObjects([id_])
        self._sc.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._sc, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'pending')

        sub_ob = getattr(ws_ob, sub_id_)
        review_state = self._wftool.getInfoFor(sub_ob, 'review_state')
        self.assertEqual(review_state, 'pending')

    #
    # Sections -> Workspaces
    #

    def test_section_2_workspace_document(self):

        # Copy paste a document from section to section and check the
        # status of the pasted objects

        # First create one within the workspace and publish it
        id_ = self._createObject(self._ws, 'File')
        ws_ob_ = getattr(self._ws, id_)
        ws_ob_.content_status_modify(
            'copy_submit',
            submit=['sections', 'sections/'],
            )

        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'pending')

        # Copy and paste it within a workspace
        cp = self._sc.manage_CPScopyObjects([id_])
        self._ws.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._ws, id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'work')

    def test_section_2_workspace_folder(self):

        # Copy paste a folder from section to workspace and check the
        # status of the pasted objects

        # First create one within the workspace and publish it
        id_ = self._createObject(self._sc, 'fakeFolder')
        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'work')

        # Copy and paste it within the same section
        cp = self._sc.manage_CPScopyObjects([id_])
        self._ws.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._ws, id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'work')

    def test_section_2_workspace_folderish(self):

        # Copy paste a folderish from section to section and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws, 'FAQ')
        ob_ = getattr(self._ws, id_)

        # Add a sub-object
        sub_id_ = self._createObject(ob_, 'FAQitem')

        self.assertEqual('work',
                         self._wftool.getInfoFor(ob_, 'review_state'))
        self.assertEqual('work',
                         self._wftool.getInfoFor(getattr(ob_, sub_id_),
                                                 'review_state'))

        ob_.content_status_modify(
            'copy_submit',
            submit=['sections', 'sections/'],
            )

        sc_ob_ = getattr(self._sc, id_)
        self.assertEqual('pending',
                         self._wftool.getInfoFor(sc_ob_, 'review_state'))
        self.assertEqual('pending',
                         self._wftool.getInfoFor(
            getattr(sc_ob_, sub_id_), 'review_state'))


        cp = self._sc.manage_CPScopyObjects([id_])
        self._ws.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._ws, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'work')

        sub_ob = getattr(ws_ob, sub_id_)
        review_state = self._wftool.getInfoFor(sub_ob, 'review_state')
        self.assertEqual(review_state, 'work')

class TestCopyPasteMember(TestCopyPasteBase):

    login_id = 'member'

    def afterSetUp(self):

        self.login('manager')
        self.pmtool = self.portal.portal_membership

        # Create a regular Member with an home folder.
        members = self.portal.portal_directories.members
        members.createEntry({'id': 'member', 'givenName' : 'Foo',
                             'sn': 'Bar', 'roles': ['Member']})
        self.pmtool.createMemberArea('member')
        self.pmtool.setLocalRoles(
            obj=self.portal.sections,
            member_ids=['member'], member_role='SectionManager')
        self.pmtool.setLocalRoles(
            obj=self.portal.members.member,
            member_ids=['member'], member_role='WorkspaceMember')

        self._ws_member = self.portal.members.member
        
        wfc = getattr(self._ws_member, '.cps_workflow_configuration')
        wfc.setChain('fakeFolder', ('workspace_folder_wf',))
        wfc.setChain('fakeFolderItem', ('workspace_folder_wf',))

        # Login as Member and here we go for the tests.
        self.login(self.login_id)
        TestCopyPasteBase.afterSetUp(self)


    #
    # Workspaces -> Workspaces
    #

    def test_workspace_2_workspace_document(self):

        # Copy paste a document from workspace to workspace and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws_member, 'File')
        cp = self._ws_member.manage_CPScopyObjects([id_])
        self._ws_member.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._ws_member, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'work')

    def test_workspace_2_workspace_folder(self):

        # Copy paste a folder from workspace to workspace and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws_member, 'Workspace')

        # Add a sub-object
        sub_id_ = self._createObject(getattr(self._ws_member, id_), 'File')

        cp = self._ws_member.manage_CPScopyObjects([id_])
        self._ws_member.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._ws_member, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'work')

        sub_ob = getattr(ws_ob, sub_id_)
        review_state = self._wftool.getInfoFor(sub_ob, 'review_state')
        self.assertEqual(review_state, 'work')

    def test_workspace_2_workspace_folderish(self):

        # Copy paste a folderish from workspace to workspace and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws_member, 'FAQ')

        # Add a sub-object
        sub_id_ = self._createObject(getattr(self._ws_member, id_), 'FAQitem')

        cp = self._ws_member.manage_CPScopyObjects([id_])
        self._ws_member.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._ws_member, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'work')

        sub_ob = getattr(ws_ob, sub_id_)
        review_state = self._wftool.getInfoFor(sub_ob, 'review_state')
        self.assertEqual(review_state, 'work')

    #
    # Workspaces -> sections
    #

    def test_workspaces_2_sections_document(self):

        # Copy paste a document from workspace to section and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws_member, 'File')
        cp = self._ws_member.manage_CPScopyObjects([id_])
        self._sc.manage_CPSpasteObjects(cp)

        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'published')


    def test_workspaces_2_sections_folder(self):

        # Copy paste a folder from workspace to section and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws_member, 'fakeFolder')
        cp = self._ws_member.manage_CPScopyObjects([id_])

        # Add a sub-object
        sub_id_ = self._createObject(
            getattr(self._ws_member, id_), 'fakeFolderItem')

        self._sc.manage_CPSpasteObjects(cp)

        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'work')

        sub_ob = getattr(sc_ob, sub_id_)
        review_state = self._wftool.getInfoFor(sub_ob, 'review_state')

        # This is not a folderish document so the children are not
        # gonna be workflowed
        self.assertEqual(review_state, 'work')

    def test_workspaces_2_sections_folderish(self):

        # Copy paste a folderish from workspace to section and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws_member, 'FAQ')
        cp = self._ws_member.manage_CPScopyObjects([id_])

        # Add a sub-object
        sub_id_ = self._createObject(getattr(self._ws_member, id_), 'FAQitem')

        self._sc.manage_CPSpasteObjects(cp)

        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'published')

        sub_ob = getattr(sc_ob, sub_id_)
        review_state = self._wftool.getInfoFor(sub_ob, 'review_state')

        # This is not a folderish document so the children are not
        # gonna be workflowed
        self.assertEqual(review_state, 'published')

    #
    # Sections -> Sections
    #

    def test_section_2_section_document(self):

        # Copy paste a document from section to section and check the
        # status of the pasted objects

        # First create one within the workspace and publish it
        id_ = self._createObject(self._ws_member, 'File')
        ws_ob_ = getattr(self._ws_member, id_)
        ws_ob_.content_status_modify(
            'copy_submit',
            submit=['sections', 'sections/'],
            )

        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'pending')

        # Copy and paste it within the same section
        cp = self._sc.manage_CPScopyObjects([id_])
        self._sc.manage_CPSpasteObjects(cp)

        sc_ob = getattr(self._sc, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'pending')

    def test_section_2_section_folder(self):

        # Copy paste a folder from section to section and check the
        # status of the pasted objects

        # First create one within the workspace and publish it
        id_ = self._createObject(self._sc, 'Section')
        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'work')

        # Copy and paste it within the same section
        cp = self._sc.manage_CPScopyObjects([id_])
        self._sc.manage_CPSpasteObjects(cp)

        sc_ob = getattr(self._sc, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'work')

    def test_section_2_section_folderish(self):

        # Copy paste a folderish from section to section and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws_member, 'FAQ')
        ob_ = getattr(self._ws_member, id_)

        # Add a sub-object
        sub_id_ = self._createObject(ob_, 'FAQitem')

        self.assertEqual('work',
                         self._wftool.getInfoFor(ob_, 'review_state'))
        self.assertEqual('work',
                         self._wftool.getInfoFor(getattr(ob_, sub_id_),
                                                 'review_state'))

        ob_.content_status_modify(
            'copy_submit',
            submit=['sections', 'sections/'],
            )

        sc_ob_ = getattr(self._sc, id_)
        self.assertEqual('pending',
                         self._wftool.getInfoFor(sc_ob_, 'review_state'))
        self.assertEqual('pending',
                         self._wftool.getInfoFor(
            getattr(sc_ob_, sub_id_), 'review_state'))


        cp = self._sc.manage_CPScopyObjects([id_])
        self._sc.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._sc, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'pending')

        sub_ob = getattr(ws_ob, sub_id_)
        review_state = self._wftool.getInfoFor(sub_ob, 'review_state')
        self.assertEqual(review_state, 'pending')

    #
    # Sections -> Workspaces
    #

    def test_section_2_workspace_document(self):

        # Copy paste a document from section to section and check the
        # status of the pasted objects

        # First create one within the workspace and publish it
        id_ = self._createObject(self._ws_member, 'File')
        ws_ob_ = getattr(self._ws_member, id_)
        ws_ob_.content_status_modify(
            'copy_submit',
            submit=['sections', 'sections/'],
            )

        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'pending')

        # Copy and paste it within a workspace
        cp = self._sc.manage_CPScopyObjects([id_])
        self._ws_member.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._ws_member, id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'work')

    def test_section_2_workspace_folder(self):

        # Copy paste a folder from section to workspace and check the
        # status of the pasted objects

        # First create one within the workspace and publish it
        id_ = self._createObject(self._sc, 'fakeFolder')
        sc_ob = getattr(self._sc, id_)
        review_state = self._wftool.getInfoFor(sc_ob, 'review_state')
        self.assertEqual(review_state, 'work')

        # Copy and paste it within the same section
        cp = self._sc.manage_CPScopyObjects([id_])
        self._ws_member.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._ws_member, id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'work')

    def test_section_2_workspace_folderish(self):

        # Copy paste a folderish from section to section and check the
        # status of the pasted objects

        id_ = self._createObject(self._ws_member, 'FAQ')
        ob_ = getattr(self._ws_member, id_)

        # Add a sub-object
        sub_id_ = self._createObject(ob_, 'FAQitem')

        self.assertEqual('work',
                         self._wftool.getInfoFor(ob_, 'review_state'))
        self.assertEqual('work',
                         self._wftool.getInfoFor(getattr(ob_, sub_id_),
                                                 'review_state'))

        ob_.content_status_modify(
            'copy_submit',
            submit=['sections', 'sections/'],
            )

        sc_ob_ = getattr(self._sc, id_)
        self.assertEqual('pending',
                         self._wftool.getInfoFor(sc_ob_, 'review_state'))
        self.assertEqual('pending',
                         self._wftool.getInfoFor(
            getattr(sc_ob_, sub_id_), 'review_state'))


        cp = self._sc.manage_CPScopyObjects([id_])
        self._ws_member.manage_CPSpasteObjects(cp)

        ws_ob = getattr(self._ws_member, 'copy_of_'+id_)
        review_state = self._wftool.getInfoFor(ws_ob, 'review_state')
        self.assertEqual(review_state, 'work')

        sub_ob = getattr(ws_ob, sub_id_)
        review_state = self._wftool.getInfoFor(sub_ob, 'review_state')
        self.assertEqual(review_state, 'work')

class TestCopyPasteForbidden(TestCopyPasteBase):

    # Test forbidden behaviors

    login_id = 'manager'

    def afterSetUp(self):
        self.login(self.login_id)
        TestCopyPasteBase.afterSetUp(self)

    def test_workspaces_2_sections_Workspace_type(self):

        id_ = self._createObject(self._ws, 'Workspace')
        cp = self._ws.manage_CPScopyObjects([id_])
        self.assertRaises(
            CopyError, self._sc.manage_CPSpasteObjects, cp)

    def test_section_2_workspace_Section_type(self):

        id_ = self._createObject(self._sc, 'Section')
        cp = self._sc.manage_CPScopyObjects([id_])
        self.assertRaises(
            CopyError, self._ws.manage_CPSpasteObjects, cp)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCopyPasteManager))
    suite.addTest(unittest.makeSuite(TestCopyPasteMember))
    suite.addTest(unittest.makeSuite(TestCopyPasteForbidden))
    return suite

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
