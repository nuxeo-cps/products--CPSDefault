##parameters=
"""
Returns the JavaScript code to put in the HTML body "onload" attribute.
"""

portal = context.portal_url.getPortalObject()

javascript = """
org.cps_cms.InformationMessageFetcher.portal_url = '%s';
org.cps_cms.InformationMessageFetcher.continuousFetch();
setFocus();
""" % portal.absolute_url()

URL = container.REQUEST.get('URL')
if URL is not None and \
    (URL.endswith('search_form') or URL.endswith('advanced_search_form')):
    return 'highlightSearchTerm(); ' + javascript

return javascript
