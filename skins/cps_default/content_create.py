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

type_name = kw['type_name']
id = kw.get('title')
if not id:
    id = 'my ' + type_name

id = context.computeId(compute_from=id)

context.invokeFactory(type_name, id)
ob = getattr(context, id)

try:
    doc = ob.getEditableContent()
except AttributeError:
    # not a proxy
    doc = ob
else:
    try:
        doc.edit(**kw)
    except:
        # CMF Compatibility.
        # type_name not necessarly and edit method
        # for CMF types is not aware about that.
        del kw['type_name']
        doc.edit(**kw)

context.portal_eventservice.notifyEvent('modify_object', context, {})
context.portal_eventservice.notifyEvent('modify_object', ob, {})


if REQUEST is not None:
    psm = 'psm_content_created'
    action_path = doc.getTypeInfo().immediate_view # getActionById('metadata')
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                              (ob.absolute_url(), action_path,
                               psm))

return id
