# Copyright (c) 2010 Georges Racinet <http://www.racinet.fr>
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
import transaction
from Products.CPSUtil import cpsjob
from Products.CPSDefault.jobs import resync

from Products.CPSDefault.upgrade import upgrade_unicode as upgrade_portal
from Products.CPSSchemas.upgrade import upgrade_voctool_unicode \
     as upgrade_voctool
from Products.CPSPortlets.upgrade import upgrade_unicode as upgrade_portlets
from Products.CPSDocument.upgrade import upgrade_unicode as upgrade_documents

logger = logging.getLogger('CPSDefault.jobs.upgradeunicode')


def base_upgrade(portal):
    """Upgrade the CPS-base set of products."""

    # The order can matter
    upgrade_portal(portal)
    upgrade_voctool(portal)
    upgrade_portlets(portal)
    upgrade_documents(portal)

def extensions_upgrade(portal):
    """Upgrade the products that are in CPS-3-full \ CPS-3-base."""
    # TODOs
    # CPSCollector
    # CPSSubscriptions
    # CPSSharedCalendar
    # CPSWiki
    # CPSComment

def main():
    """CPS job bootstrap"""

    portal, options, args = cpsjob.bootstrap(app)

    if args:
        optparser.error("Args: %s; this job accepts options only."
                        "Try --help" % args)
    base_upgrade(portal)
    after_sync(portal)

def after_sync(portal):
    """Reindexations and the like after playing the steps."""

    logger.info("Starting catalog reindex")
    resync.resync_catalog(portal)
    logger.info("Catalog reindex done")

    # not resyncing trees, because that's done by documents upgrade

    logger.info("Starting portlets catalog reindex")
    resync.reindex_portlets_catalog(portal)
    logger.info("Portlet catalog reindex done")

    transaction.commit() # Ensuring the thing

# invocation through zopectl run
if __name__ == '__main__':
    main()

