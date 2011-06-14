# (C) Copyright 2005-2007 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Florent Guillaume <fg@nuxeo.com>
# M.-A. Darche <madarche@nuxeo.com>
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

from zope.component import queryMultiAdapter
from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import importObjects

from Products.CPSWorkflow.workflowtool import LOCAL_WORKFLOW_CONFIG_ID
from Products.CPSWorkflow.configuration import (
    addConfiguration as addLocalWorkflowConfiguration)
from Products.CPSWorkflow.exportimport import (
    LocalWorkflowConfigurationXMLAdapter)

from Products.Localizer.exportimport import importLocalizer
from various import VariousImporter
from portlets import LocalPortletsExporter

from Products.GenericSetup.interfaces import IBody

# Called according to import_steps.xml
def importVarious(context):
    importer = VariousImporter(context)
    importer.importVarious()


# Called according to export_steps.xml
def exportLocalPortlets(context):
    exporter = LocalPortletsExporter(context)
    exporter.exportObjects()


def importLocalizerAndClearCaches(context):
    """Call the Localizer importer and then clear the portlets tool caches.

    That way all the portlets take advantage of the new translations.
    """
    site = context.getSite()
    importLocalizer(context)
    portlets_tool = getToolByName(site, 'portal_cpsportlets')
    portlets_tool.clearCache()


def importObjectLocalWorkflow(ob, filename, context):
    """Import local workflow chains from an XML file.
    """
    logger = context.getLogger('cpsworkflow')
    path = '/'.join(ob.getPhysicalPath())

    body = context.readDataFile(filename)
    if body is None:
        logger.info("No local workflow map for %s" % path)
        return

    if getattr(aq_base(ob), LOCAL_WORKFLOW_CONFIG_ID, None) is not None:
        confob = ob._getOb(LOCAL_WORKFLOW_CONFIG_ID)
    else:
        confob = addLocalWorkflowConfiguration(ob)
    importer = LocalWorkflowConfigurationXMLAdapter(confob, context)
    if importer is not None:
        importer.body = body

    logger.info("Local workflow map for %s imported." % path)


def importStructure(context, obj=None, path='structure', count=None):
    """Import a hierarchy of documents and folders starting from obj

    Similar logic as importObjects, except that we crawl the XML files rather
    than the site (crucial to apply to loaded sites)."""

    logger = context.getLogger('structure')
    # hack using a list as argument. XXX refactor with a class
    if count is None:
        count = 0
    else:
        count = count[0]

    if count and not count % 100:
        logger.info("Imported %d objects, committing", count)
        transaction.commit()

    if obj is None:
        obj = context.getSite()

    importer = queryMultiAdapter((obj, context), IBody)
    filename = path + importer.suffix
    body = context.readDataFile(filename)
    if body is not None:
        importer.filename = filename # for error reporting
        importer.body = body
        count += 1

    # now recurse
    # using / in there no more inconsistent than in GenericSetup.utils
    dirs = [f for f in context.listDirectory(path)
            if context.isDirectory('%s/%s' % (path, f))]

    for d in dirs:
        sub_path = '%s/%s' % (path, d)
        if not obj.hasObject(d):
            d = '.' + d
            if not obj.hasObject(d):
                logger.warn('Directory %s corresponds to no object', sub_path)
                continue
        sub_obj = getattr(obj, d)
        importStructure(context, obj=sub_obj, path=sub_path, count=[count])
