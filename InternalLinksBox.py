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
  InternalLinksBox
"""
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Acquisition import aq_base
from zLOG import LOG, DEBUG

from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName

from BaseBox import BaseBox


factory_type_information = (
    {'id': 'InternalLinks Box',
     'title': 'portal_type_InternalLinksBox_title',
     'description': 'portal_type_InternalLinksBox_description',
     'meta_type': 'InternalLinks Box',
     'icon': 'box.gif',
     'product': 'CPSDefault',
     'factory': 'addInternalLinksBox',
     'immediate_view': 'internallinksbox_edit_form',
     'filter_content_types': 0,
     'actions': ({'id': 'view',
                  'name': 'action_view',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'action_edit',
                  'action': 'internallinksbox_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 ),
     # additionnal cps stuff
     'cps_is_portalbox': 1,
     },
    )


class InternalLinksBox(BaseBox):
    """
    An InternalLinks Box allows displaying a list of documents
    manually chosen.
    """
    meta_type = 'InternalLinks Box'
    portal_type = 'InternalLinks Box'

    query_portal_type = []
    zoom = 0

    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
         {'id': 'links', 'type': 'lines', 'mode': 'w',
         'label': 'Internal links' },
        )

    def __init__(self, id, category='internallinksbox', links=[], **kw):
        BaseBox.__init__(self, id, category=category, **kw)
        self.links = links

    security.declarePublic('getContents')
    def getContents(self):
        """Get a list of contents object"""
        utool = getToolByName(self, 'portal_url')
        items = []
        for url in self.links:
            LOG("internallinksbox:getcontents", DEBUG, url)
            LOG("internallinksbox:getcontents", DEBUG, utool.restrictedTraverse(url))
            if not url:
                continue
            items.append(utool.restrictedTraverse(url))
        return items
    
InitializeClass(InternalLinksBox)


def addInternalLinksBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Content Box."""
    ob = InternalLinksBox(id, **kw)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
