# Copyright (c) 2010 Georges Racinet <georges@racinet.fr>
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

from Products.CMFCore.utils import getToolByName

try:

    from Products.CPSSkins.upgrade import *

    def cpsskins_used(portal):
        try:
            from Products.CPSSkins.PortalThemesTool import PortalThemesTool
        except ImportError:
            return False
        thmtool = getToolByName(portal, 'portal_themes', None)
        return isinstance(thmtool, PortalThemesTool)

except ImportError:

    def cpsskins_used(portal):
        return False

    def upgrade_342_343_flash_image(portal):
        """Placeholder so that zope.component can proceed."""
