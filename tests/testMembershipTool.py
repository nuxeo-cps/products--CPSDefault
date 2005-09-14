# -*- encoding: iso-8859-15 -*-
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

from time import time
import sha
import unittest
import CPSDefaultTestCase
from Testing.ZopeTestCase import user_name

class TestMembershipTool(CPSDefaultTestCase.CPSDefaultTestCase):
    login_id = 'manager'

    def afterSetUp(self):
        self.login(self.login_id)
        self.pmtool = self.portal.portal_membership

        members = self.portal.portal_directories.members
        members.createEntry({'id': 'member', 'roles': ['Member']})
        members.createEntry({'id': 'wsmanager', 'roles': ['Member']})
        members.createEntry({'id': 'semanager', 'roles': ['Member']})

        self.pmtool.createMemberArea('member')
        self.pmtool.createMemberArea('wsmanager')
        self.pmtool.createMemberArea('semanager')
        
        self.member_ws = self.portal.workspaces.members.member

        self.pmtool.setLocalRoles(
            obj=self.portal.sections,
            member_ids=['member'], member_role='SectionReader')

        self.pmtool.setLocalRoles(
            obj=self.portal.workspaces,
            member_ids=['member'], member_role='WorkspaceReader')

        self.pmtool.setLocalRoles(
            obj=self.portal.workspaces,
            member_ids=['wsmanager'], member_role='WorkspaceManager')

        self.pmtool.setLocalRoles(
            obj=self.portal.sections,
            member_ids=['semanager'], member_role='SectionManager')

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

        # check content created if portal_cpscalendar is installed
        portal_cpscalendar = getattr(self.portal, 'portal_cpscalendar', None)
        if portal_cpscalendar is not None:
            create_calendar = getattr(portal_cpscalendar, 'create_member_calendar', 1)
        else:
            create_calendar = 0
        if create_calendar:
            self.assert_('calendar' in homefolder.objectIds())
        else:
            self.assertEqual(homefolder.objectIds(), [])

    def test_getEmail(self):
        # This test is more useful if you are not logged in a manager:
        self.login(user_name)
        members = self.portal.portal_directories.members
        email = 'test@test.no'
        emission_time = str(int(time()))

        entry = members._getEntry(self.login_id)
        entry['email'] = email
        members._editEntry(entry)
        email = self.pmtool.getEmailFromUsername(self.login_id)
        self.assertEqual(email, email)

        # Do it backwards!
        hash_object = sha.new()
        hash_object.update(email)
        hash_object.update(emission_time)
        hash_object.update(self.pmtool.getNonce())
        reset_token = hash_object.hexdigest()
        users = self.pmtool.getUsernamesFromEmail(email, emission_time,
                                                  reset_token)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], self.login_id)

    def test_ManagerCanMemberChangeLocalRoles(self):

        # Manager can change them everywhere

        self.login('manager')
        self.assert_(
            self.pmtool.canMemberChangeLocalRoles(self.portal.workspaces))
        self.assert_(
            self.pmtool.canMemberChangeLocalRoles(self.portal.sections))
        self.assert_(self.pmtool.canMemberChangeLocalRoles(
            self.portal.workspaces.members.member))
        self.assert_(self.pmtool.canMemberChangeLocalRoles(
            self.portal.workspaces.members.wsmanager))
        self.assert_(self.pmtool.canMemberChangeLocalRoles(
            self.portal.workspaces.members.semanager))
        self.logout()

    def test_MemberCanMemberChangeLocalRoles(self):

        # member can change them only in its hom folder
        
        self.login('member')
        self.assert_(not
            self.pmtool.canMemberChangeLocalRoles(self.portal.workspaces))
        self.assert_(not
            self.pmtool.canMemberChangeLocalRoles(self.portal.sections))
        self.assert_(self.pmtool.canMemberChangeLocalRoles(
            self.portal.workspaces.members.member))
        self.logout()

    def test_WSManagerCanMemberChangeLocalRoles(self):

        # ws manager can change them in the workspace areas and in
        # its home folder
        
        self.login('wsmanager')
        self.assert_(
            self.pmtool.canMemberChangeLocalRoles(self.portal.workspaces))
        self.assert_(not
            self.pmtool.canMemberChangeLocalRoles(self.portal.sections))
        self.assert_(self.pmtool.canMemberChangeLocalRoles(
            self.portal.workspaces.members.wsmanager))
        self.assert_(self.pmtool.canMemberChangeLocalRoles(
            self.portal.workspaces.members.semanager))
        self.logout()

    def test_SEManagerCanMemberChangeLocalRoles(self):
        
        # se manager can change them in the section areas and in
        # its home folder
        
        self.login('semanager')
        self.assert_(not
            self.pmtool.canMemberChangeLocalRoles(self.portal.workspaces))
        self.assert_(
            self.pmtool.canMemberChangeLocalRoles(self.portal.sections))
        self.assert_(self.pmtool.canMemberChangeLocalRoles(
            self.portal.workspaces.members.semanager))
        self.assert_(not
            self.pmtool.canMemberChangeLocalRoles(
            self.portal.workspaces.members.wsmanager))
        self.logout()
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMembershipTool))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
