## Script (Python) "moveItemsDown"
##parameters=ids=[]
# $Id$
""" Move the selected objects down within the directory """

context_url = context.REQUEST.get("context_url", context.getContextUrl())

if not same_type(ids, []):
    ids = [ids]

for id in ids:
    context.move_object_down(id)

redirection_url = context_url + "/folder_contents"
context.REQUEST.RESPONSE.redirect(redirection_url)
