# Copyright (c) 2003 Nuxeo SARL <http://nuxeo.com>
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
""" CPS Default Init
"""

from Products.CMFCore.utils import ContentInit, ToolInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.permissions import AddPortalContent
from Products.GenericSetup import BASE
from Products.GenericSetup import profile_registry

from Products.CPSDefault.interface import ICPSSite


import MembershipTool
import CMFCalendarToolPatch

# Making sure that the ModuleSecurityInfo info statements of the utils
# module is taken into account.
import utils
import Portal
import Folder
import Dummy

contentClasses = (
    Folder.Folder,
    Dummy.Dummy,
    )

contentConstructors = (
    MembershipTool.addMembershipTool,
    Folder.addFolder,
    Dummy.addDummy,
    )

fti = (Folder.factory_type_information +
       Dummy.factory_type_information +
       ()
       )

registerDirectory('skins', globals())

tools = (
    MembershipTool.MembershipTool,
    )

def initialize(context):
    from Products.CPSDefault import factory

    # XXX Compatibility alias (c.f : CPSBoxes)
    ToolInit(
        'CPS Default Tool',
        tools=tools,
        icon='tool.png',
        ).initialize(context)

    ContentInit('CPSDefault Documents',
                content_types=contentClasses,
                permission=AddPortalContent,
                extra_constructors=contentConstructors,
                fti=fti,
                ).initialize(context)

    context.registerClass(Portal.CPSDefaultSite,
                          constructors=(factory.addConfiguredCPSSiteForm,
                                        factory.addConfiguredCPSSite),
                          icon='portal.png')

    # old registration
    context.registerClass(Portal.CPSDefaultSite,
                          constructors=(Portal.manage_addCPSDefaultSiteForm,
                                        Portal.manage_addCPSDefaultSite,))

    profile_registry.registerProfile('default',
                                     'CPS Default Site',
                                     "Profile for a default CPS site.",
                                     'profiles/default',
                                     'CPSDefault',
                                     BASE,
                                     for_=ICPSSite)
