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
"""CPS Folder, which is both used for work and publication.
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent, AddPortalContent

from Products.NuxCPS3.CPSBase import CPSBaseFolder, CPSBase_adder


factory_type_information = (
    {'id': 'CPS Folder',
     'description': 'A container for documents.',
     'title': '',
     'content_icon': 'folder_icon.gif',
     'product': 'NuxCPS3',
     'meta_type': 'CPS Folder',
     'factory': 'addCPSFolder',
     'immediate_view': 'folder_contents',
     'filter_content_types': 0,
     'allowed_content_types': (),
     'actions': ({'id': 'isproxytype',
                  'name': 'isproxytype',
                  'action': 'folder',
                  'permissions': ('',),
                  'visible': 0},
                 {'id': 'create',
                  'name': 'Create',
                  'action': 'cpsfolder_create',
                  'permissions': ('',),
                  'visible': 0},
                 {'id': 'view',
                  'name': 'View',
                  'action': 'folder_contents',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'Edit',
                  'action': 'cpsfolder_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 {'id': 'metadata_edit',
                  'name': 'Edit',
                  'action': 'cpsfolder_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 {'id': 'localroles',
                  'name': 'Gestion des droits',
                  'action': 'cpsfolder_localroles_form',
                  'permissions': (ModifyPortalContent,)},
                 {'id': 'folder_contents',
                  'name': 'Contenu',
                  'action': 'cpsfolder_contents',
                  'category': 'folder',
                  'permissions': (ModifyPortalContent,)},
                 {'id': 'workflows',
                  'name': 'Workflows',
                  'action': 'cpsfolder_workflows',
                  'permissions': (ModifyPortalContent,)},
                 ),
     },
    )


class CPSFolder(CPSBaseFolder):
    meta_type = 'CPS Folder'
    portal_type = meta_type # To ease testing.

InitializeClass(CPSFolder)


def addCPSFolder(container, id, REQUEST=None, **kw):
    """Add a CPS Folder."""
    ob = CPSFolder(id, **kw)
    return CPSBase_adder(container, ob, REQUEST=REQUEST)
