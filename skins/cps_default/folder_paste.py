##parameters=
#$Id$
"""
Cut an object. Used within the folder_contents template.
"""

REQUEST=context.REQUEST

if context.portal_type != 'Section':
    if context.cb_dataValid:
        context.manage_pasteObjects(REQUEST['__cp'])
        message = 'psm_item(s)_pasted'
    else:
        message = 'psm_copy_or_cut_at_least_one_document'
else:
    message = 'psm_operation_not_allowed'
return REQUEST.RESPONSE.redirect(context.absolute_url() + \
                                 '/folder_contents?portal_status_message=%s' \
                                 % (message, ))
