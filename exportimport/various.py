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

from Products.CMFCore.utils import getToolByName
from roots import RootsXMLAdapter

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
        self.setupProperties()
        self.setupTranslationService()
        self.setupRoots()
        self.setupDefaultRoles()
        return "Various settings imported."

    def setupProperties(self):
        # this cannot be changed easily and should not stay void
        self.site.default_charset = 'unicode'

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
