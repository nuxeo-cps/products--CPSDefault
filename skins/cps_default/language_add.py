##parameters=REQUEST=None, **kw
# $Id$
"""Make available a new language in a CPS portal with Localizer"""

if REQUEST is not None:
    kw.update(REQUEST.form)

portal = context.portal_url.getPortalObject()
languages = kw['languages']
if same_type(languages, ''):
    languages = [languages]

# Make languages available in Localizer
catalogs = context.Localizer.objectValues()
catalogs.append(context.Localizer)
for lang in languages:
    for catalog in catalogs:
        catalog.manage_addLanguage(lang)

# XXX needs a tools to register po files for domains
# Update Localizer/default only !
i18n_method = getattr(portal,'i18n Updater')
i18n_method()


context_url = portal.absolute_url()
action = 'language_manage_form'
psm = 'psm_language_added'

if REQUEST is not None:
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' % (context_url, action, psm))
return psm
