# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
"""
  TextBox
"""
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from BaseBox import BaseBox

factory_type_information = (
    {'id': 'Text Box',
     'title': 'portal_type_TextBox_title',
     'description': 'portal_type_TextBox_description',
     'meta_type': 'Text Box',
     'icon': 'box.gif',
     'product': 'CPSDefault',
     'factory': 'addTextBox',
     'immediate_view': 'textbox_edit_form',
     'filter_content_types': 0,
     'actions': ({'id': 'view',
                  'name': 'View',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'Edit',
                  'action': 'textbox_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 {'id': 'isportalbox',
                  'name': 'isportalbox',
                  'action': 'isportalbox',
                  'visible': 0,
                  'permissions': ()},
                 ),
     },
    )


class TextBox(BaseBox):
    """
    A Text Box simply returns a text.
    """
    meta_type = 'Text Box'
    portal_type = 'Text Box'
    
    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
        {'id':'text', 'type':'text', 'mode':'w', 'label':'Text'},
        )

    def __init__(self, id, text='', **kw):
        BaseBox.__init__(self, id, macro='textbox', kw=kw)
        self.text = text


InitializeClass(TextBox)


def addTextBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Text Box."""
    ob = TextBox(id, **kw)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
