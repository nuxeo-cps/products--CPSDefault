##parameters=comment='', REQUEST=None, **kw
# $Id$

if REQUEST is not None:
    kw.update(REQUEST.form)

wftool = context.portal_workflow
folder = context.aq_parent

locked_ob = context.getLockedObjectFromDraft()

if locked_ob is not None:
    newid = locked_ob.getId()
    wftool.doActionFor(context, 'checkin_draft',
                       dest_container=folder,
                       dest_objects=[locked_ob],
                       checkin_transition="unlock",
                       comment=comment)
else:
    # Locked has been deleted, directly unlock the draft.
    newid = context.getId()
    wftool.doActionFor(context, 'unlock', comment=comment)
    # XXX Could rename to original id, if we had it.

if REQUEST is not None:
    url = folder.absolute_url()+'/'+newid
    redirect_url = '%s/?%s' % (url, 'portal_status_message=psm_status_changed')
    REQUEST.RESPONSE.redirect(redirect_url)
