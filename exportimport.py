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

from Products.CMFCore.utils import getToolByName


CATALOGS = [ # XXX hardcode for now
    # domain, localizer catalog
    ('cpsskins', 'cpsskins'),
    #('cpscollector', 'cpscollector'),
    #('RSSBox', 'cpsrss'),
    ]

TS_TOOL = 'translation_service'

def importVarious(context):
    """Import various non-exportable settings.

    Will go away when full handlers are coded for these.

    - create translation_service config
    """
    site = context.getSite()

    if getToolByName(site, TS_TOOL, None) is None:
        addprod = site.manage_addProduct['TranslationService']
        addprod.addPlacefulTranslationService(id=TS_TOOL)

        ts = getToolByName(site, TS_TOOL)
        ts.manage_setDomainInfo(path_0='Localizer/default')
        ts.manage_addDomainInfo('default', 'Localizer/default')
        for domain, catalog in CATALOGS:
            ts.manage_addDomainInfo(domain, 'Localizer/%s' % catalog)

    return "Various settings imported."



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
