##parameters=REQUEST=None, **kw
# $Id$

if REQUEST is not None:
    kw.update(REQUEST.form)

wftool = context.portal_workflow
folder = context.aq_parent

locked_ob = context.getLockedObjectFromDraft()

if locked_ob is None:
    # XXX Nothing was actually unlocked...
    newid = context.getId()
else:
    newid = locked_ob.getId()
    wftool.doActionFor(context, 'abandon_draft')

if REQUEST is not None:
    url = folder.absolute_url()+'/'+newid
    redirect_url = '%s/?%s' % (url, 'portal_status_message=psm_status_changed')
    REQUEST.RESPONSE.redirect(redirect_url)
