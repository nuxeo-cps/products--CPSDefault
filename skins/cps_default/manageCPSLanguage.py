##parameters=REQUEST=None, **kw
# -*- coding: iso-8859-15 -*-
# $Id$
"""Make available a new language in a CPS portal with Localizer"""

if REQUEST is not None:
    kw.update(REQUEST.form)

action = kw.get('action')
languages = kw.get('languages')
lang = kw.get('language')
catalogs = context.Localizer.objectValues()
catalogs.append(context.Localizer)
portal = context.portal_url.getPortalObject()
context_url = portal.absolute_url()
template = 'language_manage_form'

if same_type(languages, ''):
    languages = [languages]

if languages is None and action in ('add', 'delete'):
    psm = 'psm_language_error_select_at_least_one_item'

elif action == 'add':
    # Make languages available in Localizer
    for lang in languages:
        for catalog in catalogs:
            catalog.manage_addLanguage(lang)

    # XXX needs a tools to register po files for domains
    # Update Localizer/default only !
    i18n_method = getattr(portal,'i18n Updater')
    i18n_method()
    psm = 'psm_language_added'

elif action == 'delete':
    # Make unavailable languages in Localizer
    for catalog in catalogs:
        catalog.manage_delLanguages(languages)
    psm = 'psm_language_deleted'

elif action == 'chooseDefault':
    for catalog in catalogs:
        catalog.manage_changeDefaultLang(lang)
    psm = 'psm_default_language_set'

else:
    psm = ''

if REQUEST is not None:
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' % (context_url, template, psm))
return psm
