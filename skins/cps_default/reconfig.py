##parameters=REQUEST
#$Id$

"""This script just save the portal properties from the reconfig_form
template.
"""

container.portal_properties.editProperties(REQUEST)
# manually update enable_portal_joining afterwards
enable_portal_joining = getattr(REQUEST, 'enable_portal_joining', 0)
container.manage_changeProperties(enable_portal_joining=enable_portal_joining)
url = '%s/reconfig_form?portal_status_message=psm_portal_reconfigured'
return REQUEST.RESPONSE.redirect(url % container.portal_url())
