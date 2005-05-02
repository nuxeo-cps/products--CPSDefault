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
from Testing import ZopeTestCase
import CPSDefaultTestCase

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.tests.base.utils import has_path

from Products.CPSCore.IndexationManager import IndexationManager

class TestSynchronousIndexation(CPSDefaultTestCase.CPSDefaultTestCase):

    login_id = 'manager'

    def afterSetUp(self):
        if self.login_id:
            self.login(self.login_id)
            self.portal.portal_membership.createMemberArea()
        self.wftool  = getToolByName(self.portal, 'portal_workflow')
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        IndexationManager.DEFAULT_SYNC = True

    def beforeTearDown(self):
        IndexationManager.DEFAULT_SYNC = True
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

class TestAsynchronousIndexation(CPSDefaultTestCase.CPSDefaultTestCase):

    login_id = 'manager'

    def afterSetUp(self):
        if self.login_id:
            self.login(self.login_id)
            self.portal.portal_membership.createMemberArea()
        self.wftool  = getToolByName(self.portal, 'portal_workflow')
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        IndexationManager.DEFAULT_SYNC = False

    def beforeTearDown(self):
        IndexationManager.DEFAULT_SYNC = True
        self.logout()

    def test_indexation_invokeFactory_asynchronous(self):
        # Create an object with invokeFactoryFor
        workspaces = self.portal.workspaces
        id = workspaces.computeId()
        self.wftool.invokeFactoryFor(self.portal.workspaces, 'File', id)
        get_transaction().commit()
        self.assert_(has_path(self.catalog, "/portal/workspaces/%s"%id))

    def test_indexation_copy_paste_asynchronous(self):

        workspaces = self.portal.workspaces
        # Create an object with invokeFactoryFor
        id = workspaces.computeId()
        self.wftool.invokeFactoryFor(workspaces, 'File', id)
        get_transaction().commit()
        self.assert_(has_path(self.catalog, "/portal/workspaces/%s"%id))

        # Paste it and see if it's indexed
        cp = workspaces.manage_CPScopyObjects([id])
        workspaces.manage_CPSpasteObjects(cp)
        self.assert_('copy_of_%s'%id in workspaces.objectIds())
        get_transaction().commit()
        self.assert_(has_path(self.catalog,
                              "/portal/workspaces/copy_of_%s"%id))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSynchronousIndexation))
    suite.addTest(unittest.makeSuite(TestAsynchronousIndexation))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

