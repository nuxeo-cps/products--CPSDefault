## Script (Python) "getDateStr"
##parameters=dt=None, fmt='medium'
# $Id$
""" return a string date using the current locale """

if not dt:
    return ''

Localizer = context.Localizer
mcat = Localizer.default

if fmt not in ['short', 'medium', 'long']:
    fmt = 'date_long'
else:
    fmt = 'date_'+fmt

try:
    ret = dt.strftime(mcat(fmt))
except 'TimeError':
    ret = 'Invalid'

return ret


