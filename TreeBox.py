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

from zLOG import LOG, DEBUG

factory_type_information = (
    {'id': 'Tree Box',
     'title': 'portal_type_TreeBox_title',
     'description': 'portal_type_TreeBox_description',
     'meta_type': 'Tree Box',
     'icon': 'box.gif',
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
         'label': 'depth of the tree'},
        {'id': 'contextual', 'type': 'boolean', 'mode': 'w', 
         'label': 'try to expand on current path'},
        {'id': 'children_only', 'type': 'boolean', 'mode': 'w', 
         'label': 'display children only'},
        {'id': 'authorized_only', 'type': 'boolean', 'mode': 'w', 
         'label': 'display authorized content only'},
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
    authorized_only = 1
    show_root = 1

    def __init__(self, id, root='', depth=0, contextual=0,
                 children_only=0, **kw):
        BaseBox.__init__(self, id, category='treebox', kw=kw)
        self.root = root
        self.depth = depth
        self.contextual = contextual
        self.children_only = children_only

    security.declarePublic('getTree')
    def getTree(self, context):
        """Return the ptree from root

        """

        portal_url = getToolByName(self, 'portal_url')
        portal_trees = getToolByName(self, 'portal_trees')
        portal_membership = getToolByName(self, 'portal_membership')

        # find the current container
        obj = context
        while obj and not obj.isPrincipiaFolderish:
            obj = aq_parent(aq_inner(obj))
        current_url = portal_url.getRelativeUrl(obj)
        current_path = current_url.split('/')
        current_path_length = len(current_path)

        if not self.root:
            root_path = current_path
        else:
            root_path = filter(None,self.root.split('/'))

        root_tree = root_path[0]

        if not hasattr(aq_base(portal_trees), root_tree):
            return []
            #raise Exception('no tree for %s' % root_tree)

        tree = portal_trees[root_tree].getList(filter=self.authorized_only)

        if self.children_only:
            #if option 'display subfolders only is checked'
            #remove objects that are not on the current path
            tree = [x for x in tree if (x['rpath'].startswith(current_url))]

        if not self.show_root:
            delta = len(root_path)
            tmp_tree = []
            for x in tree:
                if x['depth'] >= delta:
                    tmp_entry = x.copy()
                    tmp_entry['depth'] = x['depth'] - delta
                    tmp_tree.append(tmp_entry)
            tree = tmp_tree
            
        if self.depth and self.contextual:
            depth = self.depth - 1
            max_depth = len(current_path) + depth

            tfilter = []
            # make a comment to says in what the commented block is useful
##            for i in range(len(current_path)+1):
##                if i:
##                    tfilter.append({'url': '/'.join(current_path[:i]),
##                                    'depth': i + depth})
            tfilter.append({'url': current_url,
                            'depth': current_path_length})
            
            items = []
            for item in tree:
                d = item['depth']
                if d > max_depth:
                    continue
                url = item['rpath']
                for f in tfilter:
                    if d > f['depth']:
                        continue
                    if url.startswith(f['url']):
                        item = item.copy()
                        item['depth'] = d - current_path_length + 1
                        items.append(item)
                        break

            return items

        if self.depth:
            d = self.depth + len(root_path) - 1
            root_url = '/'.join(root_path)
            res = [x for x in tree if (x['depth']<=d and
                                      x['rpath'].startswith(root_url))]
            return res

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

InitializeClass(TreeBox)


def addTreeBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Tree Box."""
    ob = TreeBox(id, **kw)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
