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
    dfmt = mcat(fmt)
    ret = dt.strftime(dfmt)
    # space hack to fix %p strftime bug when LC_ALL=fr_FR
    if (dfmt.endswith('%p') and not ret.endswith('M')):
        h = int(dt.strftime('%H'))
        if h > 12:
            ret += ' PM'
        else:
            ret += ' AM'
except 'TimeError':
    ret = 'Invalid'

return ret


