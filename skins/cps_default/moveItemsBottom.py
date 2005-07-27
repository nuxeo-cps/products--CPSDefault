##parameters=ids=[]
# $Id$
"""
Move the selected objects up within the directory

FIXME: docstring doesn't match method name.
"""

context_url = context.REQUEST.get("context_url", context.getContextUrl())

if not same_type(ids, []):
    ids = [ids]

for id in ids:
    context.moveObjectsToBottom(id)

# Keeping the choosen ids while redisplaying the list
context.REQUEST.SESSION['choosen_ids'] = ids

redirection_url = context_url + "/folder_contents"
context.REQUEST.RESPONSE.redirect(redirection_url)
