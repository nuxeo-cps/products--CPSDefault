# Copyright (c) 2009 Georges Racinet <http://www.racinet.fr>
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
"""Resync various persistent stuff: tree caches, catalog..."""

import logging
import sys
import re
from pprint import pformat

import transaction
from DateTime import DateTime
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError

from Products.ZCatalog.ProgressHandler import ZLogHandler
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import ManagePortal
from Products.GenericSetup.utils import _resolveDottedName
from Products.CPSCore.utils import KEYWORD_VIEW_LANGUAGE
from Products.CPSPortlets.PortletsCatalogTool import reindex_portlets_catalog

logger = logging.getLogger('CPSDefault.jobs.resync')
from Products.CPSUtil import cpsjob

LANG_PATH_REGEXP = re.compile(KEYWORD_VIEW_LANGUAGE + r'/\a+$')

def refreshCatalog(zcatalog, clear=0, pghandler=None):
    """re-index everything we can find.
    This part is borrowed from ZCatalog (ZPL licence)
    modified to avoid problems with language
    paths."""

    cat = zcatalog._catalog
    paths = cat.paths.values()
    if clear:
        paths = tuple(paths)
        cat.clear()

    num_objects = len(paths)
    if pghandler:
        pghandler.init('Refreshing catalog: %s' % zcatalog.absolute_url(1),
                       num_objects)

    for i in xrange(num_objects):
        if pghandler: pghandler.report(i)

        p = paths[i]
        if LANG_PATH_REGEXP.search(p) is not None:
            # language rev, will be indexed with the proxy itself anyway
            continue
        obj = zcatalog.resolve_path(p)
        if obj is None:
            continue
        if obj is not None:
            try:
                zcatalog.catalog_object(obj, p, pghandler=pghandler)
            except ConflictError:
                raise
            except:
                logger.error('Recataloging object at %s failed' % p,
                             exc_info=sys.exc_info())

    if pghandler: pghandler.finish()

def resync_catalog(portal):
    """Reindexes the catalog
    Four first args are general for optparse callbacks."""

    logger.info("Starting catalog reindex")
    cat = portal.portal_catalog
    pgthreshold = cat._getProgressThreshold()
    # TODO maybe hook to logging for better cpsjob integration
    handler = (pgthreshold > 0) and ZLogHandler(pgthreshold) or None

    refreshCatalog(cat, clear=1, pghandler=handler) # does some txn stuff

    transaction.commit()
    logger.info("Catalog reindex done")

def resync_trees(portal):
    """Rebuild all tree caches.
    Four first args are standard optparse stuff."""

    trees = portal.portal_trees.objectValues('CPS Tree Cache')
    for tree in trees:
        logger.info("Rebuilding %s", tree)
        tree.rebuild()
        transaction.commit()

def main():
    """CPS job bootstrap"""

    optparser = cpsjob.optparser
    optparser.add_option('-c', '--catalog', dest='catalog',
                         action='store_true',
                         help="Catalog full reindexation")
    optparser.add_option('-p', '--portlets-catalog', dest='ptl_catalog',
                         action='store_true',
                         help="Portlets Catalog reindexation")
    optparser.add_option('-t', '--trees', dest='trees', action='store_true',
                         help="Rebuild of tree caches")

    portal, options, args = cpsjob.bootstrap(app)

    if args:
        optparser.error("Args: %s; this job accepts options only."
                        "Try --help" % args)
    if options.catalog:
	resync_catalog(portal)
    if options.trees:
	resync_trees(portal)
    if options.ptl_catalog:
        logger.info("Starting portlets catalog reindex")
        reindex_portlets_catalog(portal)
        logger.info("Portlet catalog reindex done")


# invocation through zopectl run
if __name__ == '__main__':
    main()

