# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
"""
  BaseBox
"""
import string
from ComputedAttribute import ComputedAttribute

from Globals import InitializeClass, DTMLFile
from AccessControl import getSecurityManager, ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner

from OFS.PropertyManager import PropertyManager

from Products.CMFCore.utils import _checkPermission, _verifyActionPermissions
from Products.CMFCore.CMFCorePermissions import setDefaultRoles, \
     View, ManagePortal, ModifyPortalContent
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import getToolByName

from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.Expression import Expression
from zLOG import LOG, DEBUG
#from Traversal import RestrictedTRaverse

from Products.DCWorkflow.Guard import Guard
from BoxesTool import BoxContainer

def addBaseBox(dispatcher, id, REQUEST=None):
    """Add a Base Box."""
    ob = BaseBox(id)
    container = dispatcher.Destination()
    container._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)


factory_type_information = (
    {'id': 'Base Box',
     'title': 'portal_type_BaseBox_title',
     'description': 'portal_type_BaseBox_description',     
     'meta_type': 'Base Box',
     'icon': 'box.gif',     
     'product': 'CPSDefault',
     'factory': 'addBaseBox',
     'immediate_view': 'basebox_edit_form',
     'filter_content_types': 0,
     'actions': ({'id': 'view',
                  'name': 'View',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'Edit',
                  'action': 'basebox_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 {'id': 'isportalbox',
                  'name': 'isportalbox',
                  'action': 'isportalbox',
                  'visible': 0,
                  'permissions': ()},
                 ),
     },
    )


