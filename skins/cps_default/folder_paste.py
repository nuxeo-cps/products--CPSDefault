##parameters=
#$Id$
"""
Paste objects from the clipboard. Used within the folder_contents template.
"""

REQUEST=context.REQUEST

#
# Security to let the CPS up in error situation.
# XXX : to remove if we you are sure.
# Didn't see any case since now.
#
try:
    if context.cb_dataValid():
        result = context.manage_CPSpasteObjects(REQUEST['__cp'])
        for id in [ob['new_id'] for ob in result]:
            ob = getattr(context, id)
            from Products.CPSCore.EventServiceTool import getPublicEventService
            evtool = getPublicEventService(context)
            evtool.notifyEvent('workflow_cut_copy_paste', ob, {})
        message = 'psm_item(s)_pasted'
    else:
        message = 'psm_copy_or_cut_at_least_one_document'
except:
    message = 'psm_operation_not_allowed'
return REQUEST.RESPONSE.redirect(context.absolute_url() + \
                                 '/folder_contents?portal_status_message=%s' \
                                 % (message, ))
