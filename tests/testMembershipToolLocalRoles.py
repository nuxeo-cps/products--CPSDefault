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
"""
Test MembershipTool local roles management API.
"""

import unittest
from copy import deepcopy
from OFS.Folder import Folder

from Testing.ZopeTestCase import ZopeTestCase

from Products.CPSDefault.MembershipTool import MembershipTool
from Products.CPSCore.URLTool import URLTool
# rely on CPSUserFolder local roles management
from Products.CPSUserFolder.CPSUserFolder import CPSUserFolder
from Products.CPSUserFolder.TimeoutCache import resetAllCaches


_marker = object()
class FakeDirectory(Folder):
    def __init__(self, id, id_field, title_field, blank):
        Folder.__init__(self, id)
        self.id_field = id_field
        self.title_field = title_field
        self.blank = blank
        self.entries = {}
    def getEntry(self, id, default=_marker):
        res = self.entries.get(id, default)
        if res is _marker: raise KeyError(id)
        return res
    _getEntry = getEntry
    def createEntry(self, entry):
        new = deepcopy(self.blank)
        new.update(entry)
        self.entries[entry[self.id_field]] = new
    def editEntry(self, entry):
        self.entries[entry[self.id_field]].update(entry)
    def deleteEntry(self, id):
        del self.entries[id]
    def hasEntry(self, id):
        return self.entries.has_key(id)
    def listEntryIds(self):
        return self.entries.keys()

class FakeFolder(Folder):
    # folder with Workspace portal type so that relevant roles are found and no
    # reindexing is done
    def __init__(self, id):
        Folder.__init__(self, id)
        self.portal_type = 'Workspace'

    def reindexObjectSecurity(self):
        pass

class FakeRequest:

    def __init__(self):
        self._auth = 'clcert '

