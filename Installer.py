# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
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

# TODO: using this as a base class introduce a dependency for products
# (like CPSSchemas, CPSDdocument or CPSDirectory) that should be independent
# of CPS. So this module might go to its own product someday.

import os
from App.Extensions import getPath
from re import match
from types import TupleType, ListType
from zLOG import LOG, INFO, DEBUG

class BaseInstaller:
    """Base class for product-specific installers"""

    product_name = 'CPSDefault'
    SECTIONS_ID = 'sections'
    WORKSPACES_ID = 'workspaces'

    def __init__(self, context):
        self._log = []
        self.context = context
        self.portal = context.portal_url.getPortalObject()
        self.workspaces = self.portal[self.WORKSPACES_ID]
        self.sections = self.portal[self.SECTIONS_ID]
        self.boxtool = self.portal.portal_boxes
        self.treetool = self.portal.portal_trees


    def log(self, bla, zlog=1):
        self._log.append(bla)
        if (bla and zlog):
            LOG(self.product_name + ' install:', INFO, bla)

    def logOK(self):
        self.log(" Already correctly installed")

    def logResult(self):
        return '<html><head><title>CPSDocument Update</title></head>' \
            '<body><pre>'+ '\n'.join(self._log) + '</pre></body></html>'

    def portalHas(self, id):
        """Returns whether the portal has the object with the given Id or not.
        """
        return id in self.portal.objectIds()

    def setSkinsOnTop(self, skins):
        """Sets the given set of skins at the top of the skin layers, but
        just below the 'custom' layer.

        <skins> parameter is a sequence of (<skin_name>, <skin_path>).
        """
        all_skins = self.portal.portal_skins.getSkinPaths()
        for skin_name, skin_path in all_skins:
            if skin_name != 'Basic':
                continue
            path = [x.strip() for x in skin_path.split(',')]
            for skinLayer, layerPath in skins:
                self.log("Removing and inserting back this layer %s" % skinLayer)
                path.remove(skinLayer)
                # Insert after the custom layer which is at index 0
                path.insert(1, skinLayer)
            newPath = ', '.join(path)
            self.log("New layers = %s" % newPath)
            self.portal.portal_skins.addSkinSelection(skin_name, newPath)

    def setupCpsDocumentDependantSkins(self, skins):
        """Installs or updates the given set of skins for products having a
        dependency on CPSDocument skins.

        <skins> parameter is a sequence of (<skin_name>, <skin_path>).
        """
        precedenceAlteredSkins = list(skins)
        precedenceAlteredSkins.append(
            ('cps_document', 'Products/CPSDocument/skins/cps_document')
            )
        precedenceAlteredSkins.append(
            ('cps_default', 'Products/CPSDefault/skins/cps_default')
            )
        self.setupSkins(precedenceAlteredSkins)

    def setupCpsDependantSkins(self, skins):
        """Installs or updates the given set of skins for products having a
        dependency on CPSDefault skins.

        <skins> parameter is a sequence of (<skin_name>, <skin_path>).
        """
        precedenceAlteredSkins = list(skins)
        precedenceAlteredSkins.append(
            ('cps_default', 'Products/CPSDefault/skins/cps_default')
            )
        self.setupSkins(precedenceAlteredSkins)

    def setupSkins(self, skins):
        """Installs or updates the given set of skins.

        <skins> parameter is a sequence of (<skin_name>, <skin_path>).
        """

        new_skin_installed = 0
        for skin, path in skins:
            path = path.replace('/', os.sep)
            self.log(" FS Directory View '%s'" % skin)
            if skin in self.portal.portal_skins.objectIds():
                dv = self.portal.portal_skins[skin]
                oldpath = dv.getDirPath()
                if oldpath == path:
                    self.logOK()
                else:
                    self.log("  Correctly installed, correcting path")
                    dv.manage_properties(dirpath=path)
            else:
                new_skin_installed = 1
                self.portal.portal_skins.manage_addProduct['CMFCore'].manage_addDirectoryView(filepath=path, id=skin)
                self.log("  Creating skin")

        if new_skin_installed:
            all_skins = self.portal.portal_skins.getSkinPaths()
            for skin_name, skin_path in all_skins:
                if skin_name != 'Basic':
                    continue
                path = [x.strip() for x in skin_path.split(',')]
                path = [x for x in path if x not in skins] # strip all
                if path and path[0] == 'custom':
                    path = path[:1] + [skin[0] for skin in skins] + path[1:]
                else:
                    path = [skin[0] for skin in skins] + path
                npath = ', '.join(path)
                self.portal.portal_skins.addSkinSelection(skin_name, npath)
                self.log(" Fixup of skin %s" % skin_name)
            self.log(" Resetting skin cache")
            self.portal._v_skindata = None
            self.portal.setupCurrentSkin()

    def setupTranslations(self, default_lang=None):
        """Import .po files into the Localizer/default Message Catalog.
        default_lang can be for example 'en', 'fr' or 'nl'.
        """

        mcat = self.portal.Localizer.default
        self.log(" Checking available languages")
        podir = os.path.join('Products', self.product_name)
        popath = getPath(podir, 'i18n')
        if popath is None:
            self.log(" !!! Unable to find .po dir")
        else:
            self.log("  Checking installable languages")
            langs = []
            avail_langs = mcat.get_languages()
            self.log("    Available languages: %s" % str(avail_langs))
            for file in os.listdir(popath):
                if file.endswith('.po'):
                    m = match('^.*([a-z][a-z])\.po$', file)
                    if m is None:
                        self.log('    Skipping bad file %s' % file)
                        continue
                    lang = m.group(1)
                    if lang in avail_langs:
                        lang_po_path = os.path.join(popath, file)
                        lang_file = open(lang_po_path)
                        self.log("    Importing %s into '%s' locale" % (file, lang))
                        mcat.manage_import(lang, lang_file)
                    else:
                        self.log('    Skipping not installed locale for file %s' % file)
        if default_lang:
            mcat.manage_changeDefaultLang(default_lang)


    def setupPortalProperties(self, props):
        """Set portal properties using the ones found in the props list of
        dictionaries: ({'id': 'xxx', type: 'xxx', value: xxx}, {...}, ).
        Note that existing values don't have to specify the type."""
        for property in props:
            propId = property['id']
            propValue = property['value']
            if self.portal.hasProperty(propId):
                self.portal.manage_changeProperties({propId: propValue})
            else:
                self.portal.manage_addProperty(propId, propValue,
                                               property['type'])


    def setupSiteStructure(self, filename):
        """Load a site structure dump file and rebuild the site structure using
        it."""
        portal = self.portal

        if 'loadTree' not in portal.objectIds():
            from Products.ExternalMethod.ExternalMethod import ExternalMethod
            loadTree = ExternalMethod('loadTree',
                                      'loadTree',
                                      'CPSDefault.loadTree',
                                      'loadTree')
            portal._setObject('loadTree', loadTree)
            portal.loadTree.manage_permission('View',
                roles=['Manager'], acquire=0)
            portal.loadTree.manage_permission('Access contents information',
                roles=['Manager'], acquire=0)

        self.log(portal.loadTree(filename=filename))
    def setupDelBoxes(self, boxes_id, box_container):
        """Delete boxes with the id listed in boxes_id that are located in
        box_container."""
        existing_boxes = box_container.objectIds()

        if type(boxes_id) not in (TupleType, ListType):
            boxes_id = (boxes_id,)

        for box in boxes_id:
            if box in existing_boxes:
                box_container._delObject(box)


    def setupEditBoxes(self, boxes_props, box_container):
        """Change one or more properties of an existing box, located in the
        specified box container.
        The format describing these boxes is the same as the one you see in the
        'Export' tab, in the management screen of a box."""
        existing_boxes = box_container.objectIds()

        for box, props in boxes_props.items():
            if box in existing_boxes:
                ob = box_container[box]
                ob.manage_changeProperties(**props)


    def setupAddBoxes(self, boxes_prop, box_container):
        """Add the boxes described in the boxes_prop dictionnary into the
        specified box container.
        The format is the one from the 'Export' tab, in the management screen of
        a box."""
        portal_types = self.portal.portal_types
        existing_boxes = box_container.objectIds()

        for box, props in boxes_prop.items():
            if box in existing_boxes:
                box_container._delObject(box)
            portal_types.constructContent(props['type'], box_container, box)
            ob = box_container[box]
            ob.manage_changeProperties(**props)


    def getBoxContainer(self, parent, create=0):
        """Get a box container and create it if not found and asked for."""
        portal_boxes = self.portal.portal_boxes
        container_id = portal_boxes.getBoxContainerId(parent)
        box_container = getattr(parent, container_id, None)
        if box_container is None and create:
            parent.manage_addProduct['CPSDefault'].addBoxContainer()
            box_container = getattr(parent, container_id)
        return box_container


    def getBoxTypeConfig(self, box_types):
        """Extract box type configuration under the key 'config' in the given
        box_types dictionary.
        Because of context issues, you have to call get(Custom)BoxTypes() by
        yourself, e.g.:
            config = self.getBoxTypeConfig(self.portal.getBoxTypes())
        Or just getCustomBoxTypes() if it's enough."""
        configs = {}
        for box_type in box_types:
            types = [type for type in box_type['types'] if type.has_key('config')]
            for type in types:
                configs[type['id']] = type['config']
        return configs
