# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
""" CPS Default Init
"""

from Products.CMFCore.utils import ContentInit, ToolInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import AddPortalContent

import Portal
import Folder
import Dummy

import BoxesTool
import BaseBox
import TextBox
import TreeBox
import ContentBox
import ActionBox

contentClasses = (Folder.Folder, Dummy.Dummy,
                  BaseBox.BaseBox,
                  TextBox.TextBox, TreeBox.TreeBox,
                  ContentBox.ContentBox, ActionBox.ActionBox)

contentConstructors = (Folder.addFolder, Dummy.addDummy,
                       BaseBox.addBaseBox,
                       TextBox.addTextBox, TreeBox.addTreeBox,
                       ContentBox.addContentBox, ActionBox.addActionBox)

fti = (Folder.factory_type_information +
       Dummy.factory_type_information +
       BaseBox.factory_type_information +
       TextBox.factory_type_information +
       TreeBox.factory_type_information +
       ContentBox.factory_type_information +
       ActionBox.factory_type_information +
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
    context.registerClass(BoxesTool.BoxSlot,
                          permission='Manage Boxes',
                          visibility=None,
                          constructors=(BoxesTool.addBoxSlotForm,BoxesTool.addBoxSlot))
    return
