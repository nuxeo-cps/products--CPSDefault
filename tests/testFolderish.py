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
""" Test various folderish behaviors.
"""

import unittest
import CPSDefaultTestCase

class FolderishTestCaseBase(CPSDefaultTestCase.CPSDefaultTestCase):

    def afterSetUp(self):
        self._ws = self.portal.workspaces
        self._sc = self.portal.sections
        self._wftool = self.portal.portal_workflow
        self._pxtool = self.portal.portal_proxies

    def beforeTearDown(self):
        self.logout()

    def _createObject(self, where, type_name):
        id_ = where.computeId()
        self._wftool.invokeFactoryFor(where, type_name, id_)
        return id_

    def _publishObject(self, proxy, where):
        self._wftool.doActionFor(proxy, 'copy_submit',
                                 dest_container='sections',
                                 initial_transition='publish')

    def _createNewRevisionFor(self, proxy):
        """Create a new revision for a given proxy
        """
        self._pxtool.freezeProxy(proxy)
        proxy.getEditableContent()

    def _getWorkflowState(self, proxy):
        state = self._wftool.getInfoFor(proxy, 'review_state')
        return state


class FolderishPublicationTestCase(FolderishTestCaseBase):

    login_id = 'manager'

    def afterSetUp(self):
        self.login(self.login_id)
        FolderishTestCaseBase.afterSetUp(self)

    def test_several_publications(self):
        # https://svn.nuxeo.org/trac/pub/ticket/1139
        # Test the behavior of the folderish documents after several
        # publications. Especially, the workflow states should not be
        # lost

        #
        # Create a FAQ within workspaces
        #

        faq_id = self._createObject(self._ws, 'FAQ')
        faq = getattr(self._ws, faq_id)

        self.assertEqual(faq.portal_type, 'FAQ')
        self.assertEqual(self._getWorkflowState(faq), 'work')
        self.assertEqual(faq.getRevision(), 1)

        #
        # Create a FAQ Item within
        #

        faq_item_id = self._createObject(faq, 'FAQitem')
        self.assertEqual(faq.objectIds(), [faq_item_id])

        faq_item = getattr(faq, faq_item_id)
        self.assertEqual(faq_item.portal_type, 'FAQitem')
        self.assertEqual(self._getWorkflowState(faq_item), 'work')
        self.assertEqual(faq_item.getRevision(), 1)

        #
        # Publish the whole FAQ
        #

        self._publishObject(faq, self._sc)

        pub_faq = getattr(self._sc, faq_id)
        self.assertEqual(self._getWorkflowState(pub_faq), 'published')
        self.assertEqual(pub_faq.getRevision(), 1)

        pub_faq_item = getattr(pub_faq, faq_item_id)
        self.assertEqual(self._getWorkflowState(pub_faq_item), 'published')
        self.assertEqual(pub_faq_item.getRevision(), 1)

        #
        # Modify the FAQ Item within the workspace.
        #

        self._createNewRevisionFor(faq_item)
        self.assertEqual(self._getWorkflowState(faq_item), 'work')
        self.assertEqual(faq_item.getRevision(), 2)

        #
        # Publish the whole FAQ back
        #

        self.assertEqual(self._sc.objectIds(),
                         ['.cps_workflow_configuration', faq.getId()])

        self._publishObject(faq, self._sc)

        self.assertEqual(self._sc.objectIds(),
                         ['.cps_workflow_configuration', faq.getId()])

        pub_faq = getattr(self._sc, faq_id)
        self.assertEqual(pub_faq.objectIds(), [faq_item_id])
        self.assertEqual(self._getWorkflowState(pub_faq), 'published')
        self.assertEqual(pub_faq.getRevision(), 1)

        pub_faq_item = getattr(pub_faq, faq_item_id)
        self.assertEqual(self._getWorkflowState(pub_faq_item), 'published')
        self.assertEqual(pub_faq_item.getRevision(), 2)

        #
        # Add another items within the FAQ in workspace
        #

        faq = getattr(self._ws, faq_id)

        faq_item_id_2 = self._createObject(faq, 'FAQitem')
        self.assertEqual(faq.objectIds(), [faq_item_id, faq_item_id_2])

        faq_item_2 = getattr(faq, faq_item_id_2)
        self.assertEqual(faq_item_2.portal_type, 'FAQitem')
        self.assertEqual(self._getWorkflowState(faq_item_2), 'work')
        self.assertEqual(faq_item_2.getRevision(), 1)

        #
        # Publish the whole FAQ back
        #

        self.assertEqual(self._sc.objectIds(),
                         ['.cps_workflow_configuration', faq.getId()])

        self._publishObject(faq, self._sc)

        self.assertEqual(self._sc.objectIds(),
                         ['.cps_workflow_configuration', faq.getId()])

        pub_faq = getattr(self._sc, faq_id)

        self.assertEqual(pub_faq.objectIds(), [faq_item_id, faq_item_id_2])
        self.assertEqual(self._getWorkflowState(pub_faq), 'published')
        self.assertEqual(pub_faq.getRevision(), 1)

        pub_faq_item = getattr(pub_faq, faq_item_id)
        self.assertEqual(pub_faq_item.portal_type, 'FAQitem')
        self.assertEqual(self._getWorkflowState(pub_faq_item), 'published')
        self.assertEqual(pub_faq_item.getRevision(), 2)

        pub_faq_item_2 = getattr(pub_faq, faq_item_id_2)
        self.assertEqual(pub_faq_item_2.portal_type, 'FAQitem')
        self.assertEqual(self._getWorkflowState(pub_faq_item_2), 'published')
        self.assertEqual(pub_faq_item_2.getRevision(), 1)


    def test_several_embedded_publications(self):
        # https://svn.nuxeo.org/trac/pub/ticket/1239: Folderish documents
        # workflows are not enough recursive.
        # Test the behavior of the folderish documents after several
        # publications in a hierarchy of more than 1 level

        # modify the FAQ content type so that FAQS are allowed inside FAQS
        ttool = self.portal.portal_types
        allowed = list(ttool['FAQ'].allowed_content_types)
        ttool['FAQ'].allowed_content_types = allowed + ['FAQItem']

        #
        # Create a FAQ within workspaces
        #

        faq_id = self._createObject(self._ws, 'FAQ')
        faq = getattr(self._ws, faq_id)

        self.assertEqual(faq.portal_type, 'FAQ')
        self.assertEqual(self._getWorkflowState(faq), 'work')
        self.assertEqual(faq.getRevision(), 1)

        #
        # Create a sub FAQ
        #

        sub_faq_id = self._createObject(faq, 'FAQ')
        self.assertEqual(faq.objectIds(), [sub_faq_id])

        sub_faq = getattr(faq, sub_faq_id)
        self.assertEqual(sub_faq.portal_type, 'FAQ')
        self.assertEqual(self._getWorkflowState(sub_faq), 'work')
        self.assertEqual(sub_faq.getRevision(), 1)

        #
        # Create a FAQ Item within sub FAQ
        #

        faq_item_id = self._createObject(sub_faq, 'FAQitem')
        self.assertEqual(sub_faq.objectIds(), [faq_item_id])

        faq_item = getattr(sub_faq, faq_item_id)
        self.assertEqual(faq_item.portal_type, 'FAQitem')
        self.assertEqual(self._getWorkflowState(faq_item), 'work')
        self.assertEqual(faq_item.getRevision(), 1)

        #
        # Publish the whole FAQ
        #

        self._publishObject(faq, self._sc)

        pub_faq = getattr(self._sc, faq_id)
        self.assertEqual(self._getWorkflowState(pub_faq), 'published')
        self.assertEqual(pub_faq.getRevision(), 1)
        self.assertEqual(pub_faq.objectIds(), [sub_faq_id])

        pub_sub_faq = getattr(pub_faq, sub_faq_id)
        self.assertEqual(self._getWorkflowState(pub_sub_faq), 'published')
        self.assertEqual(pub_sub_faq.getRevision(), 1)
        self.assertEqual(pub_sub_faq.objectIds(), [faq_item_id])

        pub_faq_item = getattr(pub_sub_faq, faq_item_id)
        self.assertEqual(self._getWorkflowState(pub_faq_item), 'published')
        self.assertEqual(pub_faq_item.getRevision(), 1)

        #
        # Modify the FAQ Item within the workspace.
        #

        self._createNewRevisionFor(faq_item)
        self.assertEqual(self._getWorkflowState(faq_item), 'work')
        self.assertEqual(faq_item.getRevision(), 2)

        #
        # Publish the whole FAQ back
        #

        self.assertEqual(self._sc.objectIds(),
                         ['.cps_workflow_configuration', faq.getId()])

        self._publishObject(faq, self._sc)

        self.assertEqual(self._sc.objectIds(),
                         ['.cps_workflow_configuration', faq.getId()])

        pub_faq = getattr(self._sc, faq_id)
        self.assertEqual(self._getWorkflowState(pub_faq), 'published')
        self.assertEqual(pub_faq.getRevision(), 1)
        self.assertEqual(pub_faq.objectIds(), [sub_faq_id])

        pub_sub_faq = getattr(pub_faq, sub_faq_id)
        self.assertEqual(self._getWorkflowState(pub_sub_faq), 'published')
        self.assertEqual(pub_sub_faq.getRevision(), 1)
        self.assertEqual(pub_sub_faq.objectIds(), [faq_item_id])

        pub_faq_item = getattr(pub_sub_faq, faq_item_id)
        self.assertEqual(self._getWorkflowState(pub_faq_item), 'published')
        # revision has changed
        self.assertEqual(pub_faq_item.getRevision(), 2)

        #
        # Add another item within the sub FAQ in workspace
        #

        faq_item_id_2 = self._createObject(sub_faq, 'FAQitem')
        self.assertEqual(sub_faq.objectIds(), [faq_item_id, faq_item_id_2])

        faq_item_2 = getattr(sub_faq, faq_item_id_2)
        self.assertEqual(faq_item_2.portal_type, 'FAQitem')
        self.assertEqual(self._getWorkflowState(faq_item_2), 'work')
        self.assertEqual(faq_item_2.getRevision(), 1)

        #
        # Publish the whole FAQ back
        #

        self.assertEqual(self._sc.objectIds(),
                         ['.cps_workflow_configuration', faq.getId()])

        self._publishObject(faq, self._sc)

        self.assertEqual(self._sc.objectIds(),
                         ['.cps_workflow_configuration', faq.getId()])

        pub_faq = getattr(self._sc, faq_id)
        self.assertEqual(self._getWorkflowState(pub_faq), 'published')
        self.assertEqual(pub_faq.getRevision(), 1)
        self.assertEqual(pub_faq.objectIds(), [sub_faq_id])

        pub_sub_faq = getattr(pub_faq, sub_faq_id)
        self.assertEqual(self._getWorkflowState(pub_sub_faq), 'published')
        self.assertEqual(pub_sub_faq.getRevision(), 1)
        # second faq item has been added
        self.assertEqual(pub_faq.objectIds(), [faq_item_id, faq_item_id_2])

        pub_faq_item = getattr(pub_sub_faq, faq_item_id)
        self.assertEqual(self._getWorkflowState(pub_faq_item), 'published')
        # revision is still changed
        self.assertEqual(pub_faq_item.getRevision(), 2)

        pub_faq_item_2 = getattr(pub_sub_faq, faq_item_id_2)
        self.assertEqual(self._getWorkflowState(pub_faq_item_2), 'published')
        self.assertEqual(pub_faq_item_2.getRevision(), 1)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderishPublicationTestCase))
    return suite

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
