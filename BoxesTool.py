# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
"""
  BoxesTool
"""
from zLOG import LOG, DEBUG
from DateTime import DateTime
from Globals import InitializeClass, DTMLFile, MessageDialog
from types import DictType, StringType

from AccessControl import ClassSecurityInfo, getSecurityManager, Unauthorized
from Acquisition import aq_base, aq_parent, aq_inner
from OFS.SimpleItem import SimpleItem
from ZODB.PersistentMapping import PersistentMapping

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.CMFCorePermissions import setDefaultRoles, \
     View, AccessContentsInformation, ManagePortal
from Products.CMFCore.utils import UniqueObject, getToolByName, _checkPermission

ManageOverridesPermission = 'Manage Overrides'

class BoxesTool(UniqueObject, SimpleItem):
    """
    Boxes Tool.
    """
    id = 'portal_boxes'
    meta_type = 'CPS Boxes Tool'

    security = ClassSecurityInfo()

    manage_options = (
        ({'label': "Overview", 'action': 'manage_overview',},) +
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

    security.declarePublic('getBoxes')
    def getBoxes(self, context, slot=None, include_personal=1):
        """Return a sorted list of boxes
        box are loaded from root to current path
        and overriden by personal boxes folder
        return a list of dictionaries with keys:
            'box_url', 'settings', 'macro', 'box'
        """

        # Find bottom-most folder:
        obj = context
        bmf = None
        while 1:
            if obj.isPrincipiaFolderish:
                bmf = obj
                break
            parent = aq_parent(aq_inner(obj))
            if not obj or parent == obj:
                break
            obj = parent
        if not bmf:
            bmf = context

        # get boxes from root to current path
        portal_url = getToolByName(self, 'portal_url')
        rpath = portal_url.getRelativeContentPath(bmf)
        obj = portal_url.getPortalObject()
        allboxes = []
        settings = {}
        path = '/'

        for elem in ('',) + rpath:
            if elem:
                path += elem + '/'
                obj = getattr(obj, elem)
            f_boxes, f_settings = self._getFolderBoxesAndSettings(obj)
            allboxes.extend(f_boxes)
            self._updateSettings(settings, f_settings)

        home = getToolByName(self, 'portal_membership').getHomeFolder()
        if home and include_personal:
            f_boxes, f_settings = self._getFolderBoxesAndSettings(home)
            allboxes.extend(f_boxes)
            self._updateSettings(settings, f_settings)
            homepath = portal_url.getRelativeContentPath(home)
        else:
            homepath = None

        if include_personal:
            LOG('portal_boxes: home path', DEBUG, homepath)
        else:
            LOG('portal_boxes: home path', DEBUG, 'skip personal boxes')

        boxes = []
        for box in allboxes:
            # Skip it if there is no view permission
            #if not _checkPermission('View', box):
            #    continue
            if not box.getGuard().check(getSecurityManager(), None, context):
                continue
            # Only add boxes if they are to be displayed
            # in the subfolders, or if this is the root or if
            # this is the last part of the path, or if it's a
            # personal box.
            boxpath = portal_url.getRelativeContentPath(box)
            LOG('portal_boxes: box path', DEBUG, boxpath)
            if box.display_in_subfolder or \
               not rpath or \
               elem == rpath[-1] or \
               (include_personal and homepath and \
               boxpath[:len(homepath)] == homepath):
                newbox = {'path': portal_url.getRelativeUrl(box),
                          'settings': box.getSettings(),
                          'macro': box.getMacro(),
                          'box': box}
                # Override any box settings with the local settings
                # If the box isn't locked and there are overrides
                if not newbox['box'].locked and settings.get(newbox['path']):
                    newbox['settings'].update(settings[newbox['path']])
                    newbox['macro'] = newbox['box'].getMacro(newbox['settings']['style'])

                boxes.append(newbox)

        # We now have a list of all boxes that can be displayed in this context.
        # We'll now filter to only get the open boxes in the asked for slot.
        # This can not be done previously, since 'slot' and 'closed' settings
        # can be overriden by local setting
        boxes = [x for x in boxes if (not x['settings']['closed'] and
                                      (slot is None or x['settings']['slot']==slot))]

        # TODO: filter on permission ?

        # sorting
        def cmpbox(a, b):
            return a['settings']['order'] - b['settings']['order']
        boxes.sort(cmpbox)

        LOG('portal_boxes', DEBUG, 'Returned boxes:', str(boxes) + '\n')
        return boxes

    #
    # Private
    #
    security.declarePrivate('_getFolderBoxes')
    def _getFolderBoxesAndSettings(self, folder):
        """Load all boxes in a .cps_boxes folder
        load folder settings
        """
        boxes = []
        settings = {}
        folder_boxes = None
        if hasattr(aq_base(folder), '.cps_boxes'):
            folder_boxes = getattr(folder, '.cps_boxes')
            for box in folder_boxes.objectValues():
                if not hasattr(aq_base(box), 'isPortalBox'):
                    continue
                boxes.append(box)

            settings = self.getAllBoxOverrides(folder_boxes)

        if folder_boxes:
            LOG('portal_boxes', DEBUG,
                'Found boxes and settings at %s:' % folder_boxes.absolute_url(),
                "Boxes: %s\nSettings: %s\n" % (str(boxes), str(settings)))
        return boxes, settings


    security.declarePrivate('_updateSettings')
    def _updateSettings(self, set1, set2):
        """Update settings 1 with settings 2 """
        if not set2:
            return
        for k in set2.keys():
            if set1.get(k):
                set1[k].update(set2[k])
            else:
                set1[k] = set2[k]

    def setBoxOverride(self, boxurl, settings, context):
        """Allows you to override the box default settings

        boxurl is the relative url of the box (gotten from
        portal_url.getRelativeUrl(box) )

        settings is a dictionary of the settings and the values

        context is the object where defaults should be stored.
        """
        if not hasattr(aq_base(context), '_box_overrides'):
            context._box_overrides = PersistentMapping()

        # TODO: Add permission check in context
        sm = getSecurityManager()
        if not sm.checkPermission(ManageOverridesPermission, context):
            raise Unauthorized()
        # TODO: check which settings you are allowed to change
        context._box_overrides[boxurl] = settings

    security.declarePublic('getBoxOverride')
    def getBoxOverride(self, boxurl, context):
        """Gets the overridden settings for a box"""
        if not hasattr(aq_base(context), '_box_overrides'):
            return {}
        return context._box_overrides.get(boxurl, {})

    security.declarePublic('getAllBoxOverrides')
    def getAllBoxOverrides(self, context):
        """Gets all the local overrides"""
        return getattr(aq_base(context), '_box_overrides', {})


InitializeClass(BoxesTool)


class BoxContainer(PortalFolder):
    id = '.cps_boxes'
    meta_type = 'CPS Boxes Container'
    security = ClassSecurityInfo()

    manage_options = (
        (PortalFolder.manage_options[0],
        {'label': "Overrides", 'action': 'manage_boxOverridesForm',},) +
        PortalFolder.manage_options[2:]
        )

    #
    # ZMI
    #
    security.declareProtected(ManageOverridesPermission, 'manage_boxOverridesForm')
    manage_boxOverridesForm = DTMLFile('zmi/manage_boxOverridesForm', globals())

    security.declareProtected(ManageOverridesPermission, 'manage_boxOverrides')
    def manage_boxOverrides(self, submit, new_path, overrides=[], selected=[], \
                            REQUEST=None):
        """Sets overrides"""
        LOG('Box Container', DEBUG, 'manage_boxOverrides',
            'submit: %s\nselected: %s\noverrides: %s\nnew_path: %s\n' % \
            (submit, selected, str(overrides), new_path))
        if not hasattr(aq_base(self), '_box_overrides'):
            self._box_overrides = PersistentMapping()

        if submit == " Delete ":
            for each in selected:
                del self._box_overrides[each]
            message = 'Override(s) deleted.'
        elif submit == " Add new override ":
            target = self.unrestrictedTraverse(new_path, None)
            if target is None:
                message = 'Entered box could not be found'
            else:
                portal_url = getToolByName(self, 'portal_url')
                boxpath = portal_url.getRelativeContentURL(target)
                self._box_overrides[boxpath] = {}
                message = 'Override added.'
        elif submit == " Save Changes ":
            # Kill the old settings
            self._box_overrides = PersistentMapping()
            for override in overrides:
                settings = {}
                # Filter out empty settings:
                for key, item in override.items():
                    if item:
                        if key in ('order', 'minimized', 'closed'):
                            item = int(item)
                        if key == 'box_path':
                            box_path = item
                        else:
                            settings[key] = item
                LOG('Box Container', DEBUG, 'manage_boxOverrides',
                    str(settings) + '\n')
                self._box_overrides[box_path] = settings
            message = 'Settings changed.'
        else:
            message='Nothing to do.'
        if REQUEST is not None:
            return self.manage_boxOverridesForm(REQUEST,
                management_view='Overrides',
                manage_tabs_message=message)


    #
    # Management interface support functions
    #
    # These are mainly here to support the management GUI.
    # In typical usage the overrides would be set and retrieved through
    # the portal_boxes tool.
    security.declarePublic('getOverrides')
    def getOverrides(self):
        """Gets all the local overrides"""
        result = []
        overrides = getattr(aq_base(self), '_box_overrides', {})
        for key, item in overrides.items():
            override = {'box_path': key, 'slot': '', 'order': '', 'closed':'',
                        'minimized': ''}
            override.update(item)
            result.append(override)
        LOG('BoxContainer', DEBUG, 'getOverrides', str(result) + '\n' )
        return result

def addBoxContainer(self, id=None, REQUEST=None):
    """Add a Base Box.
    id is not take into account, it is define to have
    homogeneous portal creator """
    ob = BoxContainer(BoxContainer.id)
    self=self.this()
    if hasattr(aq_base(self), ob.id):
        return MessageDialog(
            title  ='Item Exists',
            message='This object already contains an %s' % ob.id,
            action ='%s/manage_main' % REQUEST['URL1'])
    self._setObject(ob.id, ob)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


InitializeClass(BoxContainer)
