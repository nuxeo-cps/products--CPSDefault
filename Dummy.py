# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
""" A Dummy document
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
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
     'cps_proxy_type': 'document',
     'cps_is_searchable': 1,
     },
    )

class Dummy(CPSBaseDocument):
    """ The simpliest CPS document with a body """
    meta_type = 'Dummy'
    portal_type = meta_type # to ease testing

    _properties = CPSBaseDocument._properties + (
        {'id': 'body', 'type': 'text', 'mode': 'w', 'label': 'Body'},
        )

    security = ClassSecurityInfo()

    def __init__(self, id, body='', **kw):
        CPSBaseDocument.__init__(self, id, **kw)
        self.body = body


    security.declareProtected(ModifyPortalContent, 'edit')
    def edit(self, **kw):
        """ edit """
        CPSBaseDocument.edit(self, **kw)
        self._size = self._compute_size()


    security.declareProtected(View, 'getAdditionalContentInfo')
    def getAdditionalContentInfo(self):
        """ Return a dictonary used in getContentInfo """
        infos = {}
        max_len = 64
        if hasattr(self, 'body'):
            if len(self.body) > max_len:
                infos['summary'] = self.body[:max_len] + '...'
            else:
                infos['summary'] = self.body

        # infos['preview'] = 'logo_nuxeo.gif'
        return infos

    security.declareProtected(View, 'get_size')
    def get_size(self):
        """ return the size of the data """
        if hasattr(self, '_size'):
            return self._size
        return self._compute_size()

    security.declarePrivate('_compute_size')
    def _compute_size(self):
        s = 0
        for item in self.propdict().keys():
            s += len(str(getattr(self, item, '')))
        return s
    #EOC

InitializeClass(Dummy)


def addDummy(container, id, REQUEST=None, **kw):
    """ Add a Dummy Document """
    ob = Dummy(id, **kw)
    return CPSBase_adder(container, ob, REQUEST=REQUEST)

#EOF
