##parameters=ids=[]
# $Id$
"""
Move selected objects one step up in the folder
"""

context_url = context.REQUEST.get("context_url", context.getContextUrl())

if not same_type(ids, []):
    ids = [ids]

if ids:
    for id in ids:
        context.moveObjectsUp(id)
    message = 'psm_item(s)_moved_up'
else:
    message = 'psm_select_at_least_one_document'

# Keeping the choosen ids while redisplaying the list
context.REQUEST.SESSION['choosen_ids'] = ids

ret_url = context_url + "folder_contents"
context.REQUEST.RESPONSE.redirect(
    ret_url + '?portal_status_message=%s' % message)
