# (c) 2002 Nuxeo SARL <http://nuxeo.com>
# (c) 2002 Florent Guillaume <mailto:fg@nuxeo.com>
# (c) 2002 Julien Jalon <mailto:jj@nuxeo.com>
# (c) 2002 Préfecture du Bas-Rhin, France
# (c) 2002 CIRB, Belgique
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

__version__='$Revision$'[11:-2]


from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent


from BaseBox import BaseBox


def addTextBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Text Box."""
    ob = TextBox(id, **kw)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)


factory_type_information = (
    {'id': 'Text Box',
     'title': '_portal_type_Text Box',
     'description': ('A Text Box contains simple text.'),
     'meta_type': 'Text Box',
     'content_icon': 'box_icon.gif',
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
                 {'id': 'render_title',
                  'name': 'Render title',
                  'action': 'basebox_render_title',
                  'visible': 0,
                  'permissions': ()},
                 {'id': 'render_body',
                  'name': 'Render body',
                  'action': 'textbox_render_body',
                  'visible': 0,
                  'permissions': ()},
                 {'id': 'render_box',
                  'name': 'Render box',
                  'action': 'box_text',
                  'visible': 0,
                  'permissions': ()},                 
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
    # XXX Hack for CMF 1.3
    portal_type = 'Text Box'

    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
        {'id':'title', 'type':'string', 'mode':'w', 'label':'Title'},
        {'id':'text', 'type':'text', 'mode':'w', 'label':'Text'},
        )

    def __init__(self, id, title='', text='', **kw):
        apply(BaseBox.__init__, (self, id), kw)
        self.title = title
        self.text = text



InitializeClass(TextBox)

