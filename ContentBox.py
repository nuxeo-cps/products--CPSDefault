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

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Acquisition import aq_base
from ZTUtils import make_query
from DateTime import DateTime
from zLOG import LOG, DEBUG, INFO

from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName

from BaseBox import BaseBox



factory_type_information = (
    {'id': 'Content Box',
     'title': 'portal_type_ContentBox_title',
     'description': 'portal_type_ContentBox_description',
     'meta_type': 'Content Box',
     'icon': 'box.png',
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
    no_recurse = 0
    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
        {'id': 'folder', 'type': 'string', 'mode': 'w',
         'label': 'Folder path'},
        {'id': 'nb_items', 'type': 'int', 'mode': 'w',
         'label': 'Number of items'},
        {'id': 'sort_by', 'type': 'string', 'mode': 'w',
         'label': 'Sorting criteria'},
        {'id': 'direction', 'type': 'string', 'mode': 'w',
         'label': 'Direction for sorting'},
        {'id': 'display', 'type': 'string', 'mode': 'w',
         'label': 'Format for display'},
        {'id': 'zoom', 'type': 'int', 'mode': 'w',
         'label': 'Number of zoomed documents'},
        {'id': 'query_title', 'type': 'string', 'mode': 'w',
         'label': 'Title criteria' },
        {'id': 'query_description', 'type': 'string', 'mode': 'w',
         'label': 'Description criteria' },
        {'id': 'query_fulltext', 'type': 'string', 'mode': 'w',
         'label': 'Full text criteria' },
        {'id': 'query_status', 'type': 'string', 'mode': 'w',
         'label': 'Status criteria' },
        {'id': 'query_portal_type', 'type': 'lines', 'mode': 'w',
         'label': 'Portal type criteria' },
        {'id': 'query_modified', 'type': 'string', 'mode': 'w',
         'label': 'Modified criteria' },
        {'id': 'no_recurse', 'type': 'boolean', 'mode': 'w',
         'label': 'Non-recursive search'}, 
        )

    def __init__(self, id, category='contentbox', folder='', nb_items=0,
                 sort_by='', direction='', display='', query_title='',
                 query_description='', query_fulltext='', query_status='',
                 query_portal_type=[], query_modified='', zoom=0, no_recurse = 0, **kw):
        BaseBox.__init__(self, id, category=category, **kw)
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
        self.no_recurse = no_recurse


    security.declarePublic('getContents')
    def getContents(self, context):
        """Get a sorted list of contents object"""
        utool = getToolByName(self, 'portal_url')
        
        folder = self._getFolderObject(context)
        items = []
        link_more = ''
        
        if folder:
            query = self._buildQuery(folder)

            if len(query):
                # this is a search box
                folder_prefix = ''
                if self.folder:
                    folder_prefix = utool.getRelativeUrl(folder)

                items = folder.search(query=query,
                                      sort_by=self.sort_by,
                                      direction=self.direction,
                                      hide_folder=0,
                                      folder_prefix=folder_prefix)
            else:
                # this is a folder content box
                displayed = context.REQUEST.get('displayed', [''])
                items = folder.getFolderContents(sort_by=self.sort_by,
                                                 direction=self.direction,
                                                 hide_folder=1,
                                                 displayed=displayed)
                
            if self.nb_items and len(items) > self.nb_items:
                items = items[:self.nb_items]
                if len(query):
                    if query.has_key('modified'):
                        # Use argument marshalling
                        query['modified:date'] = query['modified']
                        del query['modified']
                    q = make_query(sort_by=self.sort_by,
                                   direction=self.direction,
                                   hide_folder=1,
                                   folder_prefix=folder_prefix,
                                   title_search=self.title,
                                   search_within_results=1,
                                   **query)

                    link_more = './advanced_search_form?%s' % q
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
            # setting folder to '.' allow a contextual search
            elif self.folder == '.':
                return context
            elif not hasattr(aq_base(container), folder):
                return obj

            try:
                obj = container.restrictedTraverse(folder)
            except KeyError:
                pass

        return obj


    security.declarePrivate('_buildQuery')
    def _buildQuery(self, folder):
        """Build a query for search.py """
        query = {}
        if self.query_fulltext:
            query['SearchableText'] = self.query_fulltext
        if self.query_title:
            query['Title'] = self.query_title
        if self.query_portal_type and filter(None, self.query_portal_type):
            query['portal_type'] = list(self.query_portal_type)
        if self.query_description:
            query['Description'] = self.query_description
        if self.query_status:
            query['review_state'] = self.query_status

        if self.no_recurse == 1:
            query['search_relative_path'] = 1

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
                    modified = (today - 1).Date()
                elif self.query_modified == 'time_last_week':
                    modified = (today - 7).Date()
                elif self.query_modified == 'time_last_month':
                    modified = (today - 31).Date()
            if modified:
                query['modified'] = modified
                query['modified_usage'] = "range:min"

        return query

InitializeClass(ContentBox)


def addContentBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Content Box."""
    ob = ContentBox(id, **kw)
    dispatcher._setObject(id, ob)
    ob = getattr(dispatcher, id)
    ob.manage_permission(View, ('Anonymous',), 1)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
