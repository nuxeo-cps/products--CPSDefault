# (c) 2003 Nuxeo SARL <http://nuxeo.com>
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

from zLOG import LOG, DEBUG

factory_type_information = (
    {'id': 'Tree Box',
     'title': '_portal_type_Tree Box',
     'description': ('A Tree Box contains navigation.'),
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
                 {'id': 'render_box',
                  'name': 'Render box',
                  'action': 'box_tree',
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


class TreeBox(BaseBox):
    """
    A Tree Box display tree
    """
    meta_type = 'Tree Box'
    portal_type = 'Tree Box'
    
    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
        {'id':'root', 'type':'string', 'mode':'w', 'label':'Root'},
        {'id':'depth', 'type':'int', 'mode':'w', 'label':'depth of the tree'},
        {'id':'contextual', 'type':'boolean', 'mode':'w', 'label':'try to expand on current path'},
        )

    def __init__(self, id, title='', root='', depth=0, contextual=0,
                 style='box_tree', **kw):
        BaseBox.__init__(self, id, style=style, kw=kw)
        self.title = title
        self.root = root
        self.depth = depth
        self.contextual = contextual

    security.declarePublic('getTree')
    def getTree(self, context):
        """ return the ptree from root """
        portal_url = getToolByName(self, 'portal_url')
        portal_trees = getToolByName(self, 'portal_trees')

        # find the current container
        obj = context
        while obj and not obj.isPrincipiaFolderish:
            obj = aq_parent(aq_inner(obj))
        current_url = portal_url.getRelativeUrl(obj)
        current_path = current_url.split('/')
        
        if not self.root:
            root_tree = current_path[0]
        else:
            root_tree = filter(None,self.root.split('/'))[0]
        
        if not hasattr(portal_trees, root_tree):
            raise Exception('no tree for %s' % root_tree)

        tree = portal_trees[root_tree].getList()

        if self.depth and self.contextual:
            depth = self.depth - 1
            max_depth = len(current_path) + depth
                
            tfilter = []
            for i in range(len(current_path)+1):
                if i:
                    tfilter.append({'url': '/'.join(current_path[:i]),
                                    'depth': i + depth})
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
                        items.append(item)
                        break
                    
            return items

        if self.depth:
            d = self.depth
            return [x for x in tree if (x['depth']<=d)]
        
        return tree


InitializeClass(TreeBox)


def addTreeBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Tree Box."""
    ob = TreeBox(id, **kw)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
