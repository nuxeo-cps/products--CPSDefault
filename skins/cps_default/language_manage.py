##parameters=REQUEST=None, **kw
# $Id$
"""Synchronize language used in a CPS portal with Localizer"""

if REQUEST is not None:
    kw.update(REQUEST.form)

portal = context.portal_url.getPortalObject()

raise "debug", repr(kw)

context_url = portal.absolute_url()
action = 'language_manage_form'
psm = 'psm_language_manage'

if REQUEST is not None:
    REQUEST.RESPONSE.redirect('%s/%s?&portal_status_message=%s' % (context_url, action, psm))
return psm
