##parameters=type_name, REQUEST=None, **kw
# $Id$
"""
Create an object.
"""
from urllib import urlencode

if REQUEST:
    kw.update(REQUEST.form)

    # Use creation without empty object.
    # XXX should find better
    ti = getattr(context.portal_types, type_name)
    # For cpsdocument
    if ti.meta_type == 'CPS Flexible Type Information':
        args = {'type_name': type_name}
        # XXX pass prefilled title, a bit of a hack...
        args['widget__Title'] = kw.get('title', '')
        return REQUEST.RESPONSE.redirect('%s/cpsdocument_create_form?%s' %
                                (context.absolute_url(), urlencode(args)))

if REQUEST and not kw.get('title'):
    # Need a title before creating folders
    if type_name in ('Section', 'Workspace'):
        args = {'type_name': type_name}
        return REQUEST.RESPONSE.redirect('%s/folder_edit_form?%s' %
                                (context.absolute_url(), urlencode(args)))

id = kw.get('title', 'my_' + type_name)
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
