## Script (Python) "getOnLoad.py"
#parameters=
##$Id$
""" return the body onload attribute content
"""
request = container.REQUEST

if request.has_key('URL'):
    URL = container.REQUEST['URL']
    if URL is not None and \
        (URL.endswith('search_form') or URL.endswith('advanced_search_form')):
        return 'highlightSearchTerm();'

return 'setfocus();'