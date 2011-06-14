# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
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

import transaction
from zope.component import queryMultiAdapter
from Acquisition import aq_parent, aq_inner

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import exportObjects

from Products.GenericSetup.interfaces import IBody

class LocalPortletsExporter(object):

    name = 'local_portlets'

    def __init__(self, context):
        site = self.site = context.getSite()
        self.ptltool = getToolByName(site, 'portal_cpsportlets')
        self.ptlcat = getToolByName(site, 'portal_cpsportlets_catalog')
        self.utool = getToolByName(site, 'portal_url')
        self.context = context

    def exportPortletsIn(self, parent_path, folder):
        cont = self.ptltool.getPortletContainer(context=folder, local=True)
        if cont is None:
            return False
        exportObjects(cont, parent_path + '/', self.context)
        return True

    def foldersWithPortlets(self):
        """Return a set of rpaths of all folders having local portlets."""
        brains = self.ptlcat()
        site_path = self.site.getPhysicalPath()
        spl = len('/'.join(site_path)) + 1
        rpaths =  set( b.getPath().rsplit('/', 2)[0][spl:] for b in brains)
        rpaths.discard('') # we are about local portlets, not those at top
        return rpaths

    def exportObjects(self):
        """Inspired from recursion in GenericSetup.utils but uses cps walkers
        """

        context = self.context
        logger = context.getLogger(self.name)
        parents = [self.name]
        portal_depth = len(self.site.getPhysicalPath())

        # We loop on detected folders and climb up the hierarchy from
        # each of them. Algorithmically, this is not so bad, and we keep
        # traversals and ZODB fetchs to something reasonible.
        folder_rpaths = self.foldersWithPortlets()
        done_folders = set()
        zodb_count = 0
        for folder_rpath in folder_rpaths:
            folder = ancestor = self.site.unrestrictedTraverse(folder_rpath)
            ancestor_rpath = folder_rpath
            zodb_count += 5 # rough estimate for portlets
            if zodb_count % 100 == 0:
                transaction.savepoint() # free some RAM

            while ancestor_rpath not in done_folders:
                exporter = queryMultiAdapter((ancestor, context), IBody)
                fpath = ancestor_rpath.replace(' ', '_')
                if exporter:
                    filename = '%s%s' % (fpath, exporter.suffix)
                    body = exporter.body
                    if body is not None:
                        context.writeDataFile(filename, body,
                                              exporter.mime_type)

                done_folders.add(ancestor_rpath)
                ancestor = aq_parent(aq_inner(folder))
                ancestor_rpath = ancestor_rpath.rsplit('/', 1)[0]
                zodb_count += 1

            self.exportPortletsIn(folder_rpath, folder)
