##parameters=ids=[]
# $Id$
"""
Move the selected objects up within the folder
"""

context_url = context.REQUEST.get("context_url", context.getContextUrl())

if not same_type(ids, []):
    ids = [ids]

for id in ids:
    context.moveObjectsUp(id)

# Keeping the choosen ids while redisplaying the list
context.REQUEST.SESSION['choosen_ids'] = ids

redirection_url = context_url + "/folder_contents"
context.REQUEST.RESPONSE.redirect(redirection_url)
