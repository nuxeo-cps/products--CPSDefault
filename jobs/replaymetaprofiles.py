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
"""Replay meta profiles"""

import logging
import sys
from pprint import pformat

import transaction
from DateTime import DateTime
from AccessControl import Unauthorized

from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import ManagePortal
from Products.GenericSetup.utils import _resolveDottedName

logger = logging.getLogger('CPSDefault.jobs.replaymetaprofiles')

def replay(portal, steps=()):
    if not _checkPermission(ManagePortal, portal):
        raise Unauthorized

    SiteConfigurator = _resolveDottedName(portal.configurator)
    conf = SiteConfigurator(site=portal)
    conf.replayMetaProfiles(steps=steps)

    # user feedback
    m_ids = portal.meta_profiles # always what has just been done
    log = ['Replayed meta profiles at %s ' % DateTime().ISO(), '']
    for m_id in m_ids:
        log.append(conf.meta_profiles[m_id].get('title', m_id))
    if steps:
        log.append('   run limited to these import steps: ' + ', '.join(steps))
    log.extend(['\n\n', 'User input parameters where kept as:', ''])
    params = conf.paramsSnapshot(m_ids)
    undisclosed = conf.getUndisclosedParams()
    for pid, pvalue in params.items():
        if pid in undisclosed:
            params[pid] = '**********'
    log.append(pformat(params))

    logger.info('\n'.join(log))
    return log

def run(portal, arguments, options):
    """CPS job bootstrap"""
    if arguments:
        raise ValueError("This CPS job accepts no arguments")
    steps = options.steps
    if steps:
        steps = tuple(x.strip() for x in steps.split(','))

    log = replay(portal, steps=steps)
    transaction.commit()
    sys.stderr.writelines(log)

# invocation through zopectl run
if __name__ == '__main__':
    from Products.CPSUtil.cpsjob import bootstrap
    from Products.CPSUtil.cpsjob import optparser
    optparser.add_option('-s', '--steps',
                         help="Comma-separated list of import steps to apply. "
                         "(default to all)")

    portal, options, arguments = bootstrap(app)
    run(portal, arguments, options)
