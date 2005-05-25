# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# Anahide Tchertchian <at@nuxeo.com>
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

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase

class TestMembershipTool(CPSDefaultTestCase.CPSDefaultTestCase):
    login_id = 'manager'

    def afterSetUp(self):
        self.login(self.login_id)
        self.pmtool = self.portal.portal_membership

    def beforeTearDown(self):
        self.logout()

    def test_createMemberArea(self):
        self.assertEqual(self.pmtool.getHomeFolder(), None)
        self.pmtool.createMemberArea()
        homefolder = self.pmtool.getHomeFolder()
        self.assertNotEqual(homefolder, None)

        # check home folder properties
        self.assertEqual(homefolder.portal_type,
                         self.pmtool.memberfolder_portal_type)
        self.assertEqual(homefolder.getId(),
                         self.login_id)
        # get user title
        self.members = self.portal.portal_directories.members
        member_title = self.members.getEntry(self.login_id, default={}).get(
            self.members.title_field)
        if not member_title:
            member_title = self.login_id
        self.assertEqual(homefolder.Title(), member_title)
        portal_url = self.portal.absolute_url()
        homefolder_rpath = self.pmtool.membersfolder_id + '/' + self.login_id
        self.assertEqual(self.pmtool.getHomeUrl(),
                         portal_url + '/' + homefolder_rpath)

        # check home folder local roles
        self.assertEqual(homefolder.get_local_roles(),
                         ((self.login_id, ('Owner', 'WorkspaceManager')),))

        # check content created if portal_calendar is installed
        if getattr(self.portal, 'portal_calendar', None) is not None:
            self.assert_('calendar' in homefolder.objectIds())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMembershipTool))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
