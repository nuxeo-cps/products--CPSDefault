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
  BaseBox
"""

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from OFS.PropertyManager import PropertyManager

from Products.CMFCore.utils import _verifyActionPermissions
from Products.CMFCore.CMFCorePermissions \
    import View, ModifyPortalContent, ManagePortal
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import getToolByName

from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from zLOG import LOG, DEBUG

from Products.DCWorkflow.Guard import Guard

## monkey patch to add properties in portal_types

from AccessControl.PermissionRole import PermissionRole
from Products.CMFCore.TypesTool import TypeInformation
from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
from Products.CMFCore.CMFCorePermissions import ManageProperties

TypeInformation.manage_propertiesForm = PropertyManager.manage_propertiesForm
TypeInformation.manage_addProperty__roles__ = PermissionRole(ManageProperties)
TypeInformation.manage_delProperties__roles__ = PermissionRole(ManageProperties)

ftiprops_ids = [p['id'] for p in FTI._properties]

if 'cps_is_portalbox' not in ftiprops_ids:
    FTI._properties = FTI._properties + (
        {'id':'cps_is_portalbox', 'type': 'boolean', 'mode':'w',
         'label':'CPS Portal Box'},
        )
    FTI.cps_is_portalbox = 0
## end of monkey patch

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
                  'name': 'action_view',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'action_edit',
                  'action': 'basebox_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 ),
     # additionnal cps stuff
     'cps_is_portalbox': 1,
     },
    )


class BaseBox(PortalContent, DefaultDublinCoreImpl, PropertyManager):
    """
    Base class for boxes.
    """

    isPortalBox = 1
    meta_type = 'Base Box'
    portal_type = 'Base Box'

    manage_options = (PropertyManager.manage_options +
                      ({'label': 'Guard', 'action': 'manage_guardForm'},) +
                      PortalContent.manage_options[:1] +
                      PortalContent.manage_options[3:] +
                      ({'label': 'Export', 'action': 'manage_export'},)
                     )

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    guard = None

    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w', 'label': 'Title'},

        {'id': 'provider', 'type': 'string', 'mode': 'w', 'label': 'Provider'},
        {'id': 'btype', 'type': 'string', 'mode': 'w', 'label': 'type of box'},

        {'id': 'box_skin', 'type': 'string', 'mode': 'w',
         'label': 'skin of the box'},
        {'id': 'minimized', 'type': 'boolean', 'mode': 'w',
         'label': 'Minimized'},
        {'id': 'closed', 'type': 'boolean', 'mode': 'w', 'label': 'Closed'},
        {'id': 'slot', 'type': 'string', 'mode': 'w', 'label': 'Slot'},
        {'id': 'order', 'type': 'int', 'mode': 'w', 'label': 'Order'},
        {'id': 'display_in_subfolder', 'type': 'boolean', 'mode': 'w',
         'label': 'Display in sub folder'},
        {'id': 'display_only_in_subfolder', 'type': 'boolean', 'mode': 'w',
         'label': 'Display only in sub folder'},
        {'id': 'locked', 'type': 'boolean', 'mode': 'w',
         'label': 'Locked box'},
        )

    def __init__(self, id, title='', category='basebox',
                 box_skin='here/box_lib/macros/mmcbox',
                 minimized=0, closed=0,
                 provider='nuxeo', btype='default', slot='creation_slot',
                 order=0,
                 display_in_subfolder=1,
                 display_only_in_subfolder=0, locked=0, **kw):
        DefaultDublinCoreImpl.__init__(self)
        self.id = id
        self.title = title
        self.category = category
        self.provider = provider
        self.box_skin = box_skin
        self.btype = btype
        self.slot = slot
        self.order = int(order)
        self.minimized = minimized
        self.closed = closed

        self.display_in_subfolder = display_in_subfolder
        self.display_only_in_subfolder = display_only_in_subfolder
        self.locked = locked

    #
    # ZMI
    #
    security.declareProtected(ManagePortal, 'manage_export')
    manage_export = DTMLFile('zmi/box_export', globals())

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
                'provider': self.provider,
                'btype': self.btype,
                'order': self.order,
                'minimized': self.minimized,
                'closed': self.closed,
                'box_skin': self.box_skin,
                }

    security.declareProtected('Manage Boxes', 'edit')
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
    def getMacro(self, provider=None, btype=None):
        """
        GetMacros to render the box.
        """
        if not provider:
            provider = self.provider
        if not btype:
            btype = self.btype
        return 'here/boxes_%s/macros/%s_%s' % (provider, self.category, btype)

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
        btool = getToolByName(self, 'portal_boxes')
        box_url = getToolByName(self, 'portal_url').getRelativeUrl(self)
        btool.updatePersonalBoxOverride(box_url,
                                     {'minimized':1, 'closed':0})
        if REQUEST is not None:
            goto = REQUEST.get('goto')
            if goto:
                REQUEST['RESPONSE'].redirect(goto)

    def maximize(self, REQUEST=None):
        """Maximize the box using personal settings"""
        btool = getToolByName(self, 'portal_boxes')
        box_url = getToolByName(self, 'portal_url').getRelativeUrl(self)
        btool.updatePersonalBoxOverride(box_url,
                                        {'minimized':0, 'closed':0})
        if REQUEST is not None:
            goto = REQUEST.get('goto')
            if goto:
                REQUEST['RESPONSE'].redirect(goto)

    def close(self, REQUEST=None):
        """Close the box using personal settings """
        btool = getToolByName(self, 'portal_boxes')
        box_url = getToolByName(self, 'portal_url').getRelativeUrl(self)
        btool.updatePersonalBoxOverride(box_url,
                                        {'closed':1})
        if REQUEST is not None:
            goto = REQUEST.get('goto')
            if goto:
                REQUEST['RESPONSE'].redirect(goto)


InitializeClass(BaseBox)
