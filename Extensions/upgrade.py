# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
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

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized
from zLOG import LOG, DEBUG, INFO

TYPES = ('Workspace', 'Section', 'CPSForum')
CHECK_ROOTS = ('workspaces', 'sections')

def checkUpgradeWorkflows(context):
    """Check if workflows need to be upgraded."""
    upgrade = 0
    portal = getToolByName(context, 'portal_url').getPortalObject()
    for rpath in CHECK_ROOTS:
        ob = portal.restrictedTraverse(rpath, default=None)
        if ob is None:
            continue
        workflow_history = getattr(aq_base(ob), 'workflow_history', None)
        if workflow_history is None:
            continue
        for wf_id, wfh in workflow_history.items():
            if not wfh:
                continue
            status = wfh[-1]
            if status.has_key('review_state'):
                continue
            LOG('checkUpgradeWorkflows', INFO,
                "Workflow status for '%s' needs to be upgraded." % rpath)
            upgrade = 1
            break
    return upgrade

def upgradeWorkflows(self):
    """Upgrade the folders after workflow change.

    This script is to be launched as an ExternalMethod, it will search
    for all folder documents present in the portal and fix their
    workflow state.

    How to use the upgradeWorkflowss ExternalMethod:
    - Log into the ZMI as manager
    - Go to your CPS root directory
    - Create an External Method with the following parameters:

    id            : upgradeWorkflows
    title         : Use this method if you upgrade an instance older
                    than CPS 3.2.1
    Module Name   : CPSDefault.upgrade
    Function Name : upgradeWorkflows

    - save it
    - then click on the test tab of this external method
    """

    log_key = 'upgradeWorkflows'
    LOG(log_key, DEBUG, "")

    nchanged = 0
    brains = self.portal_catalog.searchResults(portal_type=TYPES)
    for brain in brains:
        ob = brain.getObject()
        if ob is None:
            continue
        workflow_history = getattr(aq_base(ob), 'workflow_history', None)
        if workflow_history is None:
            continue
        changed = 0
        for wf_id, wfh in workflow_history.items():
            if not wfh:
                continue
            status = wfh[-1]
            if status.has_key('review_state') or not status.has_key('state'):
                continue
            status['review_state'] = status['state']
            del status['state']
            workflow_history._p_changed = 1 # trigger persistence
            changed = 1
        if changed:
            path = '/'.join(ob.getPhysicalPath())
            LOG(log_key, DEBUG, "upgrading %s" % path)
            ob.reindexObject(idxs=['review_state'])
            nchanged += 1
    LOG(log_key, DEBUG, "%s objects upgraded" % nchanged)
    return '%s objects upgraded' % nchanged

def upgradeURLTool(self):
    """Upgrade portal_url

    The CMF URLTool is replaced by the CPS URLTool thta extends it by adding
    methods to deal with virtual hosting
    """
    from Products.CPSCore.URLTool import URLTool
    utool_id = URLTool.id
    portal = self.portal_url.getPortalObject()
    utool = getToolByName(portal, utool_id, None)
    add_it = 0
    if utool is None:
        add_it = 1
    else:
        if utool.meta_type != URLTool.meta_type:
            add_it = 1
            portal.manage_delObjects([utool_id])
    if add_it:
        portal.manage_addProduct['CPSCore'].manage_addTool(URLTool.meta_type)
        log = "portal_url upgraded"
    else:
        log = "portal_url did not need to be upgraded"
    return log


def upgrade_334_335_cache_parameters(context):
    """Upgrades cache parameters.

    - 'no-cache:(contextual)' is added to the Content Portlet
       cache parameters.
    """
    PORTLET_ID = 'Content Portlet'
    NEW_PARAMETER = 'no-cache:(contextual)'

    logger = []
    log = logger.append

    log("Updating portlet cache parameters...")
    # get the current parameters
    ptltool = getToolByName(context, 'portal_cpsportlets')
    params = ptltool.getCacheParametersFor(PORTLET_ID)

    # update the parameters
    if NEW_PARAMETER in params:
        log("  '%s' already set for '%s'." % (NEW_PARAMETER, PORTLET_ID))
    else:
        params.insert(0, NEW_PARAMETER)
        ptltool.updateCacheParameters({PORTLET_ID:params})
        log("  '%s' added to '%s'." % (NEW_PARAMETER, PORTLET_ID))
    return "\n".join(logger)

################################################## 3.3.5

def upgrade_334_335(self):
    """Upgrades for CPS 3.3.5"""

    # upgrade repository
    from Products.CPSCore.upgrade import upgrade_334_335_repository
    log = upgrade_334_335_repository(self)

    # upgrade portal_url
    log += "\n\n" + upgradeURLTool(self)

    # upgrade portlet cache parameters
    log += "\n\n" + upgrade_334_335_cache_parameters(self)

    # Upgrade CPSDocument
    from Products.CPSDocument.upgrade import upgrade_334_335_allowct_sections
    log += "\n\n" + upgrade_334_335_allowct_sections(self)

    # Upgrade CPSNewsLetters
    try:
        from Products.CPSNewsLetters.upgrade import \
             upgrade_334_335_allowct_sections
    except ImportError, e:
        if str(e) != 'No module named CPSNewsLetters.upgrade':
            raise
    else:
        log += "\n\n" + upgrade_334_335_allowct_sections(self)

    return log
