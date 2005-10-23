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

from AccessControl import Unauthorized

import CPSDefaultTestCase
from Testing.ZopeTestCase import user_name

class TestMembershipTool(CPSDefaultTestCase.CPSDefaultTestCase):
    login_id = 'manager'

    def afterSetUp(self):
        self.login(self.login_id)
        self.pmtool = self.portal.portal_membership

        members = self.portal.portal_directories.members
        members.createEntry({'id': 'member', 'givenName' : 'Foo',
                             'sn': 'Bar', 'roles': ['Member']})
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

    def test_getFullnameFromIdRestricted(self):

        # Should fail because called from restricted code.
        self.assertRaises(Unauthorized, self.pmtool.getFullnameFromId,
                          'manager', REQUEST={})


    def test_getFullnameFromId(self):

        # test env

        members = self.portal.portal_directories.members
        fullname = members._getEntry('member')[members.title_field]
        self.assertEqual(fullname, 'Foo Bar')

        # Found it
        self.assertEqual(self.pmtool.getFullnameFromId('member'), 'Foo Bar')

        # Found it but no fullname so its the user id
        self.assertEqual(self.pmtool.getFullnameFromId('semanager'),
                         'semanager')

        # Use doesn't exsist -> return the id given as parameter
        self.assertEqual(self.pmtool.getFullnameFromId('fakeone'), 'fakeone')

    # non regression test for #492
    def test_anonymousGroupRoles(self):
        mtool = self.pmtool
        ws = self.portal.workspaces.members
        uf = self.portal.acl_users

        # test local roles before changes
        self.assertEquals(uf.mergedLocalRoles(ws, withgroups=1), {
            # duplicated role -> bug in CPSUserFolder ?
            'user:CPSTestCase': ['Owner', 'Owner', 'Owner'],
            'user:member': ['WorkspaceReader'],
            'user:wsmanager': ['WorkspaceManager'],
            })

        mtool.folderLocalRoleBlock(ws, lr_block='yes')
        # add a local role for anonymous users
        mtool.setLocalGroupRoles(ws, ('role:Anonymous',), 'WorkspaceMember')

        # check changes were effective
        self.assertEquals(uf.mergedLocalRoles(ws, withgroups=1), {
            'user:CPSTestCase': ['Owner'],
            'group:role:Anonymous': ['WorkspaceMember'],
            })

        # remove local role set to anonymous users
        ws.folder_localrole_edit(delete_ids=['group:role:Anonymous'])

        # check local roles are still blocked
        self.assertEquals(uf.mergedLocalRoles(ws, withgroups=1), {
            'user:CPSTestCase': ['Owner'],
            })

    def test_getCPSLocalRoles(self):

        # what are the local roles in sections ?
        roles = self.pmtool.getCPSLocalRoles(self.portal.sections)
        wanted = ({'user:member': [{'url': 'sections',
                                    'roles': ['SectionReader']
                                   }],
                   'user:semanager': [{'url': 'sections',
                                       'roles': ['SectionManager']
                                       }]}, 0)

        self.assertEquals(roles, wanted)

        # what are the local roles in workspaces ?
        roles = self.pmtool.getCPSLocalRoles(self.portal.workspaces)
        wanted = ({'user:member': [{'url': 'workspaces',
                                    'roles': ['WorkspaceReader']
                                    }],
                   'user:wsmanager': [{'url': 'workspaces',
                                       'roles': ['WorkspaceManager']
                                       }]}, 0)

        self.assertEquals(roles, wanted)

    def test_getCPSCandidateLocalRoles(self):

        # what are the local roles in sections ?
        roles = self.pmtool.getCPSCandidateLocalRoles(self.portal.sections)
        roles.sort()
        wanted = ['SectionManager', 'SectionReader', 'SectionReviewer']
        self.assertEquals(roles, wanted)

        # what are the local roles in workspaces ?
        roles = self.pmtool.getCPSCandidateLocalRoles(self.portal.workspaces)
        roles.sort()
        wanted = ['WorkspaceManager', 'WorkspaceMember', 'WorkspaceReader']
        self.assertEquals(roles, wanted)

    def test_getCPSLocalRolesRender(self):

        # what are the local roles in sections ?
        roles = self.pmtool.getCPSLocalRolesRender(self.portal.sections,
                                                   ['SectionManager'])
        wanted = (['user:semanager'],
                  {'user:semanager': {'role_input_name':
                  'role_user_semanager', 'inherited_roles': {},
                  'has_local_roles': 1, 'here_roles': {'SectionManager':
                  {'here': 1, 'inherited': 0}}, 'title': 'semanager'}},
                  [], {}, 0)

        self.assertEquals(roles, wanted)

        # what are the local roles in workspaces ?
        roles = self.pmtool.getCPSLocalRolesRender(self.portal.workspaces,
                                                   ['WorkspaceReader'])
        wanted = (['user:member'], {'user:member': {'role_input_name':
                  'role_user_member', 'inherited_roles': {},
                  'has_local_roles': 1, 'here_roles': {'WorkspaceReader':
                  {'here': 1, 'inherited': 0}}, 'title': 'Foo Bar'}}, [],
                  {}, 0)

        self.assertEquals(roles, wanted)

    # XXX AT: deactivated, I dont get what's tested (see comments below) + need
    # to check that tests in testMembershipToolLocalRoles reproduce the use
    # case
    def XXXtest_getLocalRolesTwoBlockedLevels(self):

        # let's check the ws root
        roles = self.pmtool.getCPSLocalRoles(self.portal.workspaces)

        wanted = ({'user:member': [{'url': 'workspaces',
                  'roles': ['WorkspaceReader']}], 'user:wsmanager':
                  [{'url': 'workspaces', 'roles':
                  ['WorkspaceManager']}]}, 0)

        self.assertEquals(roles, wanted)

        # let's block local roles on workspaces.members
        # then append anonymous as worspace manager
        self.pmtool.folderLocalRoleBlock(obj=self.portal.workspaces.members,
                                         lr_block='yup')
        # XXX AT: what's anonymous? group of anonymous users? if so, let's use
        # setLocalGroupRoles with 'role:Anonymous'. If it's a user named
        # 'Anonymous', let's use 'Anonymous' instead of 'user:Anonymous', but
        # anyway it's confusing.
        self.pmtool.setLocalRoles(obj=self.portal.workspaces.members,
                                  member_ids=['user:Anonymous'],
                                  member_role='WorkspaceManager')

        # let's check if it worked
        roles = self.pmtool.getCPSLocalRoles(self.portal.workspaces.members)

        # XXX AT: roles are blocked at the workspaces.members level => we
        # shouldn't get roles for 'user:member' and 'user:wsmanager' so the
        # assertion is hiding a bug
        wanted = ({'user:member': [{'url': 'workspaces', 'roles':
                  ['WorkspaceReader']}], 'user:user:Anonymous':
                  [{'url': 'workspaces/members', 'roles': ['WorkspaceManager']}],
                  'user:wsmanager': [{'url': 'workspaces',
                  'roles': ['WorkspaceManager']}]}, 1)

        self.assertEquals(roles, wanted)

        # now let's see what we have in workspaces.members.wsmanager
        # let's unblock roles there, again, and add members
        current_folder = self.portal.workspaces.members.wsmanager

        self.pmtool.folderLocalRoleBlock(obj=current_folder,
                                         lr_unblock='yup')

        self.pmtool.setLocalRoles(obj=current_folder,
                                  member_ids=['user:member'],
                                  member_role='WorkspaceManager')

        roles = self.pmtool.getCPSLocalRoles(current_folder)

        # XXX AT: roles are set for 'user:user:member', 'user:member' and
        # 'user:user:Anonymous'... 'user:member' and 'group:role:Anonymous'
        # should be tested instead (?)
        wanted = ({'user:user:member': [{'url': 'workspaces/members/wsmanager',
                 'roles': ['WorkspaceManager']}], 'user:member': [{'url':
                 'workspaces', 'roles': ['WorkspaceReader']}], 'user:wsmanager':
                 [{'url': 'workspaces/members/wsmanager', 'roles':
                 ['WorkspaceManager']}, {'url': 'workspaces', 'roles':
                 ['WorkspaceManager']}], 'user:user:Anonymous': [{'url':
                 'workspaces/members', 'roles': ['WorkspaceManager']}]}, 0)

        self.assertEquals(roles, wanted)

        # the upper folder should'nt change
        roles = self.pmtool.getCPSLocalRoles(self.portal.workspaces.members)

        wanted = ({'user:member': [{'url': 'workspaces', 'roles':
                  ['WorkspaceReader']}], 'user:user:Anonymous':
                  [{'url': 'workspaces/members', 'roles': ['WorkspaceManager']}],
                  'user:wsmanager': [{'url': 'workspaces',
                  'roles': ['WorkspaceManager']}]}, 1)

        self.assertEquals(roles, wanted)

        # let's block roles there, now, again, and add members
        current_folder = self.portal.workspaces.members.wsmanager

        self.pmtool.folderLocalRoleBlock(obj=current_folder,
                                         lr_block='yup')

        self.pmtool.setLocalRoles(obj=current_folder,
                                  member_ids=['user:member'],
                                  member_role='WorkspaceManager')

        roles = self.pmtool.getCPSLocalRoles(current_folder)

        wanted = ({'user:user:member': [{'url': 'workspaces/members/wsmanager',
                  'roles': ['WorkspaceManager']}], 'user:member': [{'url':
                  'workspaces', 'roles': ['WorkspaceReader']}], 'user:wsmanager':
                  [{'url': 'workspaces/members/wsmanager', 'roles':
                   ['WorkspaceManager']}, {'url': 'workspaces', 'roles':
                   ['WorkspaceManager']}], 'user:user:Anonymous':
                   [{'url': 'workspaces/members', 'roles': ['WorkspaceManager']}]}, 1)

        self.assertEquals(roles, wanted)

        # the upper folder should'nt change
        roles = self.pmtool.getCPSLocalRoles(self.portal.workspaces.members)

        wanted = ({'user:member': [{'url': 'workspaces', 'roles':
                  ['WorkspaceReader']}], 'user:user:Anonymous':
                  [{'url': 'workspaces/members', 'roles': ['WorkspaceManager']}],
                  'user:wsmanager': [{'url': 'workspaces',
                  'roles': ['WorkspaceManager']}]}, 1)

        self.assertEquals(roles, wanted)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMembershipTool))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
