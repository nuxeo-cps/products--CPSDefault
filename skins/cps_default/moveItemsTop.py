##parameters=ids=[]
# $Id$
"""
Move the selected objects on the top within the directory
"""

def cmp_desc(x, y):
    return -cmp(x, y)

context_url = context.REQUEST.get("context_url", context.getContextUrl())

if not same_type(ids, []):
    ids = [ids]

# To respect the relative position of the choosen objects
ids.sort(cmp_desc)

if ids:
    for id in ids:
        context.moveObjectsToTop(id)
    message = 'psm_item(s)_moved_to_top'
else:
    message = 'psm_select_at_least_one_document'

# Keeping the choosen ids while redisplaying the list
context.REQUEST.SESSION['choosen_ids'] = ids

ret_url = context_url + "folder_contents"
context.REQUEST.RESPONSE.redirect(
    ret_url + '?portal_status_message=%s' % message)
