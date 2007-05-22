# (C) Copyright 2005-2007 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Florent Guillaume <fg@nuxeo.com>
# M.-A. Darche <madarche@nuxeo.com>
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
"""CPS Default GenericSetup I/O.
"""

from Acquisition import aq_base

import Products

from Products.StandardCacheManagers.AcceleratedHTTPCacheManager \
     import AcceleratedHTTPCacheManager
from Products.CMFCore.utils import getToolByName

from Products.GenericSetup.utils import CONVERTER, DEFAULT, KEY
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import ImportConfiguratorBase
from Products.GenericSetup.utils import importObjects

from Products.CPSCore.utils import ALL_LOCALES
from Products.CPSWorkflow.workflowtool import LOCAL_WORKFLOW_CONFIG_ID
from Products.CPSWorkflow.configuration import (
    addConfiguration as addLocalWorkflowConfiguration)
from Products.CPSWorkflow.exportimport import (
    LocalWorkflowConfigurationXMLAdapter)

from Products.Localizer.exportimport import importLocalizer
from Products.CPSDocument.exportimport import importCPSObjects


class VariousImporter(object):
    """Class to import various steps.

    For steps that have not yet been separated into their own
    component. Note that this should be able to run as an extension
    profile, without purge and with potentially missing files.
    """

    catalogs = (
        # domain, localizer catalog
        ('default', 'default'),
        ('cpsskins', 'cpsskins'),
        #('cpscollector', 'cpscollector'),
        #('RSSBox', 'cpsrss'),
        )

    default_roles = ('Manager', 'Member')

    members_folder = 'members'

    def __init__(self, context):
        self.context = context
        self.site = context.getSite()

    def importVarious(self):
        """Import various non-exportable settings.

        Will go away when specific handlers are coded for these.
        """
        self.setupTranslationService()
        self.setupRoots()
        self.setupDefaultRoles()
        return "Various settings imported."

    def setupDefaultRoles(self):
        """Add the default roles to the roles directory
        """
        dtool = getToolByName(self.site, 'portal_directories')
        for role in self.default_roles:
            if not dtool['roles']._hasEntry(role):
                dtool['roles']._createEntry({'role': role, 'members': []})

    def setupTranslationService(self):
        ts = getToolByName(self.site, 'translation_service')
        ts._p_changed = 1
        ts._domain_dict[None] = 'Localizer/default'
        present = [i[0] for i in ts.getDomainInfo()]
        for domain, catalog in self.catalogs:
            if domain in present:
                continue
            ts.manage_addDomainInfo(domain, 'Localizer/%s' % catalog)
        ts._resetCache()

    def setupRoots(self):
        importer = RootsXMLAdapter(self.site, self.context)
        filename = importer.name + importer.suffix
        body = self.context.readDataFile(filename)
        if body is None:
            return
        importer.filename = filename
        importer.path = importer.name
        importer.body = body


# Called according to import_steps.xml
def importVarious(context):
    importer = VariousImporter(context)
    importer.importVarious()


def importLocalizerAndClearCaches(context):
    """Call the Localizer importer and then clear the portlets tool caches.

    That way all the portlets take advantage of the new translations.
    """
    site = context.getSite()
    importLocalizer(context)
    portlets_tool = getToolByName(site, 'portal_cpsportlets')
    portlets_tool.clearCache()


class RootsXMLAdapter(XMLAdapterBase):
    _LOGGER_ID = 'roots'
    name = 'roots'

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeRoots()
        self._initRoots(node)
        self._logger.info("Roots imported.")

    def _purgeRoots(self):
        return

    def _initRoots(self, node):
        site = self.context
        avail_langs = site.getProperty('available_languages', ALL_LOCALES)
        for child in node.childNodes:
            if child.nodeName != 'object':
                continue

            id = str(child.getAttribute('name'))
            portal_type = str(child.getAttribute('portal_type'))
            meta_type = str(child.getAttribute('meta_type'))

            # Create object if needed
            if getattr(aq_base(site), id, None) is None:
                # If this is a CPS document such as a Workspace or a Section
                if portal_type:
                    language = str(child.getAttribute('language'))
                    if language not in avail_langs:
                        language = None
                    wftool = getToolByName(site, 'portal_workflow')
                    wftool.invokeFactoryFor(site, portal_type, id,
                                            language=language)
                else:
                    # This is not a CPS document such as a Workspace or a
                    # Section and thus it can be dealt with in a generic manner.
                    for mt_info in Products.meta_types:
                        if mt_info['name'] == meta_type:
                            site._setObject(id, mt_info['instance'](id))
                            break
                    else:
                        raise ValueError("unknown meta_type '%s'" % meta_type)

            obj = site._getOb(id)

            if meta_type:
                #self._logger.debug(
                #    "_initRoots importObjects on %s with parent_path = %s"
                #    % (str(obj), self.path))
                # Import subobjects recursively
                importObjects(obj, self.path + '/', self.environ)
                # Move on to the next root object
                continue

            # Placeful configuration for one root object
            # (and subobjects creation).
            path = self.path + '/' + id
            filename = path + '.xml'

            body = self.environ.readDataFile(filename)
            if body is not None:
                importer = RootXMLAdapter(obj, self.environ)
                importer.path = path # to load rolemap contextually
                importer.filename = filename # for error reporting
                importer.body = body

            # Recurse into configuration objects
            for subid, subob in obj.objectItems():
                if subid.startswith('.'):
                    importCPSObjects(subob, path + '/', self.environ)

            # Recursively load sub obj folders
            filename = path + '/' + self.name +  '.xml'
            body = self.environ.readDataFile(filename)
            if body is not None:
                importer = RootsXMLAdapter(obj, self.environ)
                importer.path = path + '/' + self.name
                importer.filename = filename # for error reporting
                importer.body = body


