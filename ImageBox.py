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
  ImageBox
"""
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Acquisition import aq_base
from OFS.Image import Image
from OFS.Folder import Folder
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from BaseBox import BaseBox

factory_type_information = (
    {'id': 'Image Box',
     'title': 'portal_type_ImageBox_title',
     'description': 'portal_type_ImageBox_description',
     'meta_type': 'Image Box',
     'icon': 'box.png',
     'product': 'CPSDefault',
     'factory': 'addImageBox',
     'immediate_view': 'imagebox_edit_form',
     'filter_content_types': 0,
     'actions': ({'id': 'view',
                  'name': 'View',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'Edit',
                  'action': 'imagebox_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 ),
     # additionnal cps stuff
     'cps_is_portalbox': 1,
     },
    )


class ImageBox(BaseBox, Folder):
    # XXX need explanation for using Folder as a parent.
    # Why not a mixin with OFS.Image?
    """
    A Image Box.
    """
    meta_type = 'Image Box'
    portal_type = 'Image Box'

    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
        {'id': 'image_name', 'type': 'text', 'mode': 'w', 
         'label': 'Image file name'},
        {'id': 'image_link', 'type': 'text', 'mode': 'w', 
         'label': 'Link when clicking on the image'},
        )

    def __init__(self, id, category='imagebox', image_name='', image_link='',
                 **kw):
        BaseBox.__init__(self, id, category=category, **kw)
        self.image_name = image_name
        self.image_link = image_link

    def load(self, path):
        """
        Load image after having created the box.
        Path must be absolute from the /var/ directory.
        (absolute path for an image in your /skins/images/
        directory would be ../Products/your_product_dir/skins/images)
        """
        image_id = 'image_id'
        max_len = 2*1024*1024

        path = os.path.join(CLIENT_HOME, path)
        f = open(path,'r')
        if len(f.read(max_len)) < max_len:
            f.seek(0)
            img = Image(image_id, self.title, f)
            if hasattr(aq_base(self), image_id):
                self._delObject(image_id)
            self._setObject(image_id, img)

    def edit(self, **kw):
        image_id = 'image_id'
        max_len = 2*1024*1024

        BaseBox.edit(self, **kw)

        file_action = self.REQUEST.form.get('file_action')
        if file_action == 'delete':
            self.image_name = ''
            if hasattr(aq_base(self), image_id):
                self._delObject(image_id)
        elif file_action == 'change':
            f = self.REQUEST.form.get('file')
            if f and f.filename and f.read(1) != '':
                if len(f.read(max_len)) < max_len:
                    f.seek(0)
                    self.image_name = f.filename
                    img = Image(image_id, self.title, f)
                    if hasattr(aq_base(self), image_id):
                        self._delObject(image_id)
                    self._setObject(image_id, img)
                # XXX no error or warning if image too big
        else:
            # XXX why doing this?
            if hasattr(aq_base(self), image_id):
                img = getattr(aq_base(self), image_id)
                img.manage_edit(self.title, img.getContentType())

InitializeClass(ImageBox)


def addImageBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Image Box."""
    ob = ImageBox(id, **kw)
    dispatcher._setObject(id, ob)
    ob = getattr(dispatcher, id)
    ob.manage_permission(View, ('Anonymous',), 1)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
