##parameters=dt=None, fmt='medium'
# $Id$
""" return a string date using the current locale """

from DateTime.DateTime import DateTimeError

if not dt:
    return ''

Localizer = context.Localizer
mcat = Localizer.default

if fmt in ('short', 'medium', 'long'):
    # This string will be used to retrieve format in the right .po file
    fmt = 'date_' + fmt
# For iso8601 dates read http://www.w3.org/TR/NOTE-datetime
elif fmt not in ('iso8601', 'iso8601_short', 'iso8601_medium', 'iso8601_long',
                 'iso8601_medium_easy', 'iso8601_long_easy'):
    fmt = 'iso8601_medium_easy'

try:
    if fmt == 'iso8601_short' or fmt == 'iso8601':
        dfmt = '%Y-%m-%d'
    elif fmt == 'iso8601_medium':
        dfmt = '%Y-%m-%dT%H:%MZ'
    elif fmt == 'iso8601_medium_easy':
        dfmt = '%Y-%m-%d %H:%M'
    elif fmt == 'iso8601_long':
        dfmt = '%Y-%m-%dT%H:%M:%SZ'
    elif fmt == 'iso8601_long_easy':
        dfmt = '%Y-%m-%d %H:%M:%S'
    else:
        dfmt = mcat(fmt)
    ret = dt.strftime(dfmt)
    # XXX remove this as soon as strftime is fixed
    # space hack to fix %p strftime bug when LC_ALL=fr_FR
    if (dfmt.endswith('%p') and not ret.endswith('M')):
        h = int(dt.strftime('%H'))
        if h > 12:
            ret += ' PM'
        else:
            ret += ' AM'
except DateTimeError:
    ret = 'Invalid'

return ret
