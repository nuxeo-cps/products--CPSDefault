# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import AddPortalContent

import CPSSite

contentClasses = ( )
contentConstructors = ( )

fti = (
    ()
    )


registerDirectory('skins/templates', globals())
registerDirectory('skins/images', globals())

def initialize(registrar):
      registrar.registerClass(CPSSite.Sss3Site,
      constructors=(CPSSite.manage_addSss3SiteForm,
                    CPSSite.manage_addSss3Site,))
    return
    utils.ContentInit(
        'Sss3 Documents',
        content_types = contentClasses,
        permission = AddPortalContent,
        extra_constructors = contentConstructors,
        fti = fti,
        ).initialize(registrar)
