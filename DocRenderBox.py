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
 Doc RenderBox
"""
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from zLOG import LOG, DEBUG, INFO

from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from BaseBox import BaseBox

factory_type_information = (
    {'id': 'Doc Render Box',
     'title': 'portal_type_DocRenderBox_title',
     'description': 'portal_type_DocRenderBox_description',
     'meta_type': 'Doc Render Box',
     'icon': 'box.png',
     'product': 'CPSDefault',
     'factory': 'addDocRenderBox',
     'immediate_view': 'renderbox_edit_form',
     'filter_content_types': 0,
     'actions': ({'id': 'view',
                  'name': 'action_view',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'action_edit',
                  'action': 'renderbox_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 ),
     # additionnal cps stuff
     'cps_is_portalbox': 1,
     },
    )


class DocRenderBox(BaseBox):
    """
    A Doc Render Box allows displaying a rendering of a document 
    manually chosen.
    """
    meta_type = 'Doc Render Box'
    portal_type = 'Doc Render Box'

    security = ClassSecurityInfo()
    _properties = BaseBox._properties + (
      {'id': 'doc_url', 'type': 'string', 'mode': 'w',
        'label': 'Render'},
    )
    def __init__(self, id, category='docrenderbox', doc_url='',  **kw):
        BaseBox.__init__(self, id, category=category, **kw)
        self.doc_url = doc_url

    security.declarePublic('getContent')
    def getContent(self, context=None):
        """Get the content of an object
        """
        utool = getToolByName(self, 'portal_url')
        mtool = getToolByName(self, 'portal_membership')

        if self.doc_url == '':
            return ''
     
        if self.doc_url.startswith('/'):
            try:
                obj = utool.restrictedTraverse(self.doc_url)
            except KeyError:
                return ''
        else:
            # FIXME: we assume it's just an id for now
            # We don't want to use acquisition
            if not self.doc_url in context.objectIds():
                return ''
            try:
                obj = getattr(context, self.doc_url)
            except KeyError:
                return ''
        
        if not mtool.checkPermission('View', obj):
            return ''   
        return obj.getContent().render(proxy=obj)

InitializeClass(DocRenderBox)

def addDocRenderBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Content Box."""
    ob = DocRenderBox(id, **kw)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
