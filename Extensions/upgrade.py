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

TYPES = ('Workspace', 'Section')
CHECK_ROOTS = ('workspaces', 'sections')

def checkUpgradeWorkflows(context):
    """Check if workflows need to be upgraded."""
    upgrade = 0
    portal = getToolByName(context, 'portal_url').getPortalObject()
    for rpath in CHECK_ROOTS:
        ob = portal.restrictedTraverse(rpath)
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
