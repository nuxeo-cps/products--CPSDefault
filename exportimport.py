# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ImportConfiguratorBase
from Products.GenericSetup.utils import CONVERTER, DEFAULT, KEY

from Products.CPSWorkflow.configuration import (
    addConfiguration as addLocalWorkflowConfiguration)
from Products.CPSWorkflow.exportimport import (
    LocalWorkflowConfigurationXMLAdapter)

class VariousImporter(object):

    catalogs = (
        # domain, localizer catalog
        ('default', 'default'),
        ('cpsskins', 'cpsskins'),
        #('cpscollector', 'cpscollector'),
        #('RSSBox', 'cpsrss'),
        )

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
        self.setupMembershipTool()
        return "Various settings imported."

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
        importer.filename = filename
        importer.body = body

    def setupMembershipTool(self):
        mtool = getToolByName(self.site, 'portal_membership')
        mtool.setMembersFolderById(self.members_folder)


# Called according to import_steps.xml
def importVarious(context):
    importer = VariousImporter(context)
    importer.importVarious()


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
        avail_langs = site.getProperty('available_languages')
        translation_service = getToolByName(site, 'translation_service')
        for child in node.childNodes:
            if child.nodeName != 'root':
                continue

            id = str(child.getAttribute('name'))
            portal_type = str(child.getAttribute('portal_type'))

            # Create object
            if getattr(aq_base(site), id, None) is None:
                wftool = getToolByName(site, 'portal_workflow')
                wftool.invokeFactoryFor(site, portal_type, id)
            proxy = site._getOb(id)

            # Rolemap
            if child.hasAttribute('rolemap'):
                rolemap_name = str(child.getAttribute('rolemap'))
                rolemap_name += '.xml'
                importObjectRolemap(proxy, rolemap_name, self.environ)

            # I18n title
            if child.hasAttribute('title_msgid'):
                title_msgid = str(child.getAttribute('title_msgid'))
                existing_langs = proxy.getLanguageRevisions().keys()
                for lang in avail_langs:
                    if lang not in existing_langs:
                        proxy.addLanguageToProxy(lang)
                    title = translation_service(msgid=title_msgid,
                                                target_language=lang,
                                                default=title_msgid)
                    title = title.encode('iso-8859-15', 'ignore')
                    doc = proxy.getEditableContent(lang)
                    doc.edit(Title=title, proxy=proxy)

            # Workflow chains
            if child.hasAttribute('local_workflows'):
                localwf_name = str(child.getAttribute('local_workflows'))
                localwf_name += '.xml'
                importObjectLocalWorkflow(proxy, localwf_name, self.environ)


def importObjectLocalWorkflow(ob, filename, context):
    """Import local workflow chains from an XML file.
    """
    logger = context.getLogger('rolemap')
    path = '/'.join(ob.getPhysicalPath())

    body = context.readDataFile(filename)
    if body is None:
        logger.info("No local workflow map for %s" % path)
        return

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
    path = '/'.join(ob.getPhysicalPath())

    if context.shouldPurge():
        items = ob.__dict__.items()
        for k, v in items:
            if k == '__ac_roles__':
                delattr(ob, k)
            if k.startswith('_') and k.endswith('_Permission'):
                delattr(ob, k)

    body = context.readDataFile(filename)
    if body is None:
        logger.info("No role/permission map for %s" % path)
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

    logger.info("Role/permission map for %s imported." % path)


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
