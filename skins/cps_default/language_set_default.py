##parameters=REQUEST=None, **kw
# $Id$
"""Set default language in a CPS portal with Localizer"""

if REQUEST is not None:
    kw.update(REQUEST.form)

portal = context.portal_url.getPortalObject()
lang = kw['language']

# Make unavailable languages in Localizer
catalogs = context.Localizer.objectValues()
catalogs.append(context.Localizer)
for catalog in catalogs:
    catalog.manage_changeDefaultLang(lang)

context_url = portal.absolute_url()
action = 'language_manage_form'
psm = 'psm_default_language_set'

if REQUEST is not None:
    REQUEST.RESPONSE.redirect('%s/%s?&portal_status_message=%s' % (context_url, action, psm))
return psm
