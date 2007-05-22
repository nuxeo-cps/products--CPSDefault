# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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
"""CPS default permissions.

  - 'Modify Folder Properties' is used to have specific edit permissions
    on folder-like object modification (Sections, Workspace).

"""

from Products.CMFCore.permissions import setDefaultRoles
from Products.CPSUtil.integration import isProductPresent

ModifyFolderProperties = 'Modify Folder Properties'
setDefaultRoles(ModifyFolderProperties, ('Manager',))

if not isProductPresent('Products.ExternalEditor'):
    # we need to define it so that the rolemap import step can work
    setDefaultRoles('Use external editor', ('Manager',))

