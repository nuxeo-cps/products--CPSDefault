##parameters=workflow_action, comment='', REQUEST=None, **kw
# $Id$
"""Generic workflow script to trigger the transitions"""

wftool = context.portal_workflow

if REQUEST is not None:
    kw.update(REQUEST.form)

# BBB: comment is now singular internally but not yet in all templates
comments = kw.get('comments', '')
if comments:
    del kw['comments']
comment = comment or comments
kw['comment'] = comment

folder = context.aq_parent
id = context.getId()
url = None

psm = 'psm_status_changed'

if wftool.isBehaviorAllowedFor(context, wftool.TRANSITION_BEHAVIOR_PUBLISHING,
                               transition=workflow_action):
    # cloning / publishing: copy and initalize proxy into one or more target
    # folders
    allowed_transitions = wftool.getAllowedPublishingTransitions(context)
    has_rpaths = False
    for transition in allowed_transitions:
        rpaths = kw.get(transition)
        if rpaths:
            has_rpaths = True
            if same_type(rpaths, ''):
                rpaths = (rpaths,)
            for rpath in rpaths:
                wftool.doActionFor(context, workflow_action,
                                   dest_container=rpath,
                                   initial_transition=transition,
                                   comment=comment)

    if not has_rpaths:
        # no target has been specified
        psm = 'psm_you_must_select_sections_for_publishing'

else:
    # accept, reject, ...
    res = wftool.doActionFor(context, workflow_action, **kw)
    if same_type(res, ()):
        if res[0] == 'ObjectMoved':
            rpath = res[1]
            url = context.portal_url()
            if not url.endswith('/'):
                url += '/'
            url += rpath

if REQUEST is not None:
    # If the object has been deleted, we can't redirect to it.
    if url is None:
        if id in folder.objectIds():
            url = context.absolute_url()
        else:
            url = folder.absolute_url()

    if psm == 'psm_you_must_select_sections_for_publishing':
        redirect_url = '%s/content_submit_form?%s' % (
            url, 'portal_status_message=%s'%psm)
    else:
        redirect_url = '%s/?%s' % (url, 'portal_status_message=%s'%psm)
    REQUEST.RESPONSE.redirect(redirect_url)
