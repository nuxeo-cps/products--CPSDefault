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
  BoxesTool
"""

__version__='$Revision$'[11:-2]

from zLOG import LOG, DEBUG

import string
from DateTime import DateTime
from Globals import InitializeClass, DTMLFile

from AccessControl import ClassSecurityInfo, getSecurityManager, Unauthorized
from AccessControl.PermissionRole import rolesForPermissionOn
from Acquisition import aq_inner, aq_parent, aq_chain, aq_base
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem

from Products.ZCatalog.ZCatalog import ZCatalog
from Products.CMFCore.CMFCorePermissions import setDefaultRoles, \
     View, AccessContentsInformation, ManagePortal
from Products.CMFCore.utils import UniqueObject, getToolByName, \
     _checkPermission
from Products.CMFCore.ActionProviderBase import ActionProviderBase


def cmporderbox(a, b):
    return cmp(a.xpos, b.xpos) or cmp(a.ypos, b.ypos)


class BoxesTool(ActionProviderBase, UniqueObject, SimpleItem):
    """
    Boxes Tool.
    """
    id = 'portal_boxes'
    meta_type = 'CPS Boxes Tool'

    security = ClassSecurityInfo()

    manage_options = (
        ({'label': "Overview", 'action': 'manage_overview',},) +
        ActionProviderBase.manage_options +
        SimpleItem.manage_options
        )

    #
    # ZMI
    #

    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('zmi/explainBoxesTool', globals())

    #
    # Public API
    #

    security.declarePublic('getBoxTypes')
    def getBoxTypes(self, container=None):
        """
        Gets all Box types allowed in container.
        Returns a sequence of (id, title).
        """
        ttool = getToolByName(self, 'portal_types')
        tilist = ttool.listTypeInfo(container)
        res = []
        for ti in tilist:
            if ti.getActionById('isportalbox', None):
                d = {
                    'id': ti.getId(),
                    'title': ti.Title(),
                    }
                res.append(d)
        return res

    security.declarePublic('getBoxTypesList')
    def getBoxTypesList(self, container=None):
        ttool = getToolByName(self, 'portal_types')
        tilist = ttool.listTypeInfo(container)
        all_box_types = []
        for ti in tilist:
            if ti.getActionById('isportalbox', None):
                all_box_types.append(ti.getId())
        return all_box_types

    security.declarePublic('searchBoxes')
    def searchBoxes(self, context, xpos=None, alsoclosed=0, noacquire=0):
        all_box_types = self.getBoxTypesList()

        if noacquire:
            container = self.getBoxesContainer(context)
            containerparent = container.aq_parent
            paths = [containerparent.getPhysicalPath()]
        else:
            paths = []
            path = ()
            for each in context.getPhysicalPath():
                path = path + (each,)
                paths.append(path[:])

        query = { 'portal_type': all_box_types,
                  'parent_path': paths,
                  'sort_on': 'sort_order',
                }
        if xpos is not None:
            query['xpos'] = xpos

        if not alsoclosed:
            query['is_closed'] = 0

        catalog = getToolByName(self, 'portal_catalog')
        res = catalog.searchResults(query)
        return res

    security.declarePublic('getBoxesDict')
    def getBoxesDict(self, context, xpos=None, alsoclosed=0, permission = 'View'):
        """
        Gets all the boxes of a user
        Returns a dict { boxid: box }
        """
        boxes = self.searchBoxes(context, xpos=xpos, alsoclosed=alsoclosed)
        mapping = {}
        if permission is not None:
            securityManager = getSecurityManager()
        for box in boxes:
            if permission is not None and not \
               securityManager.checkPermission(permission, box):
                continue
            mapping[box.id] = box.getObject()
        return mapping

    security.declarePublic('getBoxes')
    def getBoxes(self, context, xpos=None, alsoclosed=0, permission = 'View', noacquire=0):
        boxes = self.searchBoxes(context, xpos=xpos, alsoclosed=alsoclosed, noacquire=noacquire)
        result = []
        if permission is not None:
            securityManager = getSecurityManager()
        for box in boxes:
            if permission is not None and not \
               securityManager.checkPermission(permission, box):
                continue
            result.append(box.getObject())
        return result

    security.declarePublic('setBoxState')
    def setBoxState(self, context, boxid, state):
        """
        Sets the box state, in the private box container.
        """
        # XXX should we do any security check ?
        box = self.getBoxForId(context, boxid)
        response = None
        changed_indexes = []
        if box is not None:
            valid_states = self.get_valid_states()
            valid_keys = valid_states.keys()
            for key, value in state.items():
                if key in valid_keys:
                    can_change_key = getattr(box, 'can_' + key)
                    if callable(can_change_key):
                        can_change_key = can_change_key()
                    if can_change_key:
                        if valid_states[key] == 'bool':
                            if value:
                                value='on'
                            else:
                                value=''
                        if valid_states[key] == 'int':
                            value = int(value)
                        if key == 'style':
                            can_minimized = 0
                            meth = getattr(self, 'boxes_styles_get', None)
                            if meth is not None:
                                styles = self.boxes_styles_get()
                                for style in styles:
                                    if style['id'] == value:
                                        can_minimized = style.get('can_minimized')
                                        break
                            box._can_minimized = can_minimized
                        if key == 'minimized':
                            cookie_name = '%s_%s' % (box.cps_prefId(), key)
                            if response is None:
                                response = self.REQUEST.RESPONSE
                            response.setCookie(cookie_name, value, expires= (DateTime()+365).toZone('GMT').rfc822())
                        else:
                            setattr(box, key, value)
                            changed_indexes.append(key)
            if changed_indexes:
                box.reindexObject(changed_indexes)

    security.declarePublic('getBoxForId')
    def getBoxForId(self, context, boxid):
        types = self.getBoxTypesList()
        query = { 'portal_type': types,
                  'id': boxid,
                }
        catalog = getToolByName(self, 'portal_catalog')
        res = catalog.searchResults(query)
        if len(res) == 0:
            raise Exception('Portal box with ID %s not found' % str(boxid))
        if len(res) != 1:
            raise Exception('More than one portal box with ID %s found. Please rename one.' % str(boxid))
        return res[0].getObject()

    security.declarePublic('delBox')
    def delBox(self, context, boxid):
        container = self.getBoxesContainer(context)
        if container is None:
            return

        mtool = getToolByName(self, 'portal_membership')
        if not mtool.checkPermission('Delete objects', container):
            raise Unauthorized
        container._delObject(boxid)

    security.declarePublic('getBoxesContainer')
    def getBoxesContainer(self, context):
        """Get the first boxes container for context

        Personal boxes can get retrieved by sending the
        portal_preferences.getUserPreferences container as the context.
        """
        if hasattr(context, '.cps_boxes'):
            f = getattr(context, '.cps_boxes', None)
            if f is not None:
              return f
        return None

    #
    # Private
    #

    security.declarePrivate('getDefaultState')
    def getDefaultState(self):
        """Returns the default state."""
        return self._default_state.copy()

    _default_state = {
        'closed': 0,
        'minimized': 0,
        'xpos': 1,
        'ypos': 0,
        'style': '',
        }

    security.declarePublic('get_valid_states')
    def get_valid_states(self):
        return {
                'closed': 'bool',
                'minimized': 'bool',
                'xpos': 'int',
                'ypos': 'int',
                'style': 'text'
               }


InitializeClass(BoxesTool)

