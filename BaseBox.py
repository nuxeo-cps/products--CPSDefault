# (c) 2002 Nuxeo SARL <http://nuxeo.com>
# (c) 2002 Florent Guillaume <mailto:fg@nuxeo.com>
# (c) 2002 Julien Jalon <mailto:jj@nuxeo.com>
# (c) 2002 Préfecture du Bas-Rhin, France
# (c) 2002 CIRB, Belgique
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

__version__='$Revision$'[11:-2]

from zLOG import LOG, DEBUG
import string

from Globals import InitializeClass
from AccessControl import getSecurityManager, ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner

from OFS.PropertyManager import PropertyManager

from Products.CMFCore.utils import _checkPermission, _verifyActionPermissions
from Products.CMFCore.CMFCorePermissions import setDefaultRoles, \
     View, ManagePortal, ModifyPortalContent
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import getToolByName

from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

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
     'content_icon': 'box_icon.gif',
     'product': 'NuxPortal2',
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
                       PortalContent.manage_options[:1] +
                       PortalContent.manage_options[3:]
                       )

    security = ClassSecurityInfo()

    _can_minimized = None
    
    _properties = (
        {'id': 'minimized', 'type': 'boolean', 'mode': 'w', 'label': 'Minimized'},
        {'id': 'closed', 'type': 'boolean', 'mode': 'w', 'label': 'Closed'},
        {'id': 'visible_if_empty', 'type': 'boolean', 'mode': 'w', 'label': 'Visible if empty'},
        {'id': 'style', 'type': 'string', 'mode': 'w', 'label': 'Style'},
        {'id': 'xpos', 'type': 'int', 'mode': 'w', 'label': 'XPos'},
        {'id': 'ypos', 'type': 'int', 'mode': 'w', 'label': 'YPos'}
        )

    visible_if_empty = 0

    security.declarePublic('can_edit')
    def can_edit(self):
        """
        determine if the box can be minimized
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
        determine if the box can be minimized
        """
        return _checkPermission(ModifyPortalContent, self)

    security.declarePublic('can_style')
    def can_style(self):
        """
        determine if the box can be minimized
        """
        return _checkPermission(ModifyPortalContent, self)

    security.declarePublic('can_xpos')
    def can_xpos(self):
        """
        determine if the box can be minimized
        """
        return _checkPermission(ModifyPortalContent, self)

    security.declarePublic('can_ypos')
    def can_ypos(self):
        """
        determine if the box can be minimized
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

    def cps_prefId(self):
        return 'bx_' + self.getId()
    
    def __init__(self, id, minimized=0, closed=0, style='', xpos=1, ypos=0, **kw):
        self.id = id
        self.minimized = minimized
        self.closed = closed
        self.style = style
        self.xpos = int(xpos)
        self.ypos = int(ypos)
        DefaultDublinCoreImpl.__init__(self)

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

    security.declareProtected(View, 'render')
    def render(self, **kw):
        """
        Renders the box.
        """
        template = self.style.strip()
        if not template:
            template = 'box_std_template'
        render_method = getattr(self, template)

        ti = self.getTypeInfo()
        if ti is not None:
            actions = ti.getActions()
        else:
            actions = ()

        getslot = SlotRender(box=self, actions=actions,
                             kw=kw.copy(), verif=_verifyActionPermissions)

        if getattr(aq_base(render_method), 'isDocTemp', 0):
            rendering = render_method(self, self.REQUEST, getslot=getslot)
        else:
            rendering = render_method(getslot=getslot)
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

            # sets ypos attribute correctly
            ypos_max_set = 0
            ypos_max = -1
            my_xpos = self.xpos
            for box in container.objectValues():
                xpos = getattr(aq_base(box), 'xpos', None)
                if xpos is not None and xpos == my_xpos:
                    ypos = getattr(aq_base(box), 'ypos', None)
                    if ypos is not None:
                        if ypos_max_set and ypos_max < ypos:
                            ypos_max = ypos
                        elif not ypos_max_set:
                            ypos_max_set = 1
                            ypos_max = ypos
            self.ypos = ypos_max + 1

        BaseBox.inheritedAttribute('manage_afterAdd')(self, item, container)

InitializeClass(BaseBox)


class SlotRender:
    """
    Encapsulate a call to get the rendering of a slot.
    """
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, box, actions, kw, verif):
        self.box = box
        self.actions = actions
        self.kw = kw
        self.verif = verif

    def __getitem__(self, name):
        if hasattr(self, name) and not name.startswith('_'):
            return getattr(self, name)
        if self.kw.has_key(name):
            return self.kw[name]

        actionid = 'render_' + name
        for action in self.actions:
            if action.get("id", None) == actionid:
                if self.verif(self.box, action):
                    # Found an action matching the render_name; do that action
                    method = self.box.restrictedTraverse(action['action'])
                    if getattr(aq_base(method), 'isDocTemp', 0):
                        result = method(box, box.REQUEST, getslot=self, \
                                        **self.kw)
                    else:
                        result = method(getslot=self, **self.kw)
                    setattr(self, actionid, result) # Why this? /regebro
                    return result

        # Found nothing
        return None # Never returns an error. This feels wrong.../ regebro
        #raise KeyError, name # This feels better.


InitializeClass(SlotRender)

