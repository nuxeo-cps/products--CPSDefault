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
import sys
import transaction
from Products.CMFCore.utils import getToolByName
from Products.CPSUtil import cpsjob
from Products.CPSDefault.jobs import resync
from Products.CPSCore.ProxyBase import walk_cps_folders
from Products.CPSCore.upgrade import listUpgradesByHandler

from Products.CPSDefault.upgrade import upgrade_unicode as upgrade_portal
from Products.CPSDefault.upgrade import upgrade_ascii_string_fields
from Products.CPSDefault.upgrade import upgrade_string_fields_validate_none
from Products.CPSSchemas.upgrade import upgrade_voctool_unicode \
     as upgrade_voctool
from Products.CPSPortlets.upgrade import upgrade_unicode as upgrade_portlets
from Products.CPSDocument.upgrade import upgrade_unicode as upgrade_documents
from Products.CPSWorkflow.upgrade import upgrade_unicode_in as \
    upgrade_workflows_in
from Products.CPSWorkflow.upgrade import upgrade_aggregated_histories
from Products.CPSDirectory.upgrade import upgrade_zodb_dirs_unicode \
    as upgrade_zodb_dirs

logger = logging.getLogger('CPSDefault.jobs.upgradeunicode')

# imports outside CPS-3-base
def have_product(name):
    return 'Products.' + name in sys.modules

if have_product('CPSSharedCalendar'):
    from Products.CPSSharedCalendar.upgrade import upgrade_unicode_in \
         as upgrade_calendars_in
if have_product('CPSWiki'):
    from Products.CPSWiki.upgrade import upgrade_unicode_in \
         as upgrade_wikis_in
if have_product('CPSBlog'):
    from Products.CPSBlog.upgrade import upgrade_unicode \
         as upgrade_blogs
if have_product('CPSSubscriptions'):
    from Products.CPSSubscriptions.upgrade import upgrade_msg_unicode \
         as upgrade_subscriptions
if have_product('CPSComment'):
    from Products.CPSComment.upgrade import upgrade_comments_unicode \
         as upgrade_comments
if have_product('CPSCollector'):
    from Products.CPSCollector.upgrade import upgrade_data_unicode \
         as upgrade_collector_data

def mark_handler_done(context, handler):
    """Mark all steps with that handler as done."""
    stool = getToolByName(context, 'portal_setup')
    for step in listUpgradesByHandler(handler):
        stool._markStepDone(step)
    transaction.commit()

def do_step(handler, portal, **kwargs):
    handler(portal, **kwargs)
    mark_handler_done(portal, handler)


def base_upgrade_glob(portal):
    """Play global upgrades for the CPS-base set of products."""

    # Applying upgrades in proper order is important
    for up in (upgrade_portal, upgrade_string_fields_validate_none,
               upgrade_ascii_string_fields, upgrade_voctool,
               upgrade_portlets,
               (upgrade_documents, dict(resync_trees=False)),
               upgrade_aggregated_histories, upgrade_zodb_dirs):
        if isinstance(up, tuple):
            do_step(up[0], portal, **up[1])
        else:
            do_step(up, portal)

def default_done():
    return dict(total=0, done=0)

def base_upgrade_in(folder, counters_mapping):
    """Upgrades related to CPS-base in given folder."""
    def get_counters(key):
        return counters_mapping.setdefault(key, default_done())

    upgrade_workflows_in(folder, counters=get_counters('workflows'))

def extensions_upgrade_glob(portal):
    """Play global upgrades of products that are in CPS-3-full \ CPS-3-base."""
    if have_product('CPSCollector'):
        upgrade_collector_data(portal)
        mark_handler_done(portal, upgrade_collector_data)
    if have_product('CPSSubscriptions'):
        upgrade_subscriptions(portal)
        mark_handler_done(portal, upgrade_subscriptions)
    if have_product('CPSComments'):
        upgrade_comments(portal)
        mark_handler_done(portal, upgrade_comments)
    if have_product('CPSBlog'):
        upgrade_blogs(portal)
        mark_handler_done(portal, upgrade_blogs)

def extensions_upgrade_in(folder, counters_mapping):
    """Same as extensions_upgrades but in a given folder."""

    def get_counters(key):
        return counters_mapping.setdefault(key, default_done())

    if have_product('CPSSharedCalendar'):
        upgrade_calendars_in(folder, counters=get_counters('calendars'))
    if have_product('CPSWiki'):
        upgrade_wikis_in(folder,
                         get_counters('wikis'), get_counters('wiki-pages'))

def run(portal, options):
    if options.all:
        options.glob = options.walk = options.resync = True

    if options.all_no_resync:
        options.glob = options.walk = True
        options.resync = False

    if options.glob:
        logger.info("Starting global upgrades")
        base_upgrade_glob(portal)
        extensions_upgrade_glob(portal)

    if options.walk:
        logger.info("Starting the big walk")
        counters_mapping = {}
        for folder in walk_cps_folders(portal):
            logger.info("Descending into %s", folder.absolute_url_path())

            base_upgrade_in(folder, counters_mapping)
            extensions_upgrade_in(folder, counters_mapping)
        logger.info("Big walk finished")

        for k, v in counters_mapping.items():
            logger.info("Upgraded %d/%d for %s", v['done'], v['total'], k)
        if have_product('CPSSharedCalendar'):
            mark_handler_done(portal,
                'Products.CPSSharedCalendar.upgrade.upgrade_cps_unicode')
        if have_product('CPSWiki'):
            mark_handler_done(portal,
                              'Products.CPSWiki.upgrade.upgrade_unicode')


    if options.walk and options.glob:
        mark_handler_done(portal,
                          'Products.CPSWorkflow.upgrade.upgrade_unicode')

    transaction.commit()

    if options.resync:
        logger.info("Starting to resync everything.")
        after_sync(portal)

def after_sync(portal):
    """Reindexations and the like after playing the steps."""

    logger.info("Starting catalog reindex")
    resync.resync_catalog(portal)
    logger.info("Catalog reindex done")

    logger.info("Starting rebuilding trees")
    resync.resync_trees(portal)
    logger.info("Starting rebuilding trees")

    logger.info("Starting portlets catalog reindex")
    resync.reindex_portlets_catalog(portal)
    logger.info("Portlet catalog reindex done")

    transaction.commit() # Ensuring the thing

def main():
    """cpsjob bootstrap."""
    optparser = cpsjob.optparser
    optparser.add_option('-g', '--global', dest='glob',
                         action='store_true',
                         help="Run global upgrades (those that need no walk)")
    optparser.add_option('-w', '--walk', dest='walk',
                         action='store_true',
                         help="Run upgrades that need to walk folders")
    optparser.add_option('-r', '--resync', dest='resync',
                         action='store_true',
                         help="Apply resynchronizations")
    optparser.add_option('-a', '--all', dest='all', action='store_true',
                         help="Run everything")
    optparser.add_option('--all-no-resync', dest='all_no_resync',
                         action='store_true',
                         help="Run everything but reindexings")
    portal, options, args = cpsjob.bootstrap(app)

    if args:
        optparser.error("Args: %s; this job accepts options only."
                        "Try --help" % args)

    run(portal, options)

# invocation through zopectl run
if __name__ == '__main__':
    main()

