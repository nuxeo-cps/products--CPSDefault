##parameters=ids={}, REQUEST=None
# $Id$

ret_url = context.absolute_url() + '/folder_contents'

if ids:
    context.manage_delObjects(ids)
    message = 'portal_status_message=psm_item(s)_deleted'
else:
    message = 'portal_status_message=psm_select_at_least_one_document'  

if REQUEST is not None:
    return REQUEST.RESPONSE.redirect(ret_url + '?' + message)
