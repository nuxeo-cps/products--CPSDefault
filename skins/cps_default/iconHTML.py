##parameters=
# $Id$
"""
Return the HTML for the current object's icon, if it is available.
"""

try:
    url = context.getIcon()
except (AttributeError, KeyError):
    try:
        url = context.icon
    except (AttributeError, KeyError):
        url = ''
if callable(url):
    url = url()

if not url:
    return ''

try:
    Type = context.Type()
except (AttributeError, KeyError):
    Type = ''

return '<img src="%s" align="left" alt="%s" />' % (url, Type)
