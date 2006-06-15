##parameters=comments='', REQUEST=None, **kw
# $Id$
"""
FIXME: add docstring.
"""

wftool = context.portal_workflow

# FIXME: kw is not used at all, why put this code in the first place?
if REQUEST is not None:
    kw.update(REQUEST.form)

folder = context.aq_inner.aq_parent

newid = wftool.findNewId(folder, context.getId())
wftool.doActionFor(context, 'checkout_draft',
                   dest_container=folder,
                   initial_transition='checkout_draft_in',
                   comment=comments)

if REQUEST is not None:
    url = folder.absolute_url()+'/'+newid
    redirect_url = '%s/?%s' % (url, 'portal_status_message=psm_status_changed')
    REQUEST.RESPONSE.redirect(redirect_url)
