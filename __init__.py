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
from Products.CMFCore.CMFCorePermissions import AddPortalContent

import CMFCalendarToolPatch

import Portal
import Folder
import Dummy

import BoxesTool
import BaseBox
import TextBox
import TreeBox
import ContentBox
import ActionBox
import ImageBox
import FlashBox

contentClasses = (Folder.Folder, Dummy.Dummy,
                  BaseBox.BaseBox,
                  TextBox.TextBox, TreeBox.TreeBox,
                  ContentBox.ContentBox, ActionBox.ActionBox,
                  ImageBox.ImageBox,FlashBox.FlashBox,)

contentConstructors = (Folder.addFolder, Dummy.addDummy,
                       BaseBox.addBaseBox,
                       TextBox.addTextBox, TreeBox.addTreeBox,
                       ContentBox.addContentBox, ActionBox.addActionBox,
                       ImageBox.addImageBox,FlashBox.addFlashBox,)

fti = (Folder.factory_type_information +
       Dummy.factory_type_information +
       BaseBox.factory_type_information +
       TextBox.factory_type_information +
       TreeBox.factory_type_information +
       ContentBox.factory_type_information +
       ActionBox.factory_type_information +
       ImageBox.factory_type_information +
       FlashBox.factory_type_information +
       ()
       )

tools = (BoxesTool.BoxesTool,  # XXX this should move to CPSCore ?
         )

registerDirectory('skins', globals())

def initialize(context):
    ToolInit(
        'CPS Boxes Tool',
        tools = tools,
        product_name = 'CPSDefault',
        icon = 'tool.gif',
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
    context.registerClass(BoxesTool.BoxContainer,
                          permission='Add Box Container',
                          constructors=(BoxesTool.addBoxContainer,))
    return
