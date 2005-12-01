##parameters=proxy=None, lang=None, REQUEST=None
# $Id$
"""Remove a translation from a proxy."""
if proxy is None:
    proxy = context

if not hasattr(proxy.aq_inner.aq_explicit, 'delLanguageFromProxy'):
    if REQUEST is None:
        raise ValueError("Not a proxy")
    psm = 'psm_translation_not_supported'
    url = proxy.absolute_url()
    action = proxy.getTypeInfo().getActionById('view')
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' % (
        url, action, psm))
    return

if lang is None:
    lang=proxy.getLanguage()

wftool = context.portal_workflow
wftool.doActionFor(proxy, 'delete_translation',
                   comment='%s' % lang, lang=lang)

psm = 'psm_translation_deleted'
if REQUEST is None:
    return psm
# redirect
url = proxy.absolute_url()
action = proxy.getTypeInfo().getActionById('view')
REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' % (
    url, action, psm))

