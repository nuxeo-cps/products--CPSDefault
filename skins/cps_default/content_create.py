## Script (Python) "content_create"
##title=Create a new Content
##parameters=REQUEST=None, **kw
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

doc = ob.getEditableContent()
doc.edit(**kw)
context.portal_eventservice.notifyEvent('modify_object', context, {})
context.portal_eventservice.notifyEvent('modify_object', ob, {})


if REQUEST is not None:
    psm = 'Content+create'
    REQUEST.RESPONSE.redirect('%s?portal_status_message=%s' % 
                              (ob.absolute_url(), psm))
return psm
