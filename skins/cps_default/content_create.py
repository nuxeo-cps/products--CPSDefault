## Script (Python) "content_create"
##title=Create a new Content
##parameters=REQUEST=None, **kw
# $Id$
"""
Create an object
"""
from urllib import urlencode

if REQUEST is not None:
    kw.update(REQUEST.form)

id = kw['id']
type_name = kw['type_name']
context.invokeFactory(type_name, id)
ob = getattr(context, id)

try:
    doc = ob.getEditableContent()
    doc.edit(**kw)
except AttributeError:
    # not a proxy
    doc = ob
context.portal_eventservice.notifyEvent('modify_object', context, {})
context.portal_eventservice.notifyEvent('modify_object', ob, {})


if REQUEST is not None:
    psm = 'Content+created.'
    action_path = doc.getTypeInfo().immediate_view # getActionById('metadata')
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' % 
                              (ob.absolute_url(), action_path,
                               psm))
return psm
