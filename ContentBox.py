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
                  'name': 'View',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'Edit',
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
    
    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
        {'id':'folder', 'type':'string', 'mode':'w', 'label':'folder path'},
        )

    def __init__(self, id, folder=None, **kw):
        BaseBox.__init__(self, id, macro='contentbox', kw=kw)
        self.folder = folder


    security.declarePublic('getFolderObject')
    def getFolderObject(self, context):
        """Return the self.folder object or the context object if any"""
        if self.folder:
            if self.folder[0]=='/':
                return self.restrictedTraverse(self.folder)
            else: #rpath
                if hasattr(aq_base(context), self.folder):
                    folder = context.absolute_url(relative=1) + '/' + \
                             self.folder
                    return self.restrictedTraverse(folder)
                return None
        return context

    security.declarePublic('getFolderContents')
    def getFolderContents(self, context, sort_by='status',
                          direction='asc'):
        """Get a sorted list of contents object"""
        mtool = getToolByName(self, 'portal_membership')
        wtool = getToolByName(self, 'portal_workflow')

        # filtering
        items = []
        now = context.ZopeTime()
        folder = self.getFolderObject(context)
        if not folder:
            return []
        for item in folder.objectValues():
            if item.getId().startswith('.'):
                continue
            if item.isPrincipiaFolderish:
                continue
            if not mtool.checkPermission('View', item):
                continue
# XXX expire should be handle by wf
#            if item.effective() <= now and item.expires() > now:
#                items.append(item)

        # sorting
        # XXX hardcoded status !
        status_sort_order={'nostate':'0',
                           'pending':'1',
                           'published':'2',
                           'work':'3',
                           }
        
        def cmp_desc(x, y):
            return -cmp(x, y)

        if sort_by == 'status':
            objects = [(status_sort_order[wtool.getInfoFor(x, 'review_state',
                                                           'nostate')] + \
                        x.title_or_id().lower(), x) for x in items]
        else:
            objects = [(x.getId(), x) for x in items]
        
        if direction != 'asc':
            objects.sort(cmp_desc)
        else:
            objects.sort()
        items = [x[1] for x in objects]

        return items


InitializeClass(ContentBox)


def addContentBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Content Box."""
    ob = ContentBox(id, **kw)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
