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
  TreeBox
"""
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from BaseBox import BaseBox
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base
from copy import deepcopy
from Products.CPSDefault.utils import truncateText
from zLOG import LOG, DEBUG, INFO

factory_type_information = (
    {'id': 'Tree Box',
     'title': 'portal_type_TreeBox_title',
     'description': 'portal_type_TreeBox_description',
     'meta_type': 'Tree Box',
     'icon': 'box.png',
     'product': 'CPSDefault',
     'factory': 'addTreeBox',
     'immediate_view': 'treebox_edit_form',
     'filter_content_types': 0,
     'actions': ({'id': 'view',
                  'name': 'View',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'Edit',
                  'action': 'treebox_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 ),
     # additionnal cps stuff
     'cps_is_portalbox': 1,
     },
    )


class TreeBox(BaseBox):
    """
    A Tree Box display tree
    """
    meta_type = 'Tree Box'
    portal_type = 'Tree Box'

    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
        {'id': 'root', 'type': 'string', 'mode': 'w', 'label': 'Root'},
        {'id': 'depth', 'type': 'int', 'mode': 'w',
         'label': 'depth of the accessible tree'},
        {'id': 'portal_tree_stop_depth', 'type': 'int', 'mode': 'w',
         'label': 'maximum portal_tree depth (absolute depth)'},
        {'id': 'contextual', 'type': 'boolean', 'mode': 'w',
         'label': 'try to expand on current path'},
        {'id': 'children_only', 'type': 'boolean', 'mode': 'w',
         'label': 'display children only'},
        {'id': 'authorized_only', 'type': 'boolean', 'mode': 'w',
         'label': 'display authorized content only'},
        {'id': 'display_hidden_folder', 'type': 'boolean', 'mode': 'w',
         'label': 'Display folder with hidden properties'},
        {'id': 'display_managers', 'type': 'boolean', 'mode': 'w',
         'label': 'display managers'},
        {'id': 'display_description', 'type': 'boolean', 'mode': 'w',
         'label': 'display description'},
        {'id': 'show_root', 'type': 'boolean', 'mode': 'w',
         'label': 'show tree root'},
        {'id': 'display_icons', 'type': 'boolean', 'mode': 'w',
         'label': 'display icons in front of folders'},
        )

    display_managers = 0
    display_description = 0
    display_icons = 1
    display_hidden_folder = 0
    authorized_only = 1
    show_root = 1
    portal_tree_stop_depth = 0

    def __init__(self, id, category='treebox', root='', depth=0, contextual=0,
                 children_only=0, **kw):
        BaseBox.__init__(self, id, category=category, **kw)
        self.root = root
        self.depth = depth
        self.contextual = contextual
        self.children_only = children_only


    security.declarePublic('getTree')
    def getTree(self, context):
        """Return the ptree from root."""

        portal_url = getToolByName(self, 'portal_url')
        portal_trees = getToolByName(self, 'portal_trees')
        portal = portal_url.getPortalObject()

        # find the current container
        obj = context
        while obj and not obj.isPrincipiaFolderish:
            obj = aq_parent(aq_inner(obj))
        current_url = portal_url.getRelativeUrl(obj)
        current_path = current_url.split('/')

        if not self.root:
            root_path = current_path
        else:
            root_path = filter(None, self.root.split('/'))
            try:
                root_obj = portal.restrictedTraverse(root_path)
            except KeyError:
                LOG('TreeBox', INFO, 'box:%s use invalid root_path:%s.' %
                    (self.absolute_url(1), self.root))
                return []
            root_url = portal_url.getRelativeUrl(root_obj)

        root_tree = root_path[0]

        # If there no tree for root_tree, it means that the box is neither in
        # the workspaces and neither in the sections, thus we conclude that the
        # tree box is a the root of the portal.
        # In this case, we return a navigation tree for both sections and
        # workspaces.
        if not hasattr(aq_base(portal_trees), root_tree):
            rpath_sections = 'sections'
            sections = portal.restrictedTraverse(rpath_sections)
            rpath_workspaces = 'workspaces'
            workspaces = portal.restrictedTraverse(rpath_workspaces)
            return self.getTree(sections) + self.getTree(workspaces)

        kw = {'filter': self.authorized_only}
        if self.portal_tree_stop_depth:
            kw = {'stop_depth': self.portal_tree_stop_depth}
        tree = portal_trees[root_tree].getList(**kw)

        if self.root and len(root_path) > 1:
            tree = [x for x in tree if (
                (x['rpath'] + '/').startswith(root_url+'/'))]

        if self.children_only:
            # if option 'display subfolders only is checked'
            # remove objects that are not on the current path
            tree = [x for x in tree if (
                (x['rpath'] + '/').startswith(current_url+'/'))]

        root_depth = len(root_path)
        if not self.show_root:
            # removing the root
            tree = [x for x in tree if x['depth'] >= root_depth]

        # compute relativ depth
        # we need to copy items as we modify depth
        items = deepcopy(tree)
        if items:
            local_depth = items[0]['depth']
            items[0]['depth'] = 0
            local_rpath = items[0]['rpath'] + '/'
            for item in items[1:]:
                if not (item['rpath'] + '/').startswith(local_rpath):
                    local_rpath = item['rpath'] + '/'
                    local_depth = item['depth']
                    item['depth'] = 0
                else:
                    item['depth'] = item['depth'] - local_depth
        tree = items

        if self.depth and not self.contextual:
            tree = [x for x in tree if (x['depth'] <= self.depth)]
        elif self.depth and self.contextual:
            # 'contextual' means displaying current path as well as
            # its childrens and brothers
            parents_url = []
            parents_len = []
            for i in range(len(current_path) + 1):
                if i:
                    url = '/'.join(current_path[:i]) + '/'
                    parents_url.append(url)
                    parents_len.append(len(url.split('/')) + 1)

            items = []
            for item in tree:
                rpath = item['rpath'] + '/'
                if item['depth'] <= self.depth or rpath in parents_url:
                    items.append(item)
                    continue

                rpath_len = len(rpath.split('/'))

                for i in range(len(parents_url)):
                    if rpath.startswith(parents_url[i]) and \
                           rpath_len == parents_len[i]:
                        items.append(item)
                        break

            tree = items

        # now remove hidden_folder that are not in the current path
        if not self.display_hidden_folder:
            cur_url = current_url + '/'
            hidden = [item for item in tree if item.get('hidden_folder')]
            if hidden:
                hidden = [item for item in hidden
                          if not cur_url.startswith(item['rpath'] + '/')]
            if hidden:
                items = []
                for item in tree:
                    is_hidden = 0
                    for h in hidden:
                        if (item['rpath'] + '/').startswith(h['rpath'] + '/'):
                            is_hidden = 1
                            break
                    if not is_hidden:
                        items.append(item)
                tree = items

        # l10n
        locale = self.Localizer.get_selected_language()
        for item in tree:
            if item.has_key('l10n_titles') and \
                   item['l10n_titles'].has_key(locale):
                item['title'] = item['l10n_titles'][locale]
                if item['title']:
                    title_or_id = item['title']
                else:
                    title_or_id = item['id']
                item['title_or_id'] = title_or_id
                item['short_title'] = truncateText(title_or_id)
            if item.has_key('l10n_descriptions') and \
                   item['l10n_descriptions'].has_key(locale):
                item['description'] = item['l10n_descriptions'][locale]

        return tree

    security.declarePublic('getTreeObject')
    def getTreeObject(self, context):
        """Return the ptree object from root"""
        # XXX: same docstring as above. Something must be wrong.

        portal_url = getToolByName(self, 'portal_url')
        portal_trees = getToolByName(self, 'portal_trees')

        # find the current container
        obj = context
        while obj and not obj.isPrincipiaFolderish:
            obj = aq_parent(aq_inner(obj))
        current_url = portal_url.getRelativeUrl(obj)
        current_path = current_url.split('/')

        if not self.root:
            root_path = current_path
        else:
            root_path = filter(None,self.root.split('/'))
        root_tree = root_path[0]
        if not hasattr(aq_base(portal_trees), root_tree):
            return None
            #raise Exception('no tree for %s' % root_tree)

        tree = portal_trees[root_tree]

        return tree

    security.declarePublic('searchFolder')
    def searchFolder(self, context, query):
        """Searching over folder title and description.

        If query start with a ^ search for title that begin with query.
        """
        ptree = self.getTreeObject(context)
        if not ptree or not query or query == '^':
            return []
        tree = ptree.getList(filter=0)

        query = query.lower()
        items = []

        for item in tree:
            if not item['visible'] and \
                   not item.get('public_title_and_description'):
                continue
            if query[0] == '^':
                if item['title_or_id'].lower().startswith(query[1:]):
                    items.append(item)
            elif item['title_or_id'].lower().find(query) >= 0:
                items.append(item)
            elif item['description'].lower().find(query) >= 0:
                items.append(item)

        return items


InitializeClass(TreeBox)


def addTreeBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Tree Box."""
    ob = TreeBox(id, **kw)
    dispatcher._setObject(id, ob)
    ob = getattr(dispatcher, id)
    ob.manage_permission(View, ('Anonymous',), 1)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
