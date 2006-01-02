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


class VariousImporter(object):

    catalogs = (
        # domain, localizer catalog
        ('default', 'default'),
        ('cpsskins', 'cpsskins'),
        #('cpscollector', 'cpscollector'),
        #('RSSBox', 'cpsrss'),
        )

    def importVarious(self, context):
        """Import various non-exportable settings.

        Will go away when specific handlers are coded for these.
        """
        self.site = context.getSite()
        self.configureTranslationService()
        return "Various settings imported."

    def configureTranslationService(self):
        ts = getToolByName(self.site, 'translation_service')
        ts.manage_setDomainInfo(path_0='Localizer/default')
        present = [i[0] for i in ts.getDomainInfo()]
        for domain, catalog in self.catalogs:
            if domain in present:
                continue
            ts.manage_addDomainInfo(domain, 'Localizer/%s' % catalog)


_variousImporter = VariousImporter()
importVarious = _variousImporter.importVarious


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
