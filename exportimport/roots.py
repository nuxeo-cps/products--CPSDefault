# (C) Copyright 2005-2007 Nuxeo SAS <http://nuxeo.com>
# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
# Florent Guillaume <fg@nuxeo.com>
# M.-A. Darche <madarche@nuxeo.com>
# G. Racinet <georges@racinet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import Products

from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName

from Products.GenericSetup.utils import CONVERTER, DEFAULT, KEY
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import ImportConfiguratorBase

from Products.CPSCore.utils import ALL_LOCALES

from Products.CPSDocument.exportimport import importCPSObjects
from Products.CPSDocument.upgrade import upgrade_doc_unicode

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
                            # Test if instance is not None to be able to deal
                            # with multiple meta_type definitions defining the
                            # same meta_type and only considering the definition
                            # holding a class definition. This is for example
                            # to take advantage of the five:registerClass
                            # directive.
                            if mt_info['instance'] is not None:
                                site._setObject(id, mt_info['instance'](id))
                                break
                    else:
                        self._logger.warning("unknown meta_type '%s' for fragment \n%s", meta_type, child.toprettyxml)
                        continue

            obj = site._getOb(id)
            if meta_type:
                # GR probably intended to recurse only in non proxy objects
                # but can do it as well (unwanted in most cases).
                # Hard to tell, since profiles have been using this for
                # deeper recursion, and that's side effect programming.
                # In any case, since the changes made for #2252, this leads
                # to obscure errors. Better to break now.
                if portal_type:
                    env = self.environ
                    if hasattr(env, '_profile_path'):
                        env_info = 'directory %s' % env._profile_path
                    else:
                        env_info = str(env)

                    raise ValueError(
                        "Using meta_type attribute to force recursion in a "
                        "proxy folder (%s) is now forbidden. "
                        "If this is the intent, use the new structure import "
                        "step, see issue #2252. If not, simply remove the "
                        "meta_type attribute from %s in %s" % (
                            id, self.filename, env_info))

                self._logger.debug(
                   "_initRoots importObjects on %s with parent_path = %s"
                   % (str(obj), self.path))

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


class RootXMLAdapter(XMLAdapterBase, ObjectManagerHelpers,
                     PropertyManagerHelpers):
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
            self._purgeProperties()
            self._purgeRolemap()
            self._purgeConfigurationObjects()
        self._initRolemap(node)
        self._initI18nTitles(node)
        self._initProperties(node)
        self._initObjects(node)
        self._logger.info("%s imported." % self.context.getId())

    def _exportNode(self):
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractObjects())
        return node

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
            node.removeChild(child)  # Don't interfere with normal props  
            field_id = attribute_name.split('_', 1)[0].capitalize()
            msgid = self._getNodeText(child)
            existing_langs = proxy.getLanguageRevisions().keys()

            # #2181: upgrade to unicode is necessary if this is the
            # profile import right before the big upgrade
            # furthermore we need to do it on all languages, because
            # of the reindexing (see below)
            for lang in existing_langs:
                doc = proxy.getContent(lang=lang)
                upgrade_doc_unicode(doc)

            for lang in avail_langs:
                if lang not in existing_langs:
                    proxy.addLanguageToProxy(lang)
                value = translation_service(msgid=msgid,
                                            target_language=lang,
                                            default=msgid)
                doc = proxy.getEditableContent(lang=lang)
                doc_def = {field_id: value, 'proxy': proxy}
                doc.edit(**doc_def)

            catalog = getToolByName(self.context, 'portal_catalog')
            # #2181: we need to unindex it right now, because at the
            # edge of unicode, reindexing can cause UnicodeErrors in
            # Products.ZCatalog.Catalog#updateMetaData
            # the before commit hook will index it properly at the end
            # this cannot work before the Catalog import step has been done
            # and is necessary if it's imported in the same transaction
            catalog.unindexObject(proxy)

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
