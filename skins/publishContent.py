##parameters=REQUEST=None, **kw                                                     
"""                                                                                 
Does the actual publication changes according to the user's choices
"""

if REQUEST is not None:
    kw.update(REQUEST.form)

publish_transition = 'publish' # XXX hardcoded... 

wftool = context.portal_workflow
portal = context.portal_url.getPortalObject()
allowed_transitions = wftool.getAllowedPublishingTransitions(context)
for transition in allowed_transitions:
    rpaths=kw.get(transition)
    if rpaths: # XXX fix if it is not a list !
        for rpath in rpaths:
            context.portal_workflow.doActionFor(context, publish_transition,
                                                dest_container=rpath,
                                                initial_transition=transition)

if REQUEST is not None:
    REQUEST.RESPONSE.redirect(context.absolute_url()+'/')
