# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
"""
  BoxesTool
"""
import string
from DateTime import DateTime
from Globals import InitializeClass, DTMLFile
from types import DictType, StringType

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.CMFCorePermissions import setDefaultRoles, \
     View, AccessContentsInformation, ManagePortal
from Products.CMFCore.utils import UniqueObject, getToolByName

from zLOG import LOG, DEBUG


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
    #security.declarePublic('getBoxes')
    #def getBoxes(self, context, slot=None):
    #    boxesinfo = self.getBoxesInfo(context, slot)
    #    return [info['box'] for info in boxesinfo]


    security.declarePublic('getBoxes')
    def getBoxes(self, context, slot=None):
        """Return a sorted list of boxes
        box are loaded from root to current path
        and overriden by personal boxes folder
        return a list of:
            [box_id, settings, macro_path, box_object]
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
        boxes = []
        settings = {}
        path = '/'

        for elem in ('',) + rpath:
            if elem:
                path += elem + '/'
                obj = getattr(obj, elem)
            f_boxes, f_settings = self._getFolderBoxesAndSettings(obj)
            if len(f_boxes):
                LOG('portal_boxes', DEBUG, '.cps_boxes found in %s' % path)
            if len(f_settings):
                LOG('portal_boxes', DEBUG, 'got settings in %s: %s' % (
                    path, str(f_settings)))
            LOG('portal_boxes', DEBUG, 'isPrincipiaFolderish: ' + str(obj.isPrincipiaFolderish))

            for box in f_boxes:
                # boxes should be visible if they are to be displayed
                # in the subfolder, or if this is the root or if
                # this is the last part of the path.
                if box.display_in_subfolder or not rpath or elem == rpath[-1]:
                    boxes.append({'path': portal_url.getRelativeUrl(box),
                                'settings': box.getSettings(),
                                'macro': box.getMacro(),
                                'box': box})
            self._updateSettings(settings, f_settings)

        # TODO: add get .cps_boxes for member
        # obj = self.restrictedTraverse( '~/.cps_boxes')
        # f_boxes, f_settings = self._getFolderBoxesAndSettings(obj)
        # ...

        # final settings
        for box in boxes:
            if not box['box'].locked and settings.get(box['path']):
                box['settings'].update(settings[box['path']])
                box[macr] = box[box].getMacro(box['settings']['style'])

        # TODO filter on display_in_subfolder

        # filtering on closed, slot
        boxes = [x for x in boxes if (not x['settings']['closed'] and
                                      (slot is None or x['settings']['slot']==slot))]

        # TODO filter on guard_roles

        # sorting
        def cmpbox(a, b):
            return a['settings']['order'] - b['settings']['order']

        boxes.sort(cmpbox)

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
        if hasattr(aq_base(folder), '.cps_boxes'):
            folder_boxes = getattr(folder, '.cps_boxes')
            for box in folder_boxes.objectValues():
                if not box.isPortalBox:
                    continue
                boxes.append(box)

            if hasattr(aq_base(folder_boxes), 'settings'):
                folder_settings = getattr(folder_boxes, 'settings')
                if type(folder_settings) is StringType:
                    # XXX TODO find another way without eval
                    # for security reasons
                    folder_settings = eval(folder_settings)
                if type(folder_settings) is DictType:
                    # XXX TODO check integrity of a folder_setting
                    settings = folder_settings

        return boxes, settings


    security.declarePrivate('_getFolderBoxes')
    def _updateSettings(self, set1, set2):
        """Update settings 1 with settings 2 """
        if not set2:
            return
        for k in set2.keys():
            if set1.get(k):
                set1[k].update(set2[k])
            else:
                set1[k] = set2[k]

InitializeClass(BoxesTool)

