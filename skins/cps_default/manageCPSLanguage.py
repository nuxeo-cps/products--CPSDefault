##parameters
# $Id$
"""
Make available a new language in a CPS portal with Localizer
"""

# FIXME: localizergeddon

from Products.CPSDefault.utils import manageCPSLanguage

request = context.REQUEST
context_url = context.portal_url.getPortalObject().absolute_url()
template = 'language_manage_form'
psm = ''

if request is not None:
    action = request.form.get('action')
    languages = request.form.get('languages')
    language = request.form.get('default_language')
    psm = manageCPSLanguage(context, action, language, languages)

if request is not None:
    request.RESPONSE.redirect('%s/%s?portal_status_message=%s' % (context_url, template, psm))
return psm

