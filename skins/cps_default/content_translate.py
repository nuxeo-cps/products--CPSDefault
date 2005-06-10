##parameters=lang, proxy=None, REQUEST=None

# $Id$

if proxy is None:
    proxy = context

if not hasattr(proxy, 'addLanguageToProxy'):
    if REQUEST is None:
        raise ValueError("Not a proxy")
    psm = 'psm_translation_not_supported'
    url = proxy.absolute_url()

translationservice = context.translation_service

if not lang in translationservice.getSupportedLanguages():
    if REQUEST is None:
        raise ValueError("Language '%s' not supported" % lang)
    psm = 'psm_translation_lang_not_supported'
    url = proxy.absolute_url()

wftool = context.portal_workflow
from_lang=proxy.getLanguage()
wftool.doActionFor(proxy, 'translate',
                   comment='%s' % lang,
                   lang=lang, from_lang=from_lang)
psm = 'psm_translation_added'
url = proxy.absolute_url()

if REQUEST is not None:
    from Products.CPSCore.utils import KEYWORD_SWITCH_LANGUAGE
    action = proxy.getTypeInfo().getActionById('edit')
    REQUEST.RESPONSE.redirect('%s/%s/%s/%s?portal_status_message=%s' % (
        url, KEYWORD_SWITCH_LANGUAGE, lang, action, psm))
