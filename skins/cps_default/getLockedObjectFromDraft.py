##parameters=
"""
Find the locked object for a draft.

Returns the locked object or None.
"""
# $Id$

wftool = context.portal_workflow
folder = context.aq_parent
docid = context.getDocid()
flr = context.getFromLanguageRevisions()
for ob in folder.objectValues():
    try:
        rs = wftool.getInfoFor(ob, 'review_state', None)
        if (rs == 'locked' and
            ob.getDocid() == docid and
            ob.getLanguageRevisions() == flr):
            return ob
    except:
        from zLOG import LOG
        LOG('getLockedObjectFromDraft', 200,
            'Exception in folder=%s' % folder)
        raise

return None
