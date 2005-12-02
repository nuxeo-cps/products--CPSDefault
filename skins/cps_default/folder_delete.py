##parameters=ids=[], REQUEST=None
# $Id$
"""
FIXME: add docstring.
"""

ret_url = context.absolute_url() + '/folder_contents'

if ids:
    for id in ids:
        # XXX has to be called from here since the workflow doesn't handle the
        # deletion yet
        ob = getattr(context, id)
        from Products.CPSCore.EventServiceTool import getPublicEventService
        evtool = getPublicEventService(context)
        evtool.notifyEvent('workflow_delete', ob, {})
    context.manage_delObjects(ids)
    message = 'portal_status_message=psm_item(s)_deleted'
else:
    message = 'portal_status_message=psm_select_at_least_one_document'

if REQUEST is not None:
    return REQUEST.RESPONSE.redirect(ret_url + '?' + message)
