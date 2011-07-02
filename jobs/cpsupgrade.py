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
"""Apply all upgrade steps."""

import logging
import sys

import transaction

from Products.CMFCore.utils import getToolByName

from Products.CPSDefault.jobs.replaymetaprofiles import replay as play_profiles

logger = logging.getLogger('CPSDefault.jobs.upgrades')

class Upgrader(object):

    def __init__(self, portal, categories=None):
        self.portal = portal
        self.stool = getToolByName(portal, 'portal_setup')
        if categories:
            self.cats = [c.strip() for c in categories]
        else:
            self.cats = [c['id'] for c in self.stool.listUpgradeCategories()]

    def apply_all_steps(self):
        """Applies all steps of all categories.

        Does it several times because reaching a certain version for some
        categories may unlock some steps in other categories."""

        stool = self.stool
        previous_steps = dict( (c, ()) for c in self.cats)
        cats = set(self.cats)
        while cats:
            for cat in cats:
                previous = previous_steps[cat]
                ups = stool.listUpgrades(category=cat)
                if not ups or ups == previous:
                    cats.discard(cat)
                    break
                logger.info("Applying all upgrades in category %s", cat)
                stool.doUpgrades([u['id'] for u in ups if u['proposed']], cat)
                previous_steps[cat] = ups
                transaction.commit()

    def replay_profiles(self):
        play_profiles(self.portal)

def job(portal, arguments, options):
    if options.categories:
        categories = options.categories.split(',')
    else:
        categories = None

    upgrader = Upgrader(portal, categories)
    upgrader.apply_all_steps()
    if options.meta_profiles:
        upgrader.replay_profiles()

if __name__ == '__main__':
    from Products.CPSUtil import cpsjob
    optparser = cpsjob.optparser
    optparser.add_option('-c', '--categories',
                         help="Restrict to given (comma-separated) list "
                         "of categories")
    optparser.add_option('-m', '--meta-profiles', action='store_true')

    cpsjob.run(app, job)
