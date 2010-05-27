##parameters=
"""
Returns the JavaScript code to put in the HTML body "onload" attribute.
"""

javascript = 'setFocus();'

URL = container.REQUEST.get('URL')
if URL is not None and \
    (URL.endswith('search_form') or URL.endswith('advanced_search_form')):
    return 'highlightSearchTerm(); ' + javascript

return javascript
