##parameters=reverse=0
# $Id$
"""
Find the locked object for a draft.
If reverse==1, find the draft from the locked object.

Returns an object or None.
"""

pxtool = context.portal_proxies
docid = context.getDocid()
flr = context.getFromLanguageRevisions()

candidates = pxtool.getProxyInfosFromDocid(docid, workflow_vars=['review_state'])

if not reverse:
    want_review_state = 'locked'
else:
    want_review_state = 'draft'

for info in candidates:
    if not info['visible']:
        continue
    if info['review_state'] != want_review_state:
        continue
    ob = info['object']
    if ob.getLanguageRevisions() != flr:
        continue
    return ob

return None
