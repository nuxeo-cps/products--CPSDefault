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

import MembershipTool
import CMFCalendarToolPatch

# Making sure that the ModuleSecurityInfo info statements of the utils
# module is taken into account.
import utils
import Portal
import Folder
import Dummy

# XXX Compatibility
from Products.CPSBoxes import BoxesTool
from Products.CPSBoxes import BaseBox
from Products.CPSBoxes import TextBox
from Products.CPSBoxes import TreeBox
from Products.CPSBoxes import ContentBox
from Products.CPSBoxes import ActionBox
from Products.CPSBoxes import ImageBox
from Products.CPSBoxes import FlashBox
from Products.CPSBoxes import EventCalendarBox
from Products.CPSBoxes import InternalLinksBox
from Products.CPSBoxes import DocRenderBox

contentClasses = (
    Folder.Folder,
    Dummy.Dummy,

    # XXX compatibility
    BaseBox.BaseBox,
    TextBox.TextBox,
    TreeBox.TreeBox,
    ContentBox.ContentBox,
    ActionBox.ActionBox,
    ImageBox.ImageBox,
    FlashBox.FlashBox,
    EventCalendarBox.EventCalendarBox,
    InternalLinksBox.InternalLinksBox,
    DocRenderBox.DocRenderBox,
    )

contentConstructors = (
    MembershipTool.addMembershipTool,
    Folder.addFolder,
    Dummy.addDummy,

    # XXX compatibility
    BaseBox.addBaseBox,
    TextBox.addTextBox,
    TreeBox.addTreeBox,
    ContentBox.addContentBox,
    ActionBox.addActionBox,
    ImageBox.addImageBox,
    FlashBox.addFlashBox,
    EventCalendarBox.addEventCalendarBox,
    InternalLinksBox.addInternalLinksBox,
    DocRenderBox.addDocRenderBox,
    )

fti = (Folder.factory_type_information +
       Dummy.factory_type_information +

       # XXX compatibility
       BaseBox.factory_type_information +
       TextBox.factory_type_information +
       TreeBox.factory_type_information +
       ContentBox.factory_type_information +
       ActionBox.factory_type_information +
       ImageBox.factory_type_information +
       FlashBox.factory_type_information +
       EventCalendarBox.factory_type_information +
       InternalLinksBox.factory_type_information +
       DocRenderBox.factory_type_information +
       ()
       )

registerDirectory('skins', globals())

tools = (
    MembershipTool.MembershipTool,
    BoxesTool.BoxesTool,
    )

def initialize(context):

    # XXX Compatibility alias (c.f : CPSBoxes)
    ToolInit(
        'CPS Default Tool',
        tools=tools,
        icon='tool.png',
        ).initialize(context)

    ContentInit('CPSDefault Documents',
                content_types=contentClasses,
                permission=AddPortalContent,
                extra_constructors=contentConstructors,
                fti=fti,
                ).initialize(context)

    context.registerClass(Portal.CPSDefaultSite,
                          constructors=(Portal.manage_addCPSDefaultSiteForm,
                                        Portal.manage_addCPSDefaultSite,))

    # XXX compatibility (c.f : CPSBoxes)
    context.registerClass(BoxesTool.BoxContainer,
                          permission='Add Box Container',
                          constructors=(BoxesTool.addBoxContainer,))

    if has_profile_registry:
        profile_registry.registerProfile('default',
                                         'CPS Default Site',
                                         'Profile for a default CPS site.',
                                         'profiles/default',
                                         'CPSDefault')
