## Script (Python) "moveItemsUp"
##parameters=ids=[]
# $Id$
""" Move the selected objects up within the directory """

context_url = context.REQUEST.get("context_url", context.getContextUrl())

if not same_type(ids, []):
    ids = [ids]

for id in ids:
    context.move_object_up(id)

redirection_url = context_url + "/folder_contents"
context.REQUEST.RESPONSE.redirect(redirection_url)