class BaseBox(PortalContent, DefaultDublinCoreImpl, PropertyManager):
    """
    Base class for boxes.
    """

    isPortalBox = 1
    meta_type = 'Base Box'
    portal_type = 'Base Box'

    manage_options = ( PropertyManager.manage_options +
                       ({'label': 'Guard', 'action': 'manage_guardForm'},) +
                       PortalContent.manage_options[:1] +
                       PortalContent.manage_options[3:]
                       )

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    guard = None

    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w', 'label': 'Title'},
        {'id': 'minimized', 'type': 'boolean', 'mode': 'w', 'label': 'Minimized'},
        {'id': 'closed', 'type': 'boolean', 'mode': 'w', 'label': 'Closed'},
        {'id': 'style', 'type': 'string', 'mode': 'w', 'label': 'Style'},
        {'id': 'format', 'type': 'string', 'mode': 'w', 'label': 'Display format'},
        {'id': 'slot', 'type': 'string', 'mode': 'w', 'label': 'Slot'},
        {'id': 'order', 'type': 'int', 'mode': 'w', 'label': 'Order'},
        {'id': 'visible_if_empty', 'type': 'boolean', 'mode': 'w', 'label': 'Visible if empty'},
        {'id': 'display_in_subfolder', 'type': 'boolean', 'mode': 'w', 'label': 'Display in sub folder'},
        {'id': 'locked', 'type': 'boolean', 'mode': 'w', 'label': 'Locked box'},
        )

    def __init__(self, id, title='', macro='basebox', minimized=0, closed=0,
                 style='nuxeo', format='default', slot='left', order=0,
                 visible_if_empty=0, display_in_subfolder=1,
                 locked=0, **kw):
        DefaultDublinCoreImpl.__init__(self)
        self.id = id
        self.title = title
        self.macro = macro
        self.style = style
        self.format = format
        self.slot = slot
        self.order = int(order)
        self.minimized = minimized
        self.closed = closed

        self.visible_if_empty = visible_if_empty
        self.display_in_subfolder = display_in_subfolder
        self.locked = locked

    #
    # ZMI
    #
    security.declarePublic('manage_guardForm') # XXX protect
    manage_guardForm = DTMLFile('zmi/manage_guardForm', globals())

    security.declareProtected('setGuardProperties', ModifyPortalContent)
    def setGuardProperties(self, REQUEST=None):
        """ """
        g = Guard()
        if g.changeFromProperties(REQUEST):
            self.guard = g
        else:
            self.guard = None
        if REQUEST is not None:
            return self.manage_guardForm(REQUEST,
                management_view='Guard',
                manage_tabs_message='Guard setting changed')

    #
    # Public API
    #
    security.declarePublic('getSettings')
    def getSettings(self):
        """Return a dictionary of properties that can be overriden"""
        return {'slot': self.slot,
                'order': self.order,
                'minimized': self.minimized,
                'closed': self.minimized,
                'style': self.style,
                'format': self.format,
                }

    security.declareProtected(ModifyPortalContent, 'edit')
    def edit(self, **kw):
        """
        Default edit method, changes the properties.
        """
        self.manage_changeProperties(**kw)

    #
    # Internal API's mainly called from itself or other Zope tools
    #
    def getGuard(self):
        if self.guard is not None:
            return self.guard
        else:
            return Guard().__of__(self)  # Create a temporary guard.

    security.declarePrivate('callAction')
    def callAction(self, actionid, **kw):
        """
        Call the given action.
        """
        ti = self.getTypeInfo()
        if ti is not None:
            actions = ti.getActions()
            for action in actions:
                if action.get('id', None) == actionid:
                    if _verifyActionPermissions(self, action):
                        meth = self.restrictedTraverse(action['action'])
                        if getattr(aq_base(meth), 'isDocTemp', 0):
                            return apply(meth, (self, self.REQUEST), kw)
                        else:
                            return apply(meth, (), kw)
        raise 'Not Found', (
            'Cannot find %s action for "%s"' %
            (actionid, self.absolute_url(relative=1)))

    security.declarePublic('getMacro')
    def getMacro(self, style=None, format=None):
        """
        GetMacros to render the box.
        """
        if not style:
            style = self.style
        if not format:
            format = self.format
        return 'here/boxes_%s/macros/%s_%s' % (style, self.macro, format)

    security.declarePublic('render')
    def render(self, **kw):
        """
        Renders the box.
        """
        macro = self.getMacro()
        render_method = self.restrictedTraverse(macro)
        rendering = render_method(self)
        return rendering.strip()

    security.declareProtected(View, 'edit_form')
    def edit_form(self, **kw):
        """
        Call the edit action.
        """
        return self.callAction('edit', **kw)

    def manage_afterAdd(self, item, container):
        if aq_base(self) is aq_base(item):
            # sets order attribute correctly
            order_max_set = 0
            order_max = -1
            my_slot = self.slot
            for box in container.objectValues():
                slot = getattr(aq_base(box), 'slot', None)
                if slot is not None and slot == my_slot:
                    order = getattr(aq_base(box), 'order', None)
                    if order is not None:
                        if order_max_set and order_max < order:
                            order_max = order
                        elif not order_max_set:
                            order_max_set = 1
                            order_max = order
            self.order = order_max + 1

        BaseBox.inheritedAttribute('manage_afterAdd')(self, item, container)

    def minimize(self, REQUEST=None):
        """Minimize the box using personal settings"""
        self.savePersonalSettings({'minimized':1, 'closed':0})
        if REQUEST is not None:
            goto = REQUEST.get('goto')
            if goto:
                REQUEST['RESPONSE'].redirect(goto)

    def maximize(self, REQUEST=None):
        """Maximize the box using personal settings"""
        self.savePersonalSettings({'minimized':0, 'closed':0})
        if REQUEST is not None:
            goto = REQUEST.get('goto')
            if goto:
                REQUEST['RESPONSE'].redirect(goto)

    def close(self, REQUEST=None):
        """Close the box using personal settings """
        self.savePersonalSettings({'closed':1})
        if REQUEST is not None:
            goto = REQUEST.get('goto')
            if goto:
                REQUEST['RESPONSE'].redirect(goto)


    def savePersonalSettings(self, new_settings):
        """ personal override for this box """
        # find the personal boxes container pbc, create if empty
        home = getToolByName(self, 'portal_membership').getHomeFolder()
        utool = getToolByName(self, 'portal_url')
        btool = getToolByName(self, 'portal_boxes')
        box_url = utool.getRelativeUrl(self)
        idbc = BoxContainer.id_perso
        
        pbc = None
        if hasattr(aq_base(home), idbc):
            pbc = home[idbc]
        else:
            home.manage_addProduct['CPSDefault'].addBoxContainer()
            pbc = home[idbc]
            pbc.manage_permission('Manage Box Overrides',
                                  roles=('Owner','Manager','WorkspaceManager'),
                                  acquire=0)
            LOG('BaseBox', DEBUG, 'SavePersonalSettings',
                'Creating personal boxes container %s/%s\n' % (
                str(utool.getRelativeContentURL(home)), idbc))
            
        # get current override
        overrides = pbc.getOverrides()
        settings={}
        for s in overrides:
            if s['box_path'] == box_url:
                settings = s
                break
        settings.update(new_settings)

        for field in settings.keys():
            if not settings[field]:
                del settings[field]
            elif field in ('mimimized', 'order', 'closed'):
                settings[field] = int(settings[field])
        btool.setBoxOverride(box_url, settings, pbc)
        LOG('BaseBox', DEBUG,
            'SavePersonalSettings', '%s settings %s\n' % (box_url,
                                                        str(settings)))


InitializeClass(BaseBox)
