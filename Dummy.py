# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
""" A Dummy document
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent

from Products.NuxCPS3.CPSBase import CPSBaseDocument, CPSBase_adder


factory_type_information = (
                            {'id': 'Dummy',
                             'meta_type': 'Dummy',
                             'description': 'A dummy documents',
                             'icon': 'dummy_icon.gif',
                             'product': 'SSS3',
                             'factory': 'addDummy',
                             'immediate_view': 'metadata_edit_form',
                             # CPS attr
                             'title': 'Dummy title',
                             'actions': (
                                         {'id': 'view',
                                          'name': 'View',
                                          'action': 'dummy_view',
                                          'permissions': (View,)
                                          },
                                         {'id': 'edit',
                                          'name': 'Edit',
                                          'action': 'dummy_edit_form',
                                          'permissions': (ModifyPortalContent,)
                                           },
                                         {'id': 'metadata',
                                          'name': 'Metadata',
                                          'action': 'metadata_edit_form',
                                          'permissions': (ModifyPortalContent,)
                                          },
                                         # CPS actions
                                         {'id': 'isproxytype',
                                          'name': 'isproxytype',
                                          'action': 'document',
                                          'permissions': (None,),
                                          'visible': 0,
                                          },
                                         )
                             },
                            )

class Dummy(CPSBaseDocument):
    """ The simpliest CPS document with a body """
    meta_type = 'Dummy'
    portal_type = meta_type # to ease testing

    _properties = CPSBaseDocument._properties + (
                                               {'id': 'body',
                                                'type': 'text',
                                                'mode': 'w',
                                                'label': 'Body'
                                                }, 
                                               )
    body = ''
    
    def __init__(self, id, **kw):
        CPSBaseDocument.__init__(self, id, **kw)
    #EOC
    
InitializeClass(Dummy)


def addDummy(container, id, REQUEST=None, **kw):
    """ Add a Dummy Document """
    ob = Dummy(id, **kw)
    return CPSBase_adder(container, ob, REQUEST=REQUEST)

#EOF