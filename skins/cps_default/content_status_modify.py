## Script (Python) "content_status_modify"
##parameters=workflow_action, comment='', REQUEST=None, **kw
##title=Modify the status of a content object
# $Id$
wftool = context.portal_workflow

if REQUEST is not None:
    kw.update(REQUEST.form)
 
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


redirect_url = '%s/view?%s' % (context.absolute_url()
                               , 'portal_status_message=Status+changed.'
                               )
if REQUEST is not None:
    REQUEST.RESPONSE.redirect(redirect_url)
