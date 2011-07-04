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
from xml.dom.minidom import parseString
from zope.component import queryMultiAdapter
from Products.GenericSetup.interfaces import IBody

class StructureImporter(object):

    def __init__(self, context):
        self.context = context
        self.logger = self.context.getLogger('structure')
        self.count = 0 # number of imported objects


    def importFile(self, obj, path):
        """Import a single XML file for a given object."""

        if self.count and not self.count % 100:
            self.logger.info("Imported %d objects, committing", count)
            transaction.commit()

        context = self.context
        importer = queryMultiAdapter((obj, context), IBody)

        body = context.readDataFile(path)
        if body is not None:
            importer.filename = path # for error reporting
            importer.body = body
            self.count += 1

    def readObjectId(self, path):
        body = self.context.readDataFile(path)

        dom = parseString(body)
        root = dom.documentElement
        return root.getAttribute('name')

    def importDirectory(self, container, path):
        """Import recursively a directory in given container.

        We crawl XML files rather that the site. That can save hundred of
        thousands of object loads. The drawback is object id guessing from
        the XML file name."""

        context = self.context
        assert context.isDirectory(path)

        entries = context.listDirectory(path)
        if entries is None:
            return

        files = []
        dirs = []
        for e in entries:
            p = '%s/%s' % (path, e)
            if context.isDirectory(p):
                dirs.append(e)
            else:
                files.append(e)

        # recurse first on files in order to create the containers that
        # the directories represent.
        for f in files:
            oid = f.rsplit('.', 1)[0]
            sub_path = '%s/%s' % (path, f)
            if not container.hasObject(oid):
                oid = self.readObjectId(sub_path)
                if not container.hasObject(oid):
                    self.logger.warning(
                        'File %s corresponds directly to no Zope object, and '
                        'name attribute read as %r in it', sub_path, oid)
                    continue
            self.importFile(getattr(container, oid), sub_path)

        for d in dirs:
            oid = d
            sub_path = '%s/%s' % (path, d)
            if not container.hasObject(oid):
                oid = '.' + oid
                if not container.hasObject(oid):
                    self.logger.warn('File %s corresponds to no object',
                                     sub_path)
                    continue
            self.importDirectory(getattr(container, oid), sub_path)


