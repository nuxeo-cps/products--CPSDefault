# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
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
""" Folder, which is both used for work and publication.
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent

from Products.CPSCore.CPSBase import CPSBaseFolder, CPSBase_adder


factory_type_information = (
    {'id': 'Folder',
     'title': 'portal_type_Folder_title',
     'description': 'portal_type_Folder_description',
     'content_icon': 'folder_icon.gif',
     'product': 'CPSDefault',
     'meta_type': 'Folder',
     'factory': 'addFolder',
     'immediate_view': 'folder_edit_form',
     'filter_content_types': 0,
     'allowed_content_types': (),
     'actions': ({'id': 'isproxytype',
                  'name': 'isproxytype',
                  'action': 'folder',
                  'permissions': ('',),
                  'visible': 0},
                 {'id': 'view',
                  'name': 'action_view',
                  'action': 'folder_view',
                  'permissions': (View,)},
                 {'id': 'contents',
                  'name': 'action_folder_contents',
                  'action': 'folder_contents',
                  'permissions': (ModifyPortalContent,)},
                 {'id': 'edit',
                  'name': 'action_edit',
                  'action': 'folder_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 {'id': 'metadata',
                  'name': 'action_metadata',
                  'action': 'metadata_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 {'id': 'localroles',
                  'name': 'action_local_roles',
                  'action': 'folder_localrole_form',
                  'permissions': ('Change permissions',)},
                 {'id': 'boxes',
                  'name': 'action_boxes',
                  'action': 'box_manage_form',
                  'permissions': (ModifyPortalContent,)},
                 )
     },
    )



class Folder(CPSBaseFolder):
    meta_type = 'Folder'
    portal_type = meta_type # To ease testing.

InitializeClass(Folder)


def addFolder(container, id, REQUEST=None, **kw):
    """Add a Folder."""
    ob = Folder(id, **kw)
    return CPSBase_adder(container, ob, REQUEST=REQUEST)
