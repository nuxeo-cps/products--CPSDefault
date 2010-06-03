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

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from Products.CPSCore.interfaces import ICPSSite
from Products.CPSCore.interfaces import ICPSProxy

class RoleView(BrowserView):

    def synthesis(self):
        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        obj = self.context
        return "Nothing for now"
