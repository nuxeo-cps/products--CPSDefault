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

    # Specific handling for portal_types of the CPSDocument family
    from Products.CMFCore.utils import getToolByName
    ti = getToolByName(context, 'portal_types').getTypeInfo(type_name)
    if ti.meta_type in ('CPS Flexible Type Information',
                        'Capsule Type Information'):
        args = {'type_name': type_name}
        # Passing a prefilled title (which is a bit of a hack) so
        # the title widget will be set with the given title in the CPSDocument
        # creation form.
        args['widget__Title'] = kw.get('title', '')

        return REQUEST.RESPONSE.redirect('%s/content_create?%s'
                                         % (context.absolute_url_path(),
                                            urlencode(args)))

# Specific handling for portal_types *not* of the CPSDocument family
# (for example CPSWiki documents and CPS Calendar documents).
#
# TODO: Redirect to the equivalent of a creation form prefilled with the given
# title so that the document is created with a corresponding title instead of a
# default title.
#
# Using the type_name as id for the creation if no title is specified
id = kw.get('title', type_name)
# Normalization of the id
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
    action_path = doc.getTypeInfo().immediate_view # getActionById('metadata')
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                              (ob.absolute_url(), action_path,
                               psm))

return id
