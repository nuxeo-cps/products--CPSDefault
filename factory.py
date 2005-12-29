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

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry
from Products.GenericSetup.tool import SetupTool

from Portal import CMFSite

from Products.CPSDefault.interfaces import ICPSSite


_TOOL_ID = 'portal_setup'


def addConfiguredCPSSiteForm(dispatcher):
    """Form to add a CPS Site.

    Gets some info in context.
    """
    form = PageTemplateFile('zmi/siteAddForm', globals())
    form = form.__of__(dispatcher)

    # Collect CPS profiles
    base_profiles = []
    extension_profiles = []
    for info in profile_registry.listProfileInfo(for_=ICPSSite):
        if info.get('type') == EXTENSION:
            extension_profiles.append(info)
        else: # BASE
            base_profiles.append(info)

    return form(base_profiles=tuple(base_profiles),
                extension_profiles=tuple(extension_profiles))
