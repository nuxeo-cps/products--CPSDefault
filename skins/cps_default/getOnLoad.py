##parameters=
"""
Returns the JavaScript code to put in the HTML body "onload" attribute.
"""

portal = context.portal_url.getPortalObject()
mtool = portal.portal_membership
infotool = portal.portal_information_message

is_anon = mtool.isAnonymousUser()
URL = container.REQUEST.get('URL', '')

javascript = ""
if not is_anon and not URL.endswith('information_message_config_form'):
    javascript = """
    org.cps_cms.InformationMessageFetcher.portal_url = '%s';
    org.cps_cms.InformationMessageFetcher.check_delay_initial = %s;
    org.cps_cms.InformationMessageFetcher.check_delay = %s;
    org.cps_cms.InformationMessageFetcher.continuousCheckForInformationMessage();
    """ % (portal.absolute_url(),
           infotool.check_delay_initial,
           infotool.check_delay)

javascript += "setFocus();"

if URL.endswith('search_form') or URL.endswith('advanced_search_form'):
    return 'highlightSearchTerm(); ' + javascript

return javascript
