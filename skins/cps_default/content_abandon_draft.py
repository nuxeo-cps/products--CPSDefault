##parameters=REQUEST=None, **kw
# $Id$

if REQUEST is not None:
    kw.update(REQUEST.form)

wftool = context.portal_workflow
folder_url = context.aq_parent.absolute_url()

locked_ob = context.getLockedObjectFromDraft()

if locked_ob is not None:
    url = folder_url+'/'+locked_ob.getId()
else:
    # Locked objet must have been deleted already.
    url = folder_url

wftool.doActionFor(context, 'abandon_draft')

if REQUEST is not None:
    redirect_url = '%s/?%s' % (url, 'portal_status_message=psm_status_changed')
    REQUEST.RESPONSE.redirect(redirect_url)
