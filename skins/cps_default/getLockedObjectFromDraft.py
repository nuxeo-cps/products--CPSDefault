##parameters=reverse=0
"""
Find the locked object for a draft.
If reverse==1, find the draft from the locked object.

Returns an object or None.
"""
# $Id$

wftool = context.portal_workflow
folder = context.aq_parent
docid = context.getDocid()
flr = context.getFromLanguageRevisions()
if not reverse:
    want_review_state = 'locked'
else:
    want_review_state = 'draft'
for ob in folder.objectValues():
    try:
        if ob.getDocid() != docid:
            continue
        if wftool.getInfoFor(ob, 'review_state', None) != want_review_state:
            continue
        if ob.getLanguageRevisions() != flr:
            continue
        return ob
    except:
        from zLOG import LOG
        LOG('getLockedObjectFromDraft', 200,
            'Exception in folder=%s' % folder)
        raise

return None
