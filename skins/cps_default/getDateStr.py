## Script (Python) "getDateStr"
##parameters=dt=None, fmt='medium'
# $Id$
""" return a string date using the current locale """

Localizer = context.Localizer
mcat = Localizer.default

if not dt:
    return ''

if fmt not in ['short', 'medium', 'long']:
    fmt = 'date_long'
else:
    fmt = 'date_'+fmt

ret = dt.strftime(mcat(fmt))

return ret


