##parameters=lang, proxy=None, REQUEST=None
# $Id$

if proxy is None:
    proxy = context

if not hasattr(proxy, 'addLanguageToProxy'):
    if REQUEST is None:
        raise ValueError("Not a proxy")
    psm = 'psm_translation_not_supported'
    url = proxy.absolute_url()

localizer = context.Localizer
if not lang in localizer.get_supported_languages():
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
    action = proxy.getTypeInfo().getActionById('view')
    REQUEST.RESPONSE.redirect('%s/switchLanguage/%s/%s?portal_status_message=%s' % (url, lang, action, psm))
