##parameters=REQUEST=None, **kw
# $Id$
"""Make unavailable a language in a CPS portal with Localizer"""

if REQUEST is not None:
    kw.update(REQUEST.form)

portal = context.portal_url.getPortalObject()
lang = kw['languages']

# Make unavailable languages in Localizer
catalogs = context.Localizer.objectValues()
catalogs.append(context.Localizer)
for catalog in catalogs:
    catalog.manage_delLanguages(lang)

context_url = portal.absolute_url()
action = 'language_manage_form'
psm = 'psm_language_deleted'

if REQUEST is not None:
    REQUEST.RESPONSE.redirect('%s/%s?&portal_status_message=%s' % (context_url, action, psm))
return psm
