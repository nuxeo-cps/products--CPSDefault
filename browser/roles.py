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

    def __init__(self, *args, **kwargs):
        BrowserView.__init__(self, *args, **kwargs)
        self.utool = getToolByName(self.context, 'portal_url')
        self.portal = self.utool.getPortalObject()
        self.mtool = self.portal.portal_membership

    def synthesis(self):
        #print("context: %s" % self.context)
        context_rpath = self.utool.getRpath(self.context)
        #print("context rpath: %s" % context_rpath)

        if not context_rpath:
            roots = [self.portal.workspaces, self.portal.sections]
        else:
            roots = [self.context]

        containers = []
        for container in roots:
            containers.append(container)
            #print("container: %s" % container)
            containers += self.findContainers(container)
        #print("containers: %s" % containers)

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
        #print("Working on %s\n\n" % container)
        candidate_roles = container.getCPSCandidateLocalRoles()
        folder_roles = {'rpath': self.utool.getRpath(container),
                        'candidate_roles': candidate_roles,
                        'cpslr': self.mtool.getCPSLocalRolesRender(container,
                                                              candidate_roles,
                                                              None),
                        }
        #print("folder_roles: %s\n\n" % folder_roles)
        return folder_roles
