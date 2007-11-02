##parameters=lang,REQUEST=None
# $Id$
"""
Switch UI locale to lang, reset documents language selection done by
switchLanguage.
"""

from Products.CPSCore.utils import resetSessionLanguageSelection

resetSessionLanguageSelection(context.REQUEST)

context.translation_service.changeLanguage(lang=lang)

if REQUEST is not None:
    referer = REQUEST['HTTP_REFERER']
    REQUEST.RESPONSE.redirect(referer)

