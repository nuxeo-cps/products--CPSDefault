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
     'description': ('A Base Box is the most basic box.'),
     'meta_type': 'Base Box',
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
                 {'id': 'render_title',
                  'name': 'Render title',
                  'action': 'basebox_render_title',
                  'visible': 0,
                  'permissions': (View,)},
                 {'id': 'render_body',
                  'name': 'Render body',
                  'action': '',
                  'visible': 0,
                  'permissions': (View,)},
                 {'id': 'render_box',
                  'name': 'Render box',
                  'action': '',
                  'visible': 0,
                  'permissions': (View,)},
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

    manage_options = ( PropertyManager.manage_options +
                       ({'label': 'Guard', 'action': 'manage_guardForm'},) +
                       PortalContent.manage_options[:1] +
                       PortalContent.manage_options[3:]
                       )

    security = ClassSecurityInfo()
    guard = None
    _can_minimized = None
    locked = 0
    display_in_subfolder = 1
    slot = 'right'
    order = 0

    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w', 'label': 'Title'},
        {'id': 'minimized', 'type': 'boolean', 'mode': 'w', 'label': 'Minimized'},
        {'id': 'closed', 'type': 'boolean', 'mode': 'w', 'label': 'Closed'},
        {'id': 'style', 'type': 'string', 'mode': 'w', 'label': 'Style'},
        {'id': 'slot', 'type': 'string', 'mode': 'w', 'label': 'Slot'},
        {'id': 'order', 'type': 'int', 'mode': 'w', 'label': 'Order'},
        {'id': 'visible_if_empty', 'type': 'boolean', 'mode': 'w', 'label': 'Visible if empty'},
        {'id': 'display_in_subfolder', 'type': 'boolean', 'mode': 'w', 'label': 'Display in sub folder'},
        {'id': 'locked', 'type': 'boolean', 'mode': 'w', 'label': 'Locked box'},
        )

    def __init__(self, id, minimized=0, closed=0,
                 style='', slot=0, order=0,
                 visible_if_empty= 0, display_in_subfolder=1,
                 locked=0, **kw):
        DefaultDublinCoreImpl.__init__(self)
        self.id = id
        self.style = style
        self.slot = int(slot)
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

    def setGuardProperties(self, REQUEST=None):
        '''
        '''
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
                }

    def is_closed(self):
        """Returns 0 is it is closed, 1 otherwise

        This method is necessary to make sure that a 1 or a 0 is indexed
        in the catalog, even if the value of self.closed is Null or '' or
        any otehr value than 1 or 0.
        """
        return not not self.closed

    security.declarePublic('can_edit')
    def can_edit(self):
        """

        """
        return _checkPermission(ModifyPortalContent, self)


    security.declarePublic('can_minimized')
    def can_minimized(self):
        """
        determine if the box can be minimized
        """
        return self._can_minimized

    security.declarePublic('can_closed')
    def can_closed(self):
        """
        """
        return _checkPermission(ModifyPortalContent, self)

    security.declarePublic('can_style')
    def can_style(self):
        """
        """
        return _checkPermission(ModifyPortalContent, self)

    security.declarePublic('can_slot')
    def can_slot(self):
        """
        """
        return _checkPermission(ModifyPortalContent, self)

    security.declarePublic('can_order')
    def can_order(self):
        """
        """
        return _checkPermission(ModifyPortalContent, self)

    security.declarePublic('can_delete')
    def can_delete(self):
        """
        determine if the box can be deleted
        """
        return _checkPermission('Delete objects', aq_parent(aq_inner(self)))

    security.declarePublic('is_minimized')
    def is_minimized(self):
        request = self.REQUEST
        cookie_name = '%s_minimized' % (self.cps_prefId(), )
        return request.cookies.get(cookie_name)

    security.declarePublic('getIconRelative')
    def getIconRelative(self):
        """
        Gets the Icon path, relative to the portal.
        This is needed to catalog correctly in the presence of VHM.
        """
        return self.getIcon(1)

    security.declareProtected(ModifyPortalContent, 'edit')
    def edit(self, **kw):
        """
        Default edit method, changes the properties.
        """
        self.manage_changeProperties(**kw)

    #
    # Internal API's mainly called from itself or other Zope tools
    #

    def cps_prefId(self):
        return 'bx_' + self.getId()

    def getGuard(self):
        if self.guard is not None:
            return self.guard
        else:
            return Guard().__of__(self)  # Create a temporary guard.

    def sort_order(self):
        return ('/'.join(self.getPhysicalParentPath()), self.slot)

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

    security.declareProtected(View, 'getMacro')
    def getMacro(self, style=None):
        """
        GetMacros to render the box.
        """
        ti = self.getTypeInfo()
        if ti is None:
            raise Exception('No portal type found for box: %s' % self.getId())

        template_name = ti.getActionById('render_box')
        if not template_name:
            raise Exception('No render template for box: %s' % self.getId())
        if style is None:
            style = self.style
        return 'here/%s/macros/%s' % (template_name, style)

    security.declareProtected(View, 'render')
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
            # sets _can_minimized attribute
            meth = getattr(self, 'boxes_styles_get', None)
            if meth is not None:
                my_style = self.style
                styles = meth()
                for style in styles:
                    if style['id'] == my_style:
                        self._can_minimized = style.get('can_minimized')

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

InitializeClass(BaseBox)
