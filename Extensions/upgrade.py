# $Id$

from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized
from zLOG import LOG, DEBUG

def upgradeWorkflows(self):
    """Upgrade the News documents.

    This script is to be launched as an ExternalMethod, it will search for all
    News documents present in the portal and copy the old-existing newsdate
    attribute to the now-to-be-used EffectiveDate.

    Howto use the upgradeWorkflowss ExternalMethod:
    - Log into the ZMI as manager
    - Go to your CPS root directory
    - Create an External Method with the following parameters:
    
    id            : upgradeWorkflows
    title         : Use this method if you upgrade an instance older than CPS 3.2.1
    Module Name   : CPSDefault.upgrade
    Function Name : upgradeWorkflows
    
    - save it
    - then click on the test tab of this external method
    """

    log_key = 'upgradeWorkflows'
    LOG(log_key, DEBUG, "")

    brains = self.search(query={'portal_type': ('Workspace', 'Section')})
    for brain in brains:
        proxy = brain.getObject()
        LOG(log_key, DEBUG, "checking %s..." % proxy.title_or_id)
        workflow_history = getattr(proxy, 'workflow_history', None)
        if workflow_history is not None:
            LOG(log_key, DEBUG, "upgrading -> %s <-" % proxy.title_or_id)
            for (key, value) in workflow_history.items():
                if value[0].has_key('state'):
                    del value[0]['state']
                    value[0]['review_state'] = 'work'
