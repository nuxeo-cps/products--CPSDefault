# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
"""
  TreeBox
"""
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

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
        {'id':'title', 'type':'string', 'mode':'w', 'label':'Title'},
        {'id':'root', 'type':'string', 'mode':'w', 'label':'Root'},
        )

    def __init__(self, id, title='', root='', style='box_tree', **kw):
        BaseBox.__init__(self, id, style=style, kw=kw)
        self.title = title
        self.root = root

    security.declarePublic('getTree')
    def getTree(self, context):
        """ return the ptree from root """
        root = self.root
        if not root:
            portal_url = getToolByName(self, 'portal_url')
            root = portal_url.getRelativeUrl(context)
        LOG('TreeBox', DEBUG, 'Starting in root ' + root)
        path = filter(None, root.split('/'))
        portal_trees = getToolByName(self, 'portal_trees')
        if not hasattr(portal_trees, path[0]):
            raise Exception('no tree for %s' % path[0])
        prefix = '/'.join(path)

        return portal_trees[path[0]].getList(prefix=prefix)

InitializeClass(TreeBox)


def addTreeBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Tree Box."""
    ob = TreeBox(id, **kw)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
