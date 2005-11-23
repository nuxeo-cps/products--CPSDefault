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

        faq_id_ = self._createObject(self._ws, 'FAQ')
        faq_ = getattr(self._ws, faq_id_)

        faq_info_ = self._ws.getContentInfo(faq_)
        # Test workflow state
        self.assertEqual(
            self._wftool.getInfoFor(faq_, 'review_state'), 'work')

        # Test revision
        self.assertEqual(faq_info_['rev'], '1')

        #
        # Create a FAQ Item within
        #

        faq_item_id_ = self._createObject(faq_, 'FAQitem')
        self.assertEqual(faq_.objectIds(), [faq_item_id_])

        faq_item_ = getattr(faq_, faq_item_id_)
        self.assertEqual(faq_item_.portal_type, 'FAQitem')

        faq_item_info_ = faq_.getContentInfo(faq_item_)
        # Test workflow state
        self.assertEqual(
            self._wftool.getInfoFor(faq_item_, 'review_state'), 'work')

        # Test revision
        self.assertEqual(faq_item_info_['rev'], '1')

        #
        # Publish the whole FAQ
        #

        self._publishObject(faq_, self._sc)

        faq_published_ = getattr(self._sc, faq_id_)
        faq_published_info_ = self._sc.getContentInfo(faq_published_)

        # Test FAQ workflow state
        self.assertEqual(faq_published_info_['review_state'], 'published')

        # Test FAQ revision
        self.assertEqual(faq_published_info_['rev'], '1')

        faq_published_item_ = getattr(faq_published_, faq_item_id_)
        faq_published_item_info_ = faq_published_.getContentInfo(
            faq_published_item_)

        # Test FAQitem workflow state
        self.assertEqual(
            self._wftool.getInfoFor(faq_published_item_, 'review_state'),
            'published')

        # Test FAQitem revision
        self.assertEqual(faq_published_item_info_['rev'], '1')
        

        #
        # Modify the FAQ Item within the workspace.
        #

        self._createNewRevisionFor(faq_item_)
        faq_item_info_ = faq_.getContentInfo(faq_item_)

        # Test FAQitem workflow state
        self.assertEqual(
            self._wftool.getInfoFor(faq_item_, 'review_state'), 'work')

        # Test FAQitem revision
        self.assertEqual(faq_item_info_['rev'], '2')


        #
        # Publish the whole FAQ back
        #

        self.assertEqual(self._sc.objectIds(),
                         ['.cps_workflow_configuration', faq_.getId()])

        self._publishObject(faq_, self._sc)

        self.assertEqual(self._sc.objectIds(),
                         ['.cps_workflow_configuration', faq_.getId()])

        faq_published_ = getattr(self._sc, faq_id_)

        faq_published_info_ = self._sc.getContentInfo(faq_published_)
        self.assertEqual(faq_published_.objectIds(), [faq_item_id_])

        # Test FAQ workflow state
        self.assertEqual(faq_published_info_['review_state'], 'published')

        # Test FAQ revision
        self.assertEqual(faq_published_info_['rev'], '1')

        faq_published_item_ = getattr(faq_published_, faq_item_id_)
        self.assertEqual(faq_published_item_.portal_type, 'FAQitem')
        faq_published_item_info_ = faq_published_.getContentInfo(
            faq_published_item_)

        # Test FAQitem workflow state
        self.assertEqual(
            self._wftool.getInfoFor(faq_published_item_, 'review_state'),
            'published')

        # Test FAQitem revision
        self.assertEqual(faq_published_item_info_['rev'], '2')

        #
        # Add another items within the FAQ in workspace
        #

        faq_ = getattr(self._ws, faq_id_)

        faq_item_id_2_ = self._createObject(faq_, 'FAQitem')
        self.assertEqual(faq_.objectIds(),
                         [faq_item_id_, faq_item_id_2_])

        faq_item_2_ = getattr(faq_, faq_item_id_2_)
        self.assertEqual(faq_item_.portal_type, 'FAQitem')

        faq_item_info_2_ = faq_.getContentInfo(faq_item_2_)

        # Test workflow state
        self.assertEqual(
            self._wftool.getInfoFor(faq_item_2_, 'review_state'), 'work')


        #
        # Publish the whole FAQ back
        #

        self.assertEqual(self._sc.objectIds(),
                         ['.cps_workflow_configuration', faq_.getId()])

        self._publishObject(faq_, self._sc)

        self.assertEqual(self._sc.objectIds(),
                         ['.cps_workflow_configuration', faq_.getId()])

        faq_published_ = getattr(self._sc, faq_id_)

        faq_published_info_ = self._sc.getContentInfo(faq_published_)
        self.assertEqual(faq_published_.objectIds(),
                         [faq_item_id_, faq_item_id_2_])

        # Test FAQ workflow state
        self.assertEqual(faq_published_info_['review_state'], 'published')

        # Test FAQ revision
        self.assertEqual(faq_published_info_['rev'], '1')

        faq_published_item_ = getattr(faq_published_, faq_item_id_)
        self.assertEqual(faq_published_item_.portal_type, 'FAQitem')
        faq_published_item_info_ = faq_published_.getContentInfo(
            faq_published_item_)

        # Test FAQitem workflow state
        self.assertEqual(
            self._wftool.getInfoFor(faq_published_item_, 'review_state'),
            'published')

        # Test FAQitem revision
        self.assertEqual(faq_published_item_info_['rev'], '2')

        faq_published_item_2_ = getattr(faq_published_, faq_item_id_2_)
        self.assertEqual(faq_published_item_2_.portal_type, 'FAQitem')
        faq_published_item_info_2_ = faq_published_.getContentInfo(
            faq_published_item_2_)

        # Test FAQitem workflow state
        self.assertEqual(
            self._wftool.getInfoFor(faq_published_item_2_, 'review_state'),
            'published')

        # Test FAQitem revision
        self.assertEqual(faq_published_item_info_2_['rev'], '1')
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderishPublicationTestCase))
    return suite

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
