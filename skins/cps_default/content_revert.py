##parameters=rev, REQUEST=None, **kw
# $Id$
"""
Revert a proxy to an older revision.

FIXME: what are the parameters?
"""

proxy = context

language_revs = {
    proxy.getDefaultLanguage(): rev,
    }
proxy.revertToRevisions(language_revs)

if REQUEST is not None:
    redirect_url = '%s/?%s' % (context.absolute_url(),
                               'portal_status_message=psm_revision_reverted')
    REQUEST.RESPONSE.redirect(redirect_url)
