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
  ContentBox
"""
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from BaseBox import BaseBox
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

from zLOG import LOG, DEBUG

factory_type_information = (
    {'id': 'Content Box',
     'title': 'portal_type_ContentBox_title',
     'description': 'portal_type_ContentBox_description',
     'meta_type': 'Content Box',
     'icon': 'box.gif',
     'product': 'CPSDefault',
     'factory': 'addContentBox',
     'immediate_view': 'contentbox_edit_form',
     'filter_content_types': 0,
     'actions': ({'id': 'view',
                  'name': 'action_view',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'action_edit',
                  'action': 'contentbox_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 ),
     # additionnal cps stuff
     'cps_is_portalbox': 1,
     },
    )


class ContentBox(BaseBox):
    """
    A Content Box display content
    """
    meta_type = 'Content Box'
    portal_type = 'Content Box'

    query_portal_type = []
    zoom = 0

    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
        {'id': 'folder', 'type': 'string', 'mode': 'w',
         'label': 'folder path'},
        {'id': 'nb_items', 'type': 'int', 'mode': 'w',
         'label': 'number of items'},
        {'id': 'sort_by', 'type': 'string', 'mode': 'w',
         'label': 'sorting criteria'},
        {'id': 'direction', 'type': 'string', 'mode': 'w',
         'label': 'direction for sorting'},
        {'id': 'display', 'type': 'string', 'mode': 'w',
         'label': 'format for display'},
        {'id': 'zoom', 'type': 'int', 'mode': 'w',
         'label': 'number of document using info_summary'},
        {'id': 'query_title', 'type': 'string', 'mode': 'w',
         'label': 'Search criteria' },
        {'id': 'query_description', 'type': 'string', 'mode': 'w',
         'label': 'Search criteria' },
        {'id': 'query_fulltext', 'type': 'string', 'mode': 'w',
         'label': 'Search criteria' },
        {'id': 'query_status', 'type': 'string', 'mode': 'w',
         'label': 'Search criteria' },
        {'id': 'query_portal_type', 'type': 'lines', 'mode': 'w',
         'label': 'Search criteria' },
        {'id': 'query_modified', 'type': 'string', 'mode': 'w',
         'label': 'Search criteria' },
        )

    def __init__(self, id, folder='', nb_items=0, sort_by='',
                 direction='', display='',
                 query_title='', query_description='', query_fulltext='',
                 query_status='', query_portal_type=[], query_modified='',
                 zoom = 0,
                 **kw):
        BaseBox.__init__(self, id, category='contentbox', kw=kw)
        self.folder = folder
        self.nb_items = nb_items
        self.sort_by = sort_by
        self.direction = direction
        self.display = display
        self.query_status = query_status
        self.query_fulltext = query_fulltext
        self.query_description = query_description
        self.query_portal_type = query_portal_type
        self.query_title = query_title
        self.query_modified = query_modified
        self.zoom = zoom


    security.declarePublic('getContents')
    def getContents(self, context):
        """Get a sorted list of contents object"""
        utool = getToolByName(self, 'portal_url')
        folder = self._getFolderObject(context)
        items = []
        link_more = ''
        if folder:
            query = self._buildQuery()
            if len(query):
                # this is a search box
                folder_prefix = ''
                if self.folder:
                    folder_prefix = utool.getRelativeUrl(folder)
                items = folder.search(query=query,
                                      sort_by=self.sort_by,
                                      direction=self.direction,
                                      hide_folder=1,
                                      folder_prefix=folder_prefix)

            else:
                # this is a folder content box
                items = folder.getFolderContents(sort_by=self.sort_by,
                                                 direction=self.direction,
                                                 hide_folder=1)


            if self.nb_items and len(items) > self.nb_items:
                items = items[:self.nb_items]
                if len(query):
                    from ZTUtils import make_query
                    q = make_query(sort_by=self.sort_by,
                                   direction=self.direction,
                                   hide_folder=1,
                                   folder_prefix=folder_prefix,
                                   **self._buildQuery())
                    link_more = 'search_form?%s' % q
                else:
                    link_more = utool.getRelativeUrl(folder)


        return (items, link_more)


    security.declarePrivate('_getFolderObject')
    def _getFolderObject(self, context):
        """Return the self.folder object or the context object if any"""
        obj = None
        if not self.folder:
            obj = context
        else:
            container = context
            folder = self.folder
            # if folder path start with a '/' then
            #     we 're expecting an absolute path
            # else
            #     folder must be an attribute of context,
            #     because we don't want any acquisition
            if self.folder[0]=='/':
                container = self.portal_url.getPortalObject()
                folder = self.folder[1:]
            elif not hasattr(aq_base(container), folder):
                return obj

            try:
                obj = container.restrictedTraverse(folder)
            except KeyError:
                pass

        return obj



    security.declarePrivate('_buildQuery')
    def _buildQuery(self):
        """Build a query for search.py """
        query = {}
        if self.query_fulltext:
            query['SearchableText'] = self.query_fulltext
        if self.query_title:
            query['Title'] = self.query_title
        if self.query_portal_type and self.query_portal_type != ['']:
            query['portal_type'] = self.query_portal_type
        if self.query_description:
            query['Description'] = self.query_description
        if self.query_status:
            query['review_state'] = self.query_status

        if self.query_modified:
            modified = None
            if self.query_modified == 'time_last_login':
                mtool = getToolByName(self, 'portal_membership')
                member = mtool.getAuthenticatedMember()
                if hasattr(aq_base(member), 'last_login_time'):
                    modified = member.last_login_time
            else:
                today = DateTime()
                if self.query_modified == 'time_yesterday':
                    modified = (today-1).Date()
                elif self.query_modified == 'time_last_week':
                    modified = (today-7).Date()
                elif self.query_modified == 'time_last_month':
                    modified = (today-31).Date()
            if modified:
                query['modified'] = modified
                query['modified_usage'] = "range:min"

        return query

InitializeClass(ContentBox)


def addContentBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Content Box."""
    ob = ContentBox(id, **kw)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
