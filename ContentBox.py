# (c) 2003 Nuxeo SARL <http://nuxeo.com>
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
                 {'id': 'isportalbox',
                  'name': 'isportalbox',
                  'action': 'isportalbox',
                  'visible': 0,
                  'permissions': ()},
                 ),
     },
    )


class ContentBox(BaseBox):
    """
    A Content Box display content
    """
    meta_type = 'Content Box'
    portal_type = 'Content Box'

    nb_items=0
    sort_by=direction=display=None

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
        )

    def __init__(self, id, folder=None, nb_items=None, sort_by=None,
                 direction=None, display=None, **kw):
        BaseBox.__init__(self, id, macro='contentbox', kw=kw)
        self.folder = folder


    security.declarePublic('getFolderObject')
    def getFolderObject(self, context):
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

    security.declarePublic('getFolderContents')
    def getFolderContents(self, context, sort_by='status',
                          direction='asc'):
        """Get a sorted list of contents object"""
        folder = self.getFolderObject(context)
        if folder:
            items = folder.getFolderContents(sort_by=self.sort_by,
                                             direction=self.direction,
                                             hide_folder=1)
            if self.nb_items and len(items) > self.nb_items:
                items = items[:self.nb_items]

            return items

        return []

InitializeClass(ContentBox)


def addContentBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Content Box."""
    ob = ContentBox(id, **kw)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
