# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
""" CPS Default Init
"""

from Products.CMFCore.utils import ContentInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import AddPortalContent

import Portal
import Folder
import Dummy

contentClasses = (Folder.Folder, Dummy.Dummy,)
contentConstructors = (Folder.addFolder, Dummy.addDummy,)

fti = (Folder.factory_type_information +
       Dummy.factory_type_information +
       ()
       )

registerDirectory('skins', globals())
registerDirectory('skins/images', globals())

def initialize(context):
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
