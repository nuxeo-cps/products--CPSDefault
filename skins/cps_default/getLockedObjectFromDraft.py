##parameters=reverse=0
# $Id$
"""
Find the locked object for a draft.
If reverse==1, find the draft from the locked object.

Returns an object or None.
"""

utool = context.portal_url
folder = context.aq_inner.aq_parent
docid = context.getDocid()
flr = context.getFromLanguageRevisions()

if not reverse:
    want_review_state = 'locked'
else:
    want_review_state = 'draft'

# use a catalog query to avoid scanning the whole folder content
query = {
    'portal_type': context.portal_type,
    'review_state': want_review_state,
    'folder_prefix': utool.getRpath(folder),
}

for brain in context.search(query):
    ob = brain.getObject()
    if ob.getDocid() != docid:
        continue
    if ob.getLanguageRevisions() != flr:
        continue
    return ob

return None
