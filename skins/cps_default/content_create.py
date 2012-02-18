##parameters=type_name, REQUEST=None, **kw
# $Id$
"""
Create an object with the given parameters.

Parameters:
type_name: the name of the portal_type of the content to create
title: the title of the content to create

It is possible to pass other parameters than the specific one listed above.

All the parameters will be passed to modify the document once it is created.
"""

from urllib import urlencode

if REQUEST is not None:
    kw.update(REQUEST.form)

# BBB: in ancient CPS (at least before 3.4), this script used to be called
# with title argument. It still can happen although unprobable (especially
# unprobable with CPS Document types)
title = kw.get('title', '')
args = {'type_name': type_name}

from Products.CMFCore.utils import getToolByName
ti = getToolByName(context, 'portal_types').getTypeInfo(type_name)
create_form = ti.queryMethodID('create_form')

def create_form_redirect():
    return REQUEST.RESPONSE.redirect('%s/%s?%s'% (
            context.absolute_url_path(), create_form, urlencode(args)))

if REQUEST is not None:
    # Specific handling for portal_types of the CPSDocument family
    if ti.meta_type in ('CPS Flexible Type Information',
                        'Capsule Type Information'):
        # Passing a prefilled title (which is a bit of a hack) so
        # the title widget will be set with the given title in the CPSDocument
        # creation form.
        # GR: CPS Documents don't need this anymore, although prefilling
        # can be useful in some cases.
        if title:
            args['widget__Title'] = title
        if create_form is None:
            create_form = 'cpsdocument_create_form'
        return create_form_redirect()
    elif create_form is not None:
        # not a CPSDocument, but we'll redirect to appropriate form
        if title is not None:
            args['title'] = title
        return create_form_redirect()

# Specific handling for portal_types *not* of the CPSDocument family
# (for example CPSWiki documents and CPS Calendar documents) and without
# a "create_form" alias : the creation id on type_name if title not specified
new_id = context.computeId(compute_from=title or type_name)
context.invokeFactory(type_name, new_id)
ob = getattr(context, new_id)

try:
    doc = ob.getEditableContent()
except AttributeError:
    # not a proxy
    doc = ob
else:
    try:
        doc.edit(proxy=ob, **kw)
    except:
        # CMF Compatibility.
        # type_name not necessarly and edit method
        # for CMF types is not aware about that.
        if kw.has_key('type_name'):
            del kw['type_name']
        doc.edit(**kw)

from Products.CPSCore.EventServiceTool import getPublicEventService
evtool = getPublicEventService(context)
evtool.notifyEvent('modify_object', context, {})
evtool.notifyEvent('modify_object', ob, {})

if REQUEST is not None:
    psm = 'psm_content_created'
    action_path = doc.getTypeInfo().immediate_view
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                              (ob.absolute_url(), action_path,
                               psm))

return new_id
