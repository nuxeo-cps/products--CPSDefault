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
  FlashBox
"""
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Acquisition import aq_base
from OFS.Image import File
from OFS.Folder import Folder
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from BaseBox import BaseBox

from zLOG import LOG, DEBUG

factory_type_information = (
    {'id': 'Flash Box',
     'title': 'portal_type_FlashBox_title',
     'description': 'portal_type_FlashBox_description',
     'meta_type': 'Flash Box',
     'icon': 'box.png',
     'product': 'CPSDefault',
     'factory': 'addFlashBox',
     'immediate_view': 'flashbox_edit_form',
     'filter_content_types': 0,
     'actions': ({'id': 'view',
                  'name': 'View',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'Edit',
                  'action': 'flashbox_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 ),
     # additionnal cps stuff
     'cps_is_portalbox': 1,
     },
    )


class FlashBox(BaseBox,Folder):
    """
    A box displaying Macromedia Flash objects.
    """
    meta_type = 'Flash Box'
    portal_type = 'Flash Box'

    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
        {'id': 'flash_filename', 'type': 'text', 'mode': 'w', 
         'label': 'Flash file name'},
        {'id': 'flash_width', 'type': 'int', 'mode': 'w', 
         'label': 'Flash Object Width'},
        {'id': 'flash_height', 'type': 'int', 'mode': 'w', 
         'label': 'Flash Object Height'},
        )
    
    flash_width = '300'
    flash_height = '200'

    def __init__(self, id, category='flashbox', flash_filename='', **kw):
        BaseBox.__init__(self, id, category=category, **kw)
        self.flash_filename = flash_filename
        self.flash_width = '300'
        self.flash_height = '200'

    def edit(self, **kw):
        flash_id = 'flash_id'
        max_len = 2*1024*1024

        file_action = self.REQUEST.form.get('file_action')
        if file_action == 'delete':
            self.flash_filename = ''
            if hasattr(aq_base(self), flash_id):
                self._delObject(flash_id)
        elif file_action == 'change':
            f = self.REQUEST.form.get('file')
            if f and f.filename and f.read(1) != '':
                if len(f.read(max_len)) < max_len:
                    f.seek(0)
                    self.flash_filename = f.filename
                    flash_object = File(flash_id, self.flash_filename, f)
                    if hasattr(aq_base(self), flash_id):
                        self._delObject(flash_id)
                    self._setObject(flash_id, flash_object)

        self.flash_width = self.REQUEST.form.get('flash_width')
        self.flash_height = self.REQUEST.form.get('flash_height')

        BaseBox.edit(self, **kw)


InitializeClass(FlashBox)


def addFlashBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Flash Box."""
    ob = FlashBox(id, **kw)
    dispatcher._setObject(id, ob)
    ob = getattr(dispatcher, id)
    ob.manage_permission(View, ('Anonymous',), 1)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
