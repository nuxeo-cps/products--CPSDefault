## Script (Python) "folder_delete"
##title=Delete objects from a folder
##parameters=

REQUEST = context.REQUEST
ret_url = context.absolute_url() + '/folder_contents'

if REQUEST.has_key('ids'):
    context.manage_delObjects(REQUEST['ids'])
    qs = '?portal_status_message=psm_item(s)_deleted'
else:
    qs = '?portal_status_message=psm_select_at_least_one_document'

return REQUEST.RESPONSE.redirect(ret_url + qs)
