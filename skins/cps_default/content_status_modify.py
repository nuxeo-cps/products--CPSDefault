##parameters=workflow_action, REQUEST=None, **kw
# $Id$
"""
FIXME: add docstring.
"""

wftool = context.portal_workflow

if REQUEST is not None:
    kw.update(REQUEST.form)

comments = kw.get('comments', '')

folder = context.aq_parent
id = context.getId()
url = None

if workflow_action != 'copy_submit':
    # accept, reject, ...
    res = wftool.doActionFor(context, workflow_action, **kw)
    if same_type(res, ()):
        if res[0] == 'ObjectMoved':
            rpath = res[1]
            url = context.portal_url()
            if not url.endswith('/'):
                url += '/'
            url += rpath
else:
    # publishing: copy and initalize proxy into one or more sections
    allowed_transitions = wftool.getAllowedPublishingTransitions(context)
    for transition in allowed_transitions:
        rpaths = kw.get(transition)
        if rpaths:
            if same_type(rpaths, ''):
                rpaths = (rpaths,)
            for rpath in rpaths:
                wftool.doActionFor(context, workflow_action,
                                   dest_container=rpath,
                                   initial_transition=transition,
                                   comment=comments)

if REQUEST is not None:
    # If the object has been deleted, we can't redirect to it.
    if url is None:
        if id in folder.objectIds():
            url = context.absolute_url()
        else:
            url = folder.absolute_url()

    redirect_url = '%s/?%s' % (url, 'portal_status_message=psm_status_changed')
    REQUEST.RESPONSE.redirect(redirect_url)
