##parameters=ids=[]
# $Id$
"""
Move selected objects at the bottom of the folder
"""

if same_type(ids, ''):
    ids = [ids]

if ids:
    context.moveObjectsToBottom(ids)
    message = 'psm_item(s)_moved_to_bottom'
else:
    message = 'psm_select_at_least_one_document'

# Keeping the choosen ids while redisplaying the list
context.REQUEST.SESSION['choosen_ids'] = ids

context_url = context.REQUEST.get("context_url", context.getContextUrl())
ret_url = context_url + "folder_contents"
context.REQUEST.RESPONSE.redirect(
    ret_url + '?portal_status_message=%s' % message)
