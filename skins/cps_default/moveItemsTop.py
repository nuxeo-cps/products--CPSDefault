## Script (Python) "moveItemsTop"
##parameters=ids=[]
# $Id$
""" Move the selected objects on the top within the directory """

def cmp_desc(x, y):
    return -cmp(x, y)

context_url = context.REQUEST.get("context_url", context.getContextUrl())

if not same_type(ids, []):
    ids = [ids]

# To respect the relative position of the choosen objects
ids.sort(cmp_desc)

for id in ids:
    context.move_object_to_top(id)

# Keeping the choosen ids while redisplaying the list
context.REQUEST.SESSION['choosen_ids'] = ids

redirection_url = context_url + "/folder_contents"
context.REQUEST.RESPONSE.redirect(redirection_url)
