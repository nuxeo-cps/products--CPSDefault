# (C) Copyright 2005-2006 Nuxeo SAS <http://nuxeo.com>
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
"""CPS Default Site Factory.
"""

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry
from Products.CMFCore.utils import getToolByName

from Products.CPSCore.setuptool import CPSSetupTool
from Products.CPSDefault.Portal import CPSDefaultSite

from Products.CPSCore.interfaces import ICPSSite


class CPSSiteConfigurator(object):
    """Configurator for a CPS Site.
    """

    prechecked_extensions = ()
    mandatory_extensions = ()

    available_languages = (
        {'id': 'ca', 'title': 'Catalan'},
        {'id': 'nl', 'title': 'Dutch'},
        {'id': 'en', 'title': 'English', 'checked': True},
        {'id': 'eu', 'title': 'Euskara'},
        {'id': 'fr', 'title': 'French', 'checked': True},
        {'id': 'de', 'title': 'German'},
        {'id': 'it', 'title': 'Italian'},
        {'id': 'mg', 'title': 'Malagasy'},
        {'id': 'pt_BR', 'title': 'Portugese (Brazilian)'},
        {'id': 'ro', 'title': 'Romanian'},
        {'id': 'es', 'title': 'Spanish', 'checked': True},
        )

    addForm = PageTemplateFile('zmi/siteAddForm', globals())

    def addConfiguredSiteForm(self, dispatcher):
        """Form to add a CPS Site.

        Gets some info in context.
        """
        # Collect CPS profiles
        base_profiles = []
        extension_profiles = []
        for info in profile_registry.listProfileInfo(for_=ICPSSite):
            if info['for'] == None:
                # Only keep CPS-specific extensions
                continue
            if info['type'] == EXTENSION:
                id = info['id']
                info['disabled'] = id in self.mandatory_extensions
                info['checked'] = (id in self.prechecked_extensions
                                   or info['disabled'])
                extension_profiles.append(info)
            else: # BASE
                base_profiles.append(info)
        extension_profiles.sort(key=lambda info: info['title'])

        form = self.addForm.__of__(dispatcher)
        options = {
            'base_profiles': tuple(base_profiles),
            'extension_profiles': tuple(extension_profiles),
            }
        self.prepareOptions(options)
        return form(**options)

    def prepareOptions(self, options):
        options['languages'] = self.available_languages

    def addConfiguredSite(self, dispatcher, site_id, profile_id,
                          extension_ids=(), snapshot=True,
                          REQUEST=None, **kw):
        """Add a CPSSite according to profile and extensions.
        """
        self.dispatcher = dispatcher

        self.checkForm(site_id, **kw)
        self.addSite(site_id)
        self.addSetupTool()
        self.beforeImport(**kw)
        self.importProfiles(profile_id, extension_ids)
        self.afterImport(**kw)

        if snapshot is True:
            self.setup_tool.createSnapshot('initial_configuration')

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/manage_main?update_menu=1'
                                      % dispatcher.absolute_url())
        else:
            return self.site

    def addSite(self, site_id):
        site_id = site_id.strip()
        site = CPSDefaultSite(site_id)
        self.dispatcher._setObject(site_id, site)
        self.site = self.dispatcher._getOb(site_id)

    def addSetupTool(self):
        setup_tool = CPSSetupTool()
        id = setup_tool.getId()
        self.site._setObject(id, setup_tool)
        self.setup_tool = getToolByName(self.site, id)

    def beforeImport(self, **kw):
        self.addLanguages(**kw)

    def addLanguages(self, languages=(), **kw):
        """Add to the portal the languages selected in the install form.

        This is done before the actual profile import. The Localizer importer
        uses the portal's available_languages.
        """
        if not languages:
            languages = ('en',)
        self.site.available_languages = tuple(languages)

    def importProfiles(self, profile_id, extension_ids=()):
        setup_tool = self.setup_tool
        setup_tool.setImportContext('profile-%s' % profile_id)
        setup_tool.runAllImportSteps()
        # Import mandatory extensions first
        extension_ids = tuple([id for id in extension_ids
                               if id not in self.mandatory_extensions])
        for extension_id in self.mandatory_extensions + extension_ids:
            setup_tool.setImportContext('profile-%s' % extension_id)
            setup_tool.runAllImportSteps()
        setup_tool.setImportContext('profile-%s' % profile_id)

    def afterImport(self, **kw):
        self.setDefaultUpgradedVersion()
        self.parseForm(**kw)

    def setDefaultUpgradedVersion(self):
        self.site._setDefaultUpgradedVersion()

    def checkForm(self, site_id, **kw):
        site_id = site_id.strip()
        if not site_id:
            raise ValueError("You have to provide an ID for the site!")
        self.parseForm(just_check=True, **kw)

    def parseForm(self, manager_id='', manager_email='',
                  manager_firstname='', manager_lastname='', password='',
                  password_confirm='', title='', description='',
                  just_check=False, **kw):
        title = title.strip()
        description = description.strip()
        manager_id = manager_id.strip()
        manager_email = manager_email.strip()
        manager_firstname = manager_firstname.strip()
        manager_lastname = manager_lastname.strip()
        manager_fullname = (manager_firstname+' '+manager_lastname).strip()

        if not manager_id:
            raise ValueError("You have to provide a Login "
                             "for the Administrator!")
        if not password:
            raise ValueError("You have to provide a password "
                             "for the Administrator!")
        if password != password_confirm:
            raise ValueError("Password confirmation does not match password!")
        if not manager_email:
            raise ValueError("You have to provide an Email address "
                             "for the Administrator!")

        if just_check:
            return

        self.site.title = title
        self.site.description = description
        self.site.email_from_address = manager_email
        self.site.email_from_name = manager_fullname
        self.createAdministrator(manager_id, password, manager_email,
                                 manager_firstname, manager_lastname)

    def createAdministrator(self, manager_id, password, manager_email,
                            manager_firstname, manager_lastname):
        mdir = getToolByName(self.site, 'portal_directories').members
        entry = {
            'id': manager_id,
            'password': password,
            'roles': ('Manager', 'Member'),
            'email': manager_email,
            'givenName': manager_firstname,
            'sn': manager_lastname,
        }
        mdir.createEntry(entry)



_cpsconfigurator = CPSSiteConfigurator()


# Do the following dance because bound methods don't play well with
# constructors registered for products.

def addConfiguredCPSSiteForm(dispatcher):
    """Form to add a CPS Site from ZMI.
    """
    return _cpsconfigurator.addConfiguredSiteForm(dispatcher)

def addConfiguredCPSSite(dispatcher, REQUEST=None, **kw):
    """Add a CPSSite according to profile and extensions.
    """
    if REQUEST is not None:
        kw.update(REQUEST.form)
    return _cpsconfigurator.addConfiguredSite(dispatcher,
                                              REQUEST=REQUEST, **kw)
