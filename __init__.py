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
import TextBox
import TreeBox
import ContentBox

contentClasses = (Folder.Folder, Dummy.Dummy,
                  TextBox.TextBox, TreeBox.TreeBox)
contentConstructors = (Folder.addFolder, Dummy.addDummy,
                       TextBox.addTextBox, TreeBox.addTreeBox,
                       ContentBox.addContentBox)

fti = (Folder.factory_type_information +
       Dummy.factory_type_information +
       TextBox.factory_type_information +
       TreeBox.factory_type_information +
       ContentBox.factory_type_information +       
       ()
       )

tools = (BoxesTool.BoxesTool,  # XXX this should be moved into CPSCore ?
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
    return
