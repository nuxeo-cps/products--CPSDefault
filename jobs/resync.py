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
import optparse

import transaction
from DateTime import DateTime
from AccessControl import Unauthorized

from Products.ZCatalog.ProgressHandler import ZLogHandler
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import ManagePortal
from Products.GenericSetup.utils import _resolveDottedName
from Products.CPSCore.utils import KEYWORD_VIEW_LANGUAGE

logger = logging.getLogger('CPSDefault.jobs.resync')
optparser = optparse.OptionParser(
    usage="usage: Products.CPSDefault.jobs.resync [options]")


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
        pghandler.init('Refreshing catalog: %s' % self.absolute_url(1), num_objects)

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

def resync_catalog(option, opt, value, parser, portal):
    """Reindexes the catalog
    Four first args are general for optparse callbacks."""

    logger.info("Starting catalog reindex")
    cat = portal.portal_catalog
    pgthreshold = cat._getProgressThreshold()
    # TODO maybe hook to logging for better cpsjob integration
    handler = (pgthreshold > 0) and ZLogHandler(pgthreshold) or None

    refreshCatalog(cat, clear=1, pghandler=handler) # does some txn stuff

    transaction.commit()

def resync_trees(option, opt, value, parser, portal):
    """Rebuild all tree caches.
    Four first args are standard optparse stuff."""

    trees = portal.portal_trees.objectValues('CPS Tree Cache')
    for tree in trees:
        logger.info("Rebuilding %s", tree)
        tree.rebuild()
        transaction.commit()

def run(portal, arguments):
    """CPS job bootstrap"""

    optparser.add_option('-c', '--catalog', action='callback',
                         help="Catalog full reindexation",
                         callback=resync_catalog, callback_args=(portal,))
    optparser.add_option('-t', '--trees', action='callback',
                         help="Rebuild of tree caches",
                         callback=resync_trees, callback_args=(portal,))

    options, args = optparser.parse_args(arguments)
    if args:
        optparser.error("Args: %s; this job accepts options only."
                        "Try --help" % args)

# invocation through zopectl run
if __name__ == '__main__':
    from Products.CPSUtil.cpsjob import bootstrap
    portal, options, arguments = bootstrap(app)
    run(portal, arguments)
