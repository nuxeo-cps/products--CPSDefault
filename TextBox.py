# Copyright (c) 2003 Nuxeo SARL <http://nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
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
     'icon': 'box.png',
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
                 ),
     # additionnal cps stuff
     'cps_is_portalbox': 1,
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

    def __init__(self, id, category='textbox', text='', **kw):
        BaseBox.__init__(self, id, category=category, **kw)
        self.text = text


InitializeClass(TextBox)


def addTextBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Text Box."""
    ob = TextBox(id, **kw)
    dispatcher._setObject(id, ob)
    ob = getattr(dispatcher, id)
    ob.manage_permission(View, ('Anonymous',), 1)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
