# Copyright (c) 2003 Nuxeo SARL <http://nuxeo.com>
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
""" CPS Default Init
"""

from Products.CMFCore.utils import ContentInit, ToolInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.permissions import AddPortalContent
try:
    from Products.CMFSetup import profile_registry
    has_profile_registry = True
except ImportError:
    has_profile_registry = False

import CMFCalendarToolPatch

# Making sure that the ModuleSecurityInfo info statements of the utils
# module is taken into account.

import utils
import Portal
import Folder
import Dummy

# XXX Compatibility
import BoxesTool

contentClasses = (
    Folder.Folder,
    Dummy.Dummy,
    )

contentConstructors = (
    Folder.addFolder,
    Dummy.addDummy,
    )

fti = (Folder.factory_type_information +
       Dummy.factory_type_information +
       ()
       )

registerDirectory('skins', globals())

tools = (
    BoxesTool.BoxesTool,  
    )

def initialize(context):

    # XXX Compatibility alias (c.f : CPSBoxes)
    ToolInit(
        'CPS Default Tool',
        tools = tools,
        product_name = 'CPSDefault',
        icon = 'tool.png',
        ).initialize(context)

    ContentInit('CPSDefault Documents',
                content_types = contentClasses,
                permission = AddPortalContent,
                extra_constructors = contentConstructors,
                fti = fti,
                ).initialize(context)

    context.registerClass(Portal.CPSDefaultSite,
                          constructors=(Portal.manage_addCPSDefaultSiteForm,
                                        Portal.manage_addCPSDefaultSite,))

    # XXX compatibility (c.f : CPSBoxes)
    context.registerClass(BoxesTool.BoxContainer,
                          permission='Add Box Container',
                          constructors=(BoxesTool.addBoxContainer,))

