# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
""" A Dummy document
"""

from Globals import InitializeClass

from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent

from Products.CPSCore.CPSBase import CPSBaseDocument, CPSBase_adder


factory_type_information = (
                            {'id': 'Dummy',
                             'meta_type': 'Dummy',
                             'title': 'portal_type_Dummy_title',
                             'description': 'portal_type_Dummy_description',
                             'icon': 'dummy_icon.gif',
                             'product': 'CPSDefault',
                             'factory': 'addDummy',
                             'immediate_view': 'metadata_edit_form',
                             # CPS attr
                             'actions': (
                                         {'id': 'view',
                                          'name': 'action_view',
                                          'action': 'dummy_view',
                                          'permissions': (View,)
                                          },
                                         {'id': 'edit',
                                          'name': 'action_edit',
                                          'action': 'dummy_edit_form',
                                          'permissions': (ModifyPortalContent,)
                                           },
                                         {'id': 'metadata',
                                          'name': 'action_metadata',
                                          'action': 'metadata_edit_form',
                                          'permissions': (ModifyPortalContent,)
                                          },
                                         ),
                             'cps_proxytype': 'document',
                             'cps_is_searchable': 1,
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
