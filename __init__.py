# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
from Products.CMFCore.utils import ContentInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import AddPortalContent

import CPSSite
import Dummy

contentClasses = (Dummy.Dummy,)
contentConstructors = (Dummy.addDummy,)

fti = ( Dummy.factory_type_information +
        ()
        )


registerDirectory('skins', globals())
registerDirectory('skins/images', globals())

def initialize(context):
    ContentInit('Sss3 Documents',
                content_types = contentClasses,
                permission = AddPortalContent,
                extra_constructors = contentConstructors,
                fti = fti,
                ).initialize(context)
    context.registerClass(CPSSite.Sss3Site,
                          constructors=(CPSSite.manage_addSss3SiteForm,
                                        CPSSite.manage_addSss3Site,))
    return
