##parameters=lang
# $Id$
"""switch UI locale to lang, reset documents language selection done by switchLanguage."""
from Products.CPSCore.utils import resetSessionLanguageSelection

resetSessionLanguageSelection(context.REQUEST)

return context.Localizer.changeLanguage(lang=lang)