# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
""" A Dummy document
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from OFS.Image import Image
from OFS.Folder import Folder
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

class Dummy(CPSBaseDocument, Folder):
    """ The simpliest CPS document with a body """
    meta_type = 'Dummy'
    portal_type = meta_type

    image_name = ''
    image_id = 'dummy_image'
    image_max_size = 2*1024*1024

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

        file_action = self.REQUEST.form.get('file_action')
        if file_action == 'delete':
            self.image_name = ''
            if hasattr(aq_base(self), self.image_id):
                self._delObject(self.image_id)
        elif file_action == 'change':
            f = self.REQUEST.form.get('file')
            if f and f.filename and f.read(1) != '':
                if len(f.read(self.image_max_size)) < self.image_max_size:
                    f.seek(0)
                    self.image_name = f.filename
                    img = Image(self.image_id, self.image_name, f)
                    if hasattr(aq_base(self), self.image_id):
                        self._delObject(self.image_id)
                    self._setObject(self.image_id, img)

        self._size = self._compute_size()


    security.declareProtected(View, 'getAdditionalContentInfo')
    def getAdditionalContentInfo(self):
        """ Return a dictonary used in getContentInfo """
        infos = {}
        max_len = 512
        if hasattr(aq_base(self), 'body'):
            if len(self.body) > max_len:
                infos['summary'] = self.body[:max_len] + '...'
            else:
                infos['summary'] = self.body

        if hasattr(aq_base(self), self.image_id):
            infos['preview'] = self.absolute_url(1) + '/' + self.image_id
        return infos

    security.declareProtected(View, 'get_size')
    def get_size(self):
        """ return the size of the data """
        if hasattr(aq_base(self), '_size'):
            return self._size
        return self._compute_size()

    security.declarePrivate('_compute_size')
    def _compute_size(self):
        s = 0
        for item in self.propdict().keys():
            s += len(str(getattr(self, item, '')))
        if hasattr(aq_base(self), self.image_id):
            s += self[self.image_id].get_size()
        
        return s
    #EOC

InitializeClass(Dummy)


def addDummy(container, id, REQUEST=None, **kw):
    """ Add a Dummy Document """
    ob = Dummy(id, **kw)
    return CPSBase_adder(container, ob, REQUEST=REQUEST)

#EOF
