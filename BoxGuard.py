# -*- coding: iso-8859-15 -*-
# Copyright (c) 2003 Nuxeo SARL <http://nuxeo.com>
# Author Hervé Cauwelier <hc@nuxeo.com>
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
  BoxGuard
"""

from Globals import InitializeClass
from Products.PageTemplates.Expressions import getEngine
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.Guard import Guard

def createExpressionContext(sm, box, context):
    """Create a name space for TALES expressions.
       
    @param sm: SecurityManager instance
    @param box: Box instance
    @param context: Zope context (which object is being published)
    """
    portal = getToolByName(context, 'portal_url').getPortalObject()
    data = {
        'box': box,
        'here': context,
        'portal': portal,
        'request': getattr(context, 'REQUEST', None),
        'user': sm.getUser(),
        'nothing': None,
        }
    return getEngine().getContext(data)

class BoxGuard(Guard):
    """DCWorkflow Guard with a box-specific name space.
    """
    def check(self, sm, box, context):
        """Checks conditions in this guard.
        
        @param sm: SecurityManager instance
        @param box: Box instance
        @param context: Zope context (which object is being published)
        """
        pp = self.permissions
        if pp:
            found = 0
            for p in pp:
                if sm.checkPermission(p, box):
                    found = 1
                    break
            if not found:
                return 0
        roles = self.roles
        if roles:
            # Require at least one of the given roles.
            found = 0
            u_roles = sm.getUser().getRolesInContext(box)
            for role in roles:
                if role in u_roles:
                    found = 1
                    break
            if not found:
                return 0
        expr = self.expr
        if expr is not None:
            econtext = createExpressionContext(sm, box, context)
            res = expr(econtext)
            if not res:
                return 0
        return 1

InitializeClass(BoxGuard)