class TestMembershipToolLocalRoles(ZopeTestCase):

    # fixture
    def _setup(self):
        # portal, use 'foler' id cause 'portal' is used in other tests and
        # conflicts...
        self.app._setObject('folder', Folder('folder'))
        portal = self.portal = getattr(self.app, 'folder')
        # roles
        self.roles = [
            'WorkspaceManager',
            'WorkspaceMember',
            'WorkspaceReader',
            ]
        self.roles.sort()
        for role in ['Manager'] + self.roles:
            portal._addRole(role)
        # user folder and directories
        portal._setObject('acl_users', CPSUserFolder())
        dirtool = portal.portal_directories = Folder('portal_directories')
        dirtool.members = FakeDirectory(
            'members', 'uid', 'title',
            {'pw': 'secret',
             'roles': [],
             'groups': [],
             'sn': None,
             'title': '',
             })
        dirtool.groups = FakeDirectory(
            'groups', 'group', 'title', {'members': ()})
        uf = portal.acl_users
        uf.manage_changeProperties(
            users_dir='members',
            users_password_field='pw',
            users_roles_field='roles',
            users_groups_field='groups',
            )
        resetAllCaches()
        # manager
        uf.userFolderAddUser('manager', 'secret', ['Manager'], [])
        # login needs self.folder
        self.folder = portal
        self.login('manager')

    def afterSetUp(self):
        self.request = FakeRequest()
        # create mtool and utool
        portal = self.portal
        portal._setObject(URLTool.id, URLTool())
        portal._setObject(MembershipTool.id, MembershipTool())
        self.mtool = getattr(portal, MembershipTool.id)
        self.root = self.makeFolders()
        self.default_roles = self.setDefaultRoles()

    def beforeTearDown(self):
        del self.portal
        del self.roles
        del self.request
        del self.mtool
        del self.root
        del self.default_roles

    # helper methods

    def makeFolders(self):
        self.portal._setObject('root', FakeFolder('root'))
        root = getattr(self.portal, 'root')
        root.fold = FakeFolder('fold')
        root.fold.ob = FakeFolder('ob')
        root.fold.ob.subob = FakeFolder('subob')
        return root

    def setDefaultRoles(self):
        mtool = self.mtool
        root = self.root
        fold = root.fold
        ob = fold.ob
        mtool.setLocalRoles(root, ['someuser'], 'WorkspaceManager')
        mtool.setLocalGroupRoles(root, ['somegroup'], 'WorkspaceReader')
        mtool.setLocalRoles(fold, ['someuser'], 'WorkspaceMember')
        mtool.setLocalGroupRoles(ob, ['somegroup'], 'WorkspaceManager')
        default_roles = {
            'root': {
                'user:someuser': [{'url': 'root', 'roles': ['WorkspaceManager']},],
                'group:somegroup': [{'url': 'root', 'roles': ['WorkspaceReader']},],
                },
            'fold': {
                'user:someuser': [
                    {'url': 'root/fold', 'roles': ['WorkspaceMember']},
                    {'url': 'root', 'roles': ['WorkspaceManager']},
                    ],
                'group:somegroup': [
                    {'url': 'root', 'roles': ['WorkspaceReader']},
                    ],
                },
            'ob': {
                'user:someuser': [
                    {'url': 'root/fold', 'roles': ['WorkspaceMember']},
                    {'url': 'root', 'roles': ['WorkspaceManager']},
                    ],
                'group:somegroup': [
                    {'url': 'root/fold/ob', 'roles': ['WorkspaceManager']},
                    {'url': 'root', 'roles': ['WorkspaceReader']},
                    ],
                },
            }
        return default_roles

    # tests

    def test_getCPSCandidateLocalRoles(self):
        mtool = self.mtool
        root = self.root
        fold = root.fold
        ob = fold.ob
        roles = mtool.getCPSCandidateLocalRoles(root)
        roles.sort()
        self.assertEquals(roles, self.roles)

    def test_getCPSLocalRoles(self):
        mtool = self.mtool
        root = self.root
        fold = root.fold
        ob = fold.ob
        roles, blocked = mtool.getCPSLocalRoles(root)
        self.assertEquals(roles, self.default_roles['root'])
        self.assertEquals(blocked, 0)
        roles, blocked = mtool.getCPSLocalRoles(fold)
        self.assertEquals(roles, self.default_roles['fold'])
        self.assertEquals(blocked, 0)
        roles, blocked = mtool.getCPSLocalRoles(ob)
        self.assertEquals(roles, self.default_roles['ob'])
        self.assertEquals(blocked, 0)

    def test_folderLocalRoleBlock(self):
        mtool = self.mtool
        root = self.root
        fold = root.fold
        ob = fold.ob

        self.assertEquals(
            self.portal.acl_users.mergedLocalRoles(root, withgroups=1),
            {'user:manager': ['Owner'],
             'user:someuser': ['WorkspaceManager'],
             'group:somegroup': ['WorkspaceReader']})
        self.assertEquals(
            self.portal.acl_users.mergedLocalRoles(fold, withgroups=1),
            {'user:manager': ['Owner'],
             'user:someuser': ['WorkspaceMember', 'WorkspaceManager'],
             'group:somegroup': ['WorkspaceReader']})
        self.assertEquals(
            self.portal.acl_users.mergedLocalRoles(ob, withgroups=1),
            {'user:manager': ['Owner'],
             'user:someuser': ['WorkspaceMember', 'WorkspaceManager'],
             'group:somegroup': ['WorkspaceManager', 'WorkspaceReader']})

        # block roles on fold
        mtool.folderLocalRoleBlock(fold, lr_block='yep')

        self.assertEquals(
            self.portal.acl_users.mergedLocalRoles(root, withgroups=1),
            {'user:manager': ['Owner'],
             'user:someuser': ['WorkspaceManager'],
             'group:somegroup': ['WorkspaceReader']})
        self.assertEquals(
            self.portal.acl_users.mergedLocalRoles(fold, withgroups=1),
            {'user:someuser': ['WorkspaceMember']})
        self.assertEquals(
            self.portal.acl_users.mergedLocalRoles(ob, withgroups=1),
            {'user:someuser': ['WorkspaceMember'],
             'group:somegroup': ['WorkspaceManager']})

        # unblock roles on fold
        mtool.folderLocalRoleBlock(fold, lr_unblock='yep')

        # back to where we started?
        self.assertEquals(
            self.portal.acl_users.mergedLocalRoles(root, withgroups=1),
            {'user:manager': ['Owner'],
             'user:someuser': ['WorkspaceManager'],
             'group:somegroup': ['WorkspaceReader']})
        self.assertEquals(
            self.portal.acl_users.mergedLocalRoles(fold, withgroups=1),
            {'user:manager': ['Owner'],
             'user:someuser': ['WorkspaceMember', 'WorkspaceManager'],
             'group:somegroup': ['WorkspaceReader']})
        self.assertEquals(
            self.portal.acl_users.mergedLocalRoles(ob, withgroups=1),
            {'user:manager': ['Owner'],
             'user:someuser': ['WorkspaceMember', 'WorkspaceManager'],
             'group:somegroup': ['WorkspaceManager', 'WorkspaceReader']})


    def test_getCPSLocalRoles_with_blocking(self):
        mtool = self.mtool
        root = self.root
        fold = root.fold
        ob = fold.ob

        # block roles on fold
        mtool.folderLocalRoleBlock(fold, lr_block='yes')

        roles, blocked = mtool.getCPSLocalRoles(root)
        self.assertEquals(roles, self.default_roles['root'])
        self.assertEquals(blocked, 0)
        roles, blocked = mtool.getCPSLocalRoles(fold)
        self.assertEquals(roles, {
                'user:someuser': [
                    {'url': 'root/fold', 'roles': ['WorkspaceMember']},
                    ],
                })
        self.assertEquals(blocked, 1)
        roles, blocked = mtool.getCPSLocalRoles(ob)
        self.assertEquals(roles, {
                'user:someuser': [
                    {'url': 'root/fold', 'roles': ['WorkspaceMember']},
                    ],
                'group:somegroup': [
                    {'url': 'root/fold/ob', 'roles': ['WorkspaceManager']},
                    ],
                })
        # non regression test for #923
        self.assertEquals(blocked, 0)

    def test_getCPSLocalRoles_with_several_blockings(self):
        mtool = self.mtool
        root = self.root
        fold = root.fold
        ob = fold.ob

        # block roles on fold and ob
        mtool.folderLocalRoleBlock(fold, lr_block='yes')
        mtool.folderLocalRoleBlock(ob, lr_block='yes')

        roles, blocked = mtool.getCPSLocalRoles(root)
        self.assertEquals(roles, self.default_roles['root'])
        self.assertEquals(blocked, 0)
        roles, blocked = mtool.getCPSLocalRoles(fold)
        self.assertEquals(roles, {
                'user:someuser': [
                    {'url': 'root/fold', 'roles': ['WorkspaceMember']},
                    ],
                })
        self.assertEquals(blocked, 1)
        roles, blocked = mtool.getCPSLocalRoles(ob)
        self.assertEquals(roles, {
                'group:somegroup': [
                    {'url': 'root/fold/ob', 'roles': ['WorkspaceManager']},
                    ],
                })
        self.assertEquals(blocked, 1)

        # unblock roles on ob and block it on lower level
        subob = ob.subob
        mtool.folderLocalRoleBlock(ob, lr_unblock='yes')
        mtool.folderLocalRoleBlock(subob, lr_block='yes')

        roles, blocked = mtool.getCPSLocalRoles(root)
        self.assertEquals(roles, self.default_roles['root'])
        self.assertEquals(blocked, 0)
        roles, blocked = mtool.getCPSLocalRoles(fold)
        self.assertEquals(roles, {
                'user:someuser': [
                    {'url': 'root/fold', 'roles': ['WorkspaceMember']},
                    ],
                })
        self.assertEquals(blocked, 1)
        roles, blocked = mtool.getCPSLocalRoles(ob)
        self.assertEquals(roles, {
                'user:someuser': [
                    {'url': 'root/fold', 'roles': ['WorkspaceMember']},
                    ],
                'group:somegroup': [
                    {'url': 'root/fold/ob', 'roles': ['WorkspaceManager']},
                    ],
                })
        self.assertEquals(blocked, 0)
        roles, blocked = mtool.getCPSLocalRoles(subob)
        self.assertEquals(roles, {})
        self.assertEquals(blocked, 1)

    def test_getCPSLocalRolesRender(self):
        mtool = self.mtool
        root = self.root
        fold = root.fold
        ob = fold.ob

        # on root
        res = mtool.getCPSLocalRolesRender(root, self.roles)
        sorted_members = ['user:someuser']
        self.assertEquals(res[0], sorted_members)
        # members
        members = {
            'user:someuser': {
                'title': 'someuser',
                'role_input_name': 'role_user_someuser',
                'inherited_roles': {},
                'has_local_roles': 1,
                'here_roles': {'WorkspaceManager': {'here': 1,
                                                    'inherited': 0},
                               'WorkspaceMember': {'here': 0,
                                                   'inherited': 0},
                               'WorkspaceReader': {'here': 0,
                                                   'inherited': 0},
                               },
                },
            }
        self.assertEquals(res[1], members)
        # groups
        sorted_groups = ['group:somegroup']
        self.assertEquals(res[2], sorted_groups)
        groups = {
            'group:somegroup': {
                'title': 'somegroup',
                'role_input_name': 'role_group_somegroup',
                'inherited_roles': {},
                'has_local_roles': 1,
                'here_roles': {'WorkspaceManager': {'here': 0,
                                                    'inherited': 0},
                               'WorkspaceMember': {'here': 0,
                                                   'inherited': 0},
                               'WorkspaceReader': {'here': 1,
                                                   'inherited': 0},
                               },
                },
            }
        self.assertEquals(res[3], groups)
        # blocking
        self.assertEquals(res[4], 0)

        # on folder
        res = mtool.getCPSLocalRolesRender(fold, self.roles)
        self.assertEquals(res[0], sorted_members)
        # members
        members = {
            'user:someuser': {
                'title': 'someuser',
                'role_input_name': 'role_user_someuser',
                'inherited_roles': {'WorkspaceManager': ['root']},
                'has_local_roles': 1,
                'here_roles': {'WorkspaceManager': {'here': 0,
                                                    'inherited': 1},
                               'WorkspaceMember': {'here': 1,
                                                   'inherited': 0},
                               'WorkspaceReader': {'here': 0,
                                                   'inherited': 0},
                               },
                },
            }
        self.assertEquals(res[1], members)
        # groups
        self.assertEquals(res[2], sorted_groups)
        groups = {
            'group:somegroup': {
                'title': 'somegroup',
                'role_input_name': 'role_group_somegroup',
                'inherited_roles': {'WorkspaceReader': ['root']},
                'has_local_roles': 0,
                'here_roles': {'WorkspaceManager': {'here': 0,
                                                    'inherited': 0},
                               'WorkspaceMember': {'here': 0,
                                                   'inherited': 0},
                               'WorkspaceReader': {'here': 0,
                                                   'inherited': 1},
                               },
                },
            }
        self.assertEquals(res[3], groups)
        # blocking
        self.assertEquals(res[4], 0)

        # on object
        res = mtool.getCPSLocalRolesRender(ob, self.roles)
        self.assertEquals(res[0], sorted_members)
        # members
        members = {
            'user:someuser': {
                'title': 'someuser',
                'role_input_name': 'role_user_someuser',
                'inherited_roles': {
                    'WorkspaceManager': ['root'],
                    'WorkspaceMember': ['root/fold'],
                    },
                'has_local_roles': 0,
                'here_roles': {'WorkspaceManager': {'here': 0,
                                                    'inherited': 1},
                               'WorkspaceMember': {'here': 0,
                                                   'inherited': 1},
                               'WorkspaceReader': {'here': 0,
                                                   'inherited': 0},
                               },
                },
            }
        self.assertEquals(res[1], members)
        # groups
        self.assertEquals(res[2], sorted_groups)
        groups = {
            'group:somegroup': {
                'title': 'somegroup',
                'role_input_name': 'role_group_somegroup',
                'inherited_roles': {'WorkspaceReader': ['root']},
                'has_local_roles': 1,
                'here_roles': {'WorkspaceManager': {'here': 1,
                                                    'inherited': 0},
                               'WorkspaceMember': {'here': 0,
                                                   'inherited': 0},
                               'WorkspaceReader': {'here': 0,
                                                   'inherited': 1},
                               },
                },
            }
        self.assertEquals(res[3], groups)
        # blocking
        self.assertEquals(res[4], 0)

        # test on ob with filtered role -> same result without somegroup
        res = mtool.getCPSLocalRolesRender(ob, self.roles,
                                           'WorkspaceMember')
        self.assertEquals(res[0], ['user:someuser'])
        members = {
            'user:someuser': members['user:someuser'],
            }
        self.assertEquals(res[1], members)
        # groups
        self.assertEquals(res[2], [])
        self.assertEquals(res[3], {})
        # blocking
        self.assertEquals(res[4], 0)


    def test_getCPSLocalRolesRender_with_blocking(self):
        mtool = self.mtool
        root = self.root
        fold = root.fold
        ob = fold.ob

        # block local roles
        mtool.folderLocalRoleBlock(fold, lr_block='yes')

        res = mtool.getCPSLocalRolesRender(root, self.roles)
        sorted_members = ['user:someuser']
        self.assertEquals(res[0], sorted_members)
        # members
        members = {
            'user:someuser': {
                'title': 'someuser',
                'role_input_name': 'role_user_someuser',
                'inherited_roles': {},
                'has_local_roles': 1,
                'here_roles': {'WorkspaceManager': {'here': 1,
                                                    'inherited': 0},
                               'WorkspaceMember': {'here': 0,
                                                   'inherited': 0},
                               'WorkspaceReader': {'here': 0,
                                                   'inherited': 0},
                               },
                },
            }
        self.assertEquals(res[1], members)
        # groups
        sorted_groups = ['group:somegroup']
        self.assertEquals(res[2], sorted_groups)
        groups = {
            'group:somegroup': {
                'title': 'somegroup',
                'role_input_name': 'role_group_somegroup',
                'inherited_roles': {},
                'has_local_roles': 1,
                'here_roles': {'WorkspaceManager': {'here': 0,
                                                    'inherited': 0},
                               'WorkspaceMember': {'here': 0,
                                                   'inherited': 0},
                               'WorkspaceReader': {'here': 1,
                                                   'inherited': 0},
                               },
                },
            }
        self.assertEquals(res[3], groups)
        # blocking
        self.assertEquals(res[4], 0)

        # on folder
        res = mtool.getCPSLocalRolesRender(fold, self.roles)
        self.assertEquals(res[0], ['user:someuser'])
        # members
        members = {
            'user:someuser': {
                'title': 'someuser',
                'role_input_name': 'role_user_someuser',
                'inherited_roles': {},
                'has_local_roles': 1,
                'here_roles': {'WorkspaceManager': {'here': 0,
                                                    'inherited': 0},
                               'WorkspaceMember': {'here': 1,
                                                   'inherited': 0},
                               'WorkspaceReader': {'here': 0,
                                                   'inherited': 0},
                               },
                },
            }
        self.assertEquals(res[1], members)
        # groups
        self.assertEquals(res[2], [])
        self.assertEquals(res[3], {})
        # blocking
        self.assertEquals(res[4], 1)

        # on object
        res = mtool.getCPSLocalRolesRender(ob, self.roles)
        self.assertEquals(res[0], sorted_members)
        # members
        members = {
            'user:someuser': {
                'title': 'someuser',
                'role_input_name': 'role_user_someuser',
                'inherited_roles': {
                    'WorkspaceMember': ['root/fold'],
                    },
                'has_local_roles': 0,
                'here_roles': {'WorkspaceManager': {'here': 0,
                                                    'inherited': 0},
                               'WorkspaceMember': {'here': 0,
                                                   'inherited': 1},
                               'WorkspaceReader': {'here': 0,
                                                   'inherited': 0},
                               },
                },
            }
        self.assertEquals(res[1], members)
        # groups
        self.assertEquals(res[2], sorted_groups)
        groups = {
            'group:somegroup': {
                'title': 'somegroup',
                'role_input_name': 'role_group_somegroup',
                'inherited_roles': {},
                'has_local_roles': 1,
                'here_roles': {'WorkspaceManager': {'here': 1,
                                                    'inherited': 0},
                               'WorkspaceMember': {'here': 0,
                                                   'inherited': 0},
                               'WorkspaceReader': {'here': 0,
                                                   'inherited': 0},
                               },
                },
            }
        self.assertEquals(res[3], groups)
        # blocking
        self.assertEquals(res[4], 0)

        # test on ob with filtered role WorkspaceMember
        res = mtool.getCPSLocalRolesRender(ob, self.roles,
                                           'WorkspaceMember')
        self.assertEquals(res[0], sorted_members)
        self.assertEquals(res[1], members)
        # groups
        self.assertEquals(res[2], [])
        self.assertEquals(res[3], {})
        # blocking
        self.assertEquals(res[4], 0)

        # test on ob with filtered role WorkspaceManager
        res = mtool.getCPSLocalRolesRender(ob, self.roles,
                                           'WorkspaceManager')
        self.assertEquals(res[0], [])
        self.assertEquals(res[1], {})
        # groups
        self.assertEquals(res[2], sorted_groups)
        self.assertEquals(res[3], groups)
        # blocking
        self.assertEquals(res[4], 0)

        # test on ob with filtered role WorkspaceReader
        res = mtool.getCPSLocalRolesRender(ob, self.roles,
                                           'WorkspaceReader')
        self.assertEquals(res[0], [])
        self.assertEquals(res[1], {})
        # groups
        self.assertEquals(res[2], [])
        self.assertEquals(res[3], {})
        # blocking
        self.assertEquals(res[4], 0)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestMembershipToolLocalRoles),
        ))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
