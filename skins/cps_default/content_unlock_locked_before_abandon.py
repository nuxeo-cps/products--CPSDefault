##parameters=state_change
"""
Unlock the locked object before a draft is abandonned.

Called during the abandon_draft transition by the workflow.
context is the object.
"""
# $Id$

wftool = context.portal_workflow

locked_ob = context.getLockedObjectFromDraft()

if locked_ob is not None:
    wftool.doActionFor(locked_ob, 'unlock')