class RootXMLAdapter(XMLAdapterBase, ObjectManagerHelpers):
    """Import the subobjects of one root.
    """
    _LOGGER_ID = 'roots'
    name = 'roots'
    # following attributes must be CMF dublin core attributes
    i18n_attributes = ('title', 'description')

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeRolemap()
            self._purgeConfigurationObjects()
        self._initRolemap(node)
        self._initI18nTitles(node)
        self._initObjects(node)
        self._logger.info("%s imported." % self.context.getId())

    def _exportNode(self):
        raise NotImplementedError

    def _purgeConfigurationObjects(self):
        for id in self.context.objectIds():
            if id.startswith('.'):
                self.context._delObject(id)

    def _purgeRolemap(self):
        pass

    def _initRolemap(self, node):
        ob = self.context
        for child in node.childNodes:
            if child.nodeName != 'rolemap':
                continue
            file = str(child.getAttribute('file'))
            filename = self.path+'/'+file # self.path added by caller
            importObjectRolemap(ob, filename, self.environ)

    def _initI18nTitles(self, node):
        proxy = self.context
        site = self.environ.getSite()
        avail_langs = site.getProperty('available_languages')
        translation_service = getToolByName(site, 'translation_service')
        wanted_attributes = ['%s_msgid' % id for id in self.i18n_attributes]
        for child in node.childNodes:
            if child.nodeName != 'property':
                continue
            attribute_name = str(child.getAttribute('name'))
            if attribute_name not in wanted_attributes:
                continue
            field_id = attribute_name.split('_', 1)[0].capitalize()
            msgid = self._getNodeText(child)
            existing_langs = proxy.getLanguageRevisions().keys()
            for lang in avail_langs:
                if lang not in existing_langs:
                    proxy.addLanguageToProxy(lang)
                value = translation_service(msgid=msgid,
                                            target_language=lang,
                                            default=msgid)
                doc = proxy.getEditableContent(lang=lang)
                doc_def = {field_id: value, 'proxy': proxy}
                doc.edit(**doc_def)

def importObjectLocalWorkflow(ob, filename, context):
    """Import local workflow chains from an XML file.
    """
    logger = context.getLogger('cpsworkflow')
    path = '/'.join(ob.getPhysicalPath())

    body = context.readDataFile(filename)
    if body is None:
        logger.info("No local workflow map for %s" % path)
        return

    if getattr(aq_base(ob), LOCAL_WORKFLOW_CONFIG_ID, None) is not None:
        confob = ob._getOb(LOCAL_WORKFLOW_CONFIG_ID)
    else:
        confob = addLocalWorkflowConfiguration(ob)
    importer = LocalWorkflowConfigurationXMLAdapter(confob, context)
    if importer is not None:
        importer.body = body

    logger.info("Local workflow map for %s imported." % path)


# Old-style importer for rolemap, using explicit object/filename

def importObjectRolemap(ob, filename, context):
    """Import roles / permission map from an XML file.
    """
    logger = context.getLogger('rolemap')

    if context.shouldPurge():
        items = ob.__dict__.items()
        for k, v in items:
            if k == '__ac_roles__':
                delattr(ob, k)
            if k.startswith('_') and k.endswith('_Permission'):
                delattr(ob, k)

    body = context.readDataFile(filename)
    if body is None:
        return

    rc = RolemapImportConfigurator(ob, context.getEncoding())
    info = rc.parseXML(body)

    # Roles
    immediate_roles = list(getattr(ob, '__ac_roles__', []))
    already = dict.fromkeys(ob.valid_roles(), True)
    for role in info['roles']:
        if role not in already:
            immediate_roles.append(role)
            already[role] = True
    immediate_roles.sort()
    ob.__ac_roles__ = tuple(immediate_roles)

    # Permission map
    for permission in info['permissions']:
        ob.manage_permission(permission['name'],
                             permission['roles'],
                             permission['acquire'])

    logger.info("Role/permission map for %s imported." % ob.getId())


# Old-style configurator

class RolemapImportConfigurator(ImportConfiguratorBase):
    def _getImportMapping(self):
        return {
            'rolemap': {
                'roles': {CONVERTER: self._convertToUnique, DEFAULT: ()},
                'permissions': {CONVERTER: self._convertToUnique},
                },
            'roles': {
                'role': {KEY: None, DEFAULT: ()},
                },
            'role': {
                'name': {KEY: None},
                },
            'permissions': {
                'permission': {KEY: None, DEFAULT: ()},
                },
            'permission': {
                'name': {},
                'role': {KEY: 'roles'},
                'acquire': {CONVERTER: self._convertToBoolean},
                },
            }


"""
 product=CPSCollector cat=cpscollector
 product=CPSSchemas cat=default
 product=CPSDocument cat=default
 product=CPSForum cat=default
 product=CPSChat cat=default
 product=CPSDirectory cat=default
 product=CPSNavigation cat=default
 product=CPSSubscriptions cat=default
 product=CalZope cat=default
 product=CPSSharedCalendar cat=default
 product=CPSNewsLetters cat=default
 product=CPSWiki cat=default
 product=CPSPortlets cat=default
 product=CPSOOo cat=default
 product=CPSDefault cat=default
"""
