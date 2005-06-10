##parameters=lang
# $Id$
"""
Switch UI locale to lang, reset documents language selection done by
switchLanguage.
"""

from Products.CPSCore.utils import resetSessionLanguageSelection

resetSessionLanguageSelection(context.REQUEST)

return context.translation_service.changeLanguage(lang=lang)
