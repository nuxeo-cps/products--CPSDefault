##parameters=rev, REQUEST=None, **kw
# $Id$
"""
Delete an archived revision of a proxy.

FIXME: what are the parameters?
"""

proxy = context
proxy.delArchivedRevisions([rev])

if REQUEST is not None:
    redirect_url = '%s/content_status_history?portal_status_message=%s' % (
        context.absolute_url(),
        'psm_archive_deleted')
    REQUEST.RESPONSE.redirect(redirect_url)
