# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
"""
  ActionBox
"""
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from BaseBox import BaseBox
from Products.CMFCore.utils import getToolByName

factory_type_information = (
    {'id': 'Action Box',
     'title': 'portal_type_ActionBox_title',
     'description': 'portal_type_ActionBox_description',
     'meta_type': 'Action Box',
     'icon': 'box.gif',
     'product': 'CPSDefault',
     'factory': 'addActionBox',
     'immediate_view': 'actionbox_edit_form',
     'filter_content_types': 0,
     'actions': ({'id': 'view',
                  'name': 'action_view',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'action_edit',
                  'action': 'actionbox_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 {'id': 'isportalbox',
                  'name': 'isportalbox',
                  'action': 'isportalbox',
                  'visible': 0,
                  'permissions': ()},
                 ),
     },
    )


class ActionBox(BaseBox):
    """
    An Action Box simply returns an action.
    """
    meta_type = 'Action Box'
    portal_type = 'Action Box'

    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
        {'id': 'categories', 'type': 'lines', 'mode': 'w', 
            'label':'Categories of actions'},
    )

    def __init__(self, id, categories=[], **kw):
        BaseBox.__init__(self, id, category='actionbox', kw=kw)
        self.categories = categories

    security.declarePublic('getActions')
    def getActions(self, context, actions=None):
        """Return actions that belong to self.categories"""
        if not actions:
            atool = getToolByName(self, 'portal_actions')
            actions = atool.listFilteredActionsFor(context)

        categories = all_categories = actions.keys()
        if self.categories:
            categories = self.categories

        items = []
        for cat in categories:
            if cat in all_categories:
                if len(actions[cat]):
                    items.append(actions[cat])

        if len(items) == 1 and len(items[0]) == 1 \
           and items[0][0]['id'] == 'view':
            items = []

        return items


InitializeClass(ActionBox)


def addActionBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Action Box."""
    ob = ActionBox(id, **kw)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
