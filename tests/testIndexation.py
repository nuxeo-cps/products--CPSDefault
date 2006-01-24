# -*- coding: iso-8859-15 -*-
# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
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
""" Test indexation manager in synchronous and asynchronous mode
"""

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
import transaction

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.tests.base.utils import has_path

from Products.CPSCore.IndexationManager import get_indexation_manager
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase

class TestSynchronousIndexation(CPSTestCase):

    login_id = 'manager'

    def afterSetUp(self):
        if self.login_id:
            self.login(self.login_id)
        self.wftool  = getToolByName(self.portal, 'portal_workflow')
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        get_indexation_manager().setSynchronous(True)

    def beforeTearDown(self):
        self.logout()

    def test_indexation_invokeFactory_synchronous(self):
        # Create an object with invokeFactoryFor
        workspaces = self.portal.workspaces
        id = workspaces.computeId()
        self.wftool.invokeFactoryFor(self.portal.workspaces, 'File', id)
        self.assert_(has_path(self.catalog, "/portal/workspaces/%s"%id))

    def test_indexation_copy_paste_synchronous(self):

        workspaces = self.portal.workspaces
        # Create an object with invokeFactoryFor
        id = workspaces.computeId()
        self.wftool.invokeFactoryFor(workspaces, 'File', id)
        self.assert_(has_path(self.catalog, "/portal/workspaces/%s"%id))

        # Paste it and see if it's indexed
        cp = workspaces.manage_CPScopyObjects([id])
        workspaces.manage_CPSpasteObjects(cp)
        self.assert_('copy_of_%s'%id in workspaces.objectIds())
        self.assert_(has_path(self.catalog,
                              "/portal/workspaces/copy_of_%s"%id))

    def test_indexation_cut_paste_synchronous(self):

        workspaces = self.portal.workspaces
        # Create an object with invokeFactoryFor
        id = workspaces.computeId()
        self.wftool.invokeFactoryFor(workspaces, 'File', id)
        self.assert_(has_path(self.catalog, "/portal/workspaces/%s"%id))

        # Create a folder for pasting
        ws_id = workspaces.computeId()
        self.wftool.invokeFactoryFor(workspaces, 'Workspace', ws_id)
        new_ws = getattr(workspaces, ws_id)

        # savepoint to be able to cut
        transaction.savepoint(optimistic=True)

        # Paste it and see if it's indexed
        cp = workspaces.manage_CPScutObjects([id])
        new_ws.manage_CPSpasteObjects(cp)
        self.assert_(not has_path(self.catalog, "/portal/workspaces/%s"%id))
        self.assert_(id in new_ws.objectIds())
        self.assert_(has_path(self.catalog,
                              "/portal/workspaces/%s/%s"%(ws_id, id)))

class TestAsynchronousIndexation(CPSTestCase):

    login_id = 'manager'

    def afterSetUp(self):
        if self.login_id:
            self.login(self.login_id)
            # XXX This should be harmless but makes testMembershipTool fail
            # because member area created still exists, dont know why
            #self.portal.portal_membership.createMemberArea()
        self.wftool  = getToolByName(self.portal, 'portal_workflow')
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        get_indexation_manager().setSynchronous(False)
        # XXX that's for the current transaction, but as soon
        # as we commit/abort there'll be another one...

    def beforeTearDown(self):
        self.logout()

    def test_indexation_invokeFactory_asynchronous(self):
        # Create an object with invokeFactoryFor
        workspaces = self.portal.workspaces
        id = workspaces.computeId()
        self.wftool.invokeFactoryFor(self.portal.workspaces, 'File', id)
        transaction.commit()
        self.assert_(has_path(self.catalog, "/portal/workspaces/%s"%id))

    def test_indexation_copy_paste_asynchronous(self):

        workspaces = self.portal.workspaces
        # Create an object with invokeFactoryFor
        id = workspaces.computeId()
        self.wftool.invokeFactoryFor(workspaces, 'File', id)
        transaction.commit()
        self.assert_(has_path(self.catalog, "/portal/workspaces/%s"%id))

        # Paste it and see if it's indexed
        # XXX here the commit() made us revert to default state,
        # which is synchronous in tests.
        cp = workspaces.manage_CPScopyObjects([id])
        workspaces.manage_CPSpasteObjects(cp)
        self.assert_('copy_of_%s'%id in workspaces.objectIds())
        transaction.commit()
        self.assert_(has_path(self.catalog,
                              "/portal/workspaces/copy_of_%s"%id))

    def test_indexation_cut_paste_asynchronous(self):

        workspaces = self.portal.workspaces
        # Create an object with invokeFactoryFor
        id = workspaces.computeId()
        self.wftool.invokeFactoryFor(workspaces, 'File', id)
        transaction.commit()
        self.assert_(has_path(self.catalog, "/portal/workspaces/%s"%id))

        # Create a folder for pasting
        ws_id = workspaces.computeId()
        self.wftool.invokeFactoryFor(workspaces, 'Workspace', ws_id)
        new_ws = getattr(workspaces, ws_id)

        # savepoint to be able to cut
        transaction.savepoint(optimistic=True)

        # Paste it and see if it's indexed
        cp = workspaces.manage_CPScutObjects([id])
        new_ws.manage_CPSpasteObjects(cp)
        transaction.commit()
        self.assert_(not has_path(self.catalog, "/portal/workspaces/%s"%id))
        self.assert_(id in new_ws.objectIds())
        self.assert_(has_path(self.catalog,
                              "/portal/workspaces/%s/%s"%(ws_id, id)))

    def test_indexation_cut_paste_async_2_indexations_per_transaction(self):

        workspaces = self.portal.workspaces
        # Create an object with invokeFactoryFor
        id = workspaces.computeId()
        self.wftool.invokeFactoryFor(workspaces, 'File', id)
        transaction.commit()
        self.assert_(has_path(self.catalog, "/portal/workspaces/%s"%id))

        # Create a folder for pasting
        ws_id = workspaces.computeId()
        self.wftool.invokeFactoryFor(workspaces, 'Workspace', ws_id)
        new_ws = getattr(workspaces, ws_id)

        # savepoint to be able to cut
        transaction.savepoint(optimistic=True)

        # Paste it and see if it's indexed

        # Modify doc to be cut before so it gets in the queue too
        proxy = getattr(workspaces, id)
        proxy.getEditableContent().edit(proxy=proxy)

        cp = workspaces.manage_CPScutObjects([id])
        new_ws.manage_CPSpasteObjects(cp)
        transaction.commit()
        self.assert_(not has_path(self.catalog, "/portal/workspaces/%s"%id))
        self.assert_(id in new_ws.objectIds())
        self.assert_(has_path(self.catalog,
                              "/portal/workspaces/%s/%s"%(ws_id, id)))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSynchronousIndexation))
    suite.addTest(unittest.makeSuite(TestAsynchronousIndexation))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

