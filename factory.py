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
"""CPS Default Site Factory.
"""

import os
from Globals import package_home
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry
from Products.CMFCore.utils import getToolByName

from Products.CPSCore.setuptool import CPSSetupTool
from Products.CPSDefault.Portal import CPSDefaultSite
from Products.CPSDefault.interfaces import ICPSSite


class CPSSiteConfigurator(object):
    """Configurator for a CPS Site.
    """

    default_extensions = (
        'CPSSkins:cps3',
        'CPSPortlets:default',
        )

    def addConfiguredCPSSiteForm(self, dispatcher):
        """Form to add a CPS Site.

        Gets some info in context.
        """
        form = PageTemplateFile('zmi/siteAddForm', globals())
        form = form.__of__(dispatcher)

        # Collect CPS profiles
        base_profiles = []
        extension_profiles = []
        for info in profile_registry.listProfileInfo(for_=ICPSSite):
            if info['for'] == None:
                continue
            if info['type'] == EXTENSION:
                info['checked'] = info['id'] in self.default_extensions
                extension_profiles.append(info)
            else: # BASE
                base_profiles.append(info)

        return form(base_profiles=tuple(base_profiles),
                    extension_profiles=tuple(extension_profiles))

    def addConfiguredCPSSite(self, dispatcher, site_id, profile_id,
                             snapshot=True, extension_ids=(),
                             REQUEST=None, **kw):
        """Add a CPSSite according to profile and extensions.
        """
        self.dispatcher = dispatcher
        self.addSite(site_id)
        self.addSetupTool()

        setup_tool = self.setup_tool
        setup_tool.setImportContext('profile-%s' % profile_id)
        setup_tool.runAllImportSteps()
        for extension_id in extension_ids:
            setup_tool.setImportContext('profile-%s' % extension_id)
            setup_tool.runAllImportSteps()
        setup_tool.setImportContext('profile-%s' % profile_id)

        # XXX more config here

        if snapshot is True:
            setup_tool.createSnapshot('initial_configuration')

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/manage_main?update_menu=1'
                                      % dispatcher.absolute_url())
        else:
            return self.site

    def addSite(self, site_id):
        site = CPSDefaultSite(site_id)
        self.dispatcher._setObject(site_id, site)
        self.site = self.dispatcher._getOb(site_id)

    def addSetupTool(self):
        setup_tool = CPSSetupTool()
        id = setup_tool.getId()
        self.site._setObject(id, setup_tool)
        self.setup_tool = getToolByName(self.site, id)


_configurator = CPSSiteConfigurator()


# Do the following dance because bound methods don't play well with
# constructors registered for products.

def addConfiguredCPSSiteForm(dispatcher):
    """Form to add a CPS Site from ZMI.
    """
    return _configurator.addConfiguredCPSSiteForm(dispatcher)

def addConfiguredCPSSite(dispatcher, site_id, profile_id, REQUEST=None, **kw):
    """Add a CPSSite according to profile and extensions.
    """
    if REQUEST is not None:
        kw.update(REQUEST.form)
        for name in ('dispatcher', 'site_id', 'profile_id'):
            if name in kw:
                del kw[name]
    return _configurator.addConfiguredCPSSite(dispatcher, site_id, profile_id,
                                              REQUEST=REQUEST, **kw)
