# (C) Copyright 2010 AFUL <http://aful.org/>
# Authors:
# M.-A. Darche
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
"""Contains the view for role listing/synthesis audit page.
"""

from logging import getLogger

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from Products.CPSCore.interfaces import ICPSSite
from Products.CPSCore.interfaces import ICPSProxy

LOG_KEY = 'RoleView'

class RoleView(BrowserView):

    # TODO: Get those appropriately
    roles = [
        'WorkspaceManager',
        'WorkspaceMember',
        'WorkspaceReader',
        'SectionManager',
        'SectionMember',
        'SectionReader',
        ]

    def synthesis(self):
        print("context: %s" % self.context)
        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        mtool = portal.portal_membership
        context_rpath = utool.getRpath(self.context)
        print("context rpath: %s" % context_rpath)

        if not context_rpath:
            containers = [portal.workspaces, portal.sections]
        else:
            containers = [self.context]

        for container in containers:
            containers += self.findContainers(container)
        print("containers: %s" % containers)

        roles_struct_list = []
        for container in containers:
            roles_struct_list.append(self.getContainerRoles(container))
        return roles_struct_list

    def findContainers(self, container):
        containers = []
        for id, obj in container.objectItems():
            if id.startswith('.'):
                continue
            containers.append(obj)
            containers += self.findContainers(obj)
        return containers

    def getContainerRoles(self, container):
        logger = getLogger(LOG_KEY + '.synthesis')
        print("Working on %s\n\n" % container)
        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        mtool = portal.portal_membership
        folder_roles = {'rpath': utool.getRpath(container),
                        'roles': mtool.getCPSLocalRolesRender(container, self.roles,
                                                              None),
                        }
        print("folder_roles: %s\n\n" % folder_roles)
        return folder_roles
