## Script (Python) "content_status_modify"
##parameters=workflow_action, comment='', REQUEST=None, **kw
##title=Modify the status of a content object
# $Id$

wftool = context.portal_workflow

if REQUEST is not None:
    kw.update(REQUEST.form)

folder = context.aq_parent
id = context.getId()

if workflow_action != 'copy_submit':
    # accept, reject, ...
    wftool.doActionFor(context, workflow_action, comment=comment)
else:
    # publishing: copy and initalize proxy into one or more sections
    allowed_transitions = wftool.getAllowedPublishingTransitions(context)
    for transition in allowed_transitions:
        rpaths=kw.get(transition)
        if rpaths:
            if same_type(rpaths, ''):
                rpaths = (rpaths,)
            for rpath in rpaths:
                wftool.doActionFor(context, workflow_action,
                                   dest_container=rpath,
                                   initial_transition=transition,
                                   comment=comment)

if REQUEST is not None:
    # If the object has been deleted, we can't redirect to it.
    if id in folder.objectIds():
        url = context.absolute_url()
    else:
        url = folder.absolute_url()

    redirect_url = '%s/?%s' % (url, 'portal_status_message=Status+changed.')
    REQUEST.RESPONSE.redirect(redirect_url)
