# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
"""
  BoxesTool
"""
import string
from DateTime import DateTime
from Globals import InitializeClass, DTMLFile
from types import DictType

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
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
    security.declarePublic('getBoxes')
    def getBoxes(self, context, xpos=None):
        """Return a sorted list of boxes
        box are loaded from root to current path
        and overriden by personal boxes folder
        return a list of:
            [box_id, settings, macro_path, box_object]
        """
        if xpos == 'left':
            xpos = 0
        elif xpos == 'center':
            xpos = 1
        elif xpos == 'right':
            xpos = 2
            
        # get boxes from root to current path
        portal_url = getToolByName(self, 'portal_url')
        rpath = portal_url.getRelativeContentPath(context)
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

            for box in f_boxes:
                boxes.append(['%s%s'%(path, box.getId()),
                              box.getSettings(),
                              box.getMacro(),
                              box])
            self._updateSettings(settings, f_settings)
                                        
        # TODO: add get .cps_boxes for member
        # obj = self.restrictedTraverse( '~/.cps_boxes')
        # f_boxes, f_settings = self._getFolderBoxesAndSettings(obj)
        # ...

        # final settings
        for box in boxes:
            # box[0] box_id
            # box[1] settings dict
            # box[2] macro path
            # box[3] box object            
            if settings.get(box[0]):
                box[1].update(settings[box[0]])
                box[2].getMacro(box[1]['style'])

        # filtering on xpos
        if xpos is not None:
            boxes = [x for x in boxes if (x[1]['xpos']==xpos)]

        # sorting
        def cmpbox(a, b):
            return (a[1]['xpos']*100 + a[1]['ypos']) - \
                   (b[1]['xpos']*100 + b[1]['ypos'])

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
                if type(folder_settings) is DictType:
                    # XXX TODO check integrity of a folder_setting
                    settings = folder_settings

        return boxes, settings


    security.declarePrivate('_getFolderBoxes')
    def _updateSettings(self, set1, set2):
        """Update settings 1 with settings 2 """
        # TODO not yet tested !
        if not set2:
            return
        for k in set2.keys():
            if set1.get(k):
                set1[k].update(set2[k])
            else:
                set1[k] = set2[k]

InitializeClass(BoxesTool)

