##parameters=rev, REQUEST=None, **kw
"""
Revert a proxy to an older revision.
"""
# $Id$

proxy = context

language_revs = {
    proxy.getDefaultLanguage(): rev,
    }
proxy.revertToRevisions(language_revs)

if REQUEST is not None:
    redirect_url = '%s/?%s' % (context.absolute_url(),
                               'portal_status_message=psm_revision_reverted')
    REQUEST.RESPONSE.redirect(redirect_url)
