##parameters=REQUEST
#$Id$

"""This script just save the portal properties from the reconfig_form
template.
"""

container.portal_properties.manage_editProperties(REQUEST)
url = '%s/reconfig_form?portal_status_message=psm_portal_reconfigured'
return REQUEST.RESPONSE.redirect(url % context.portal_url())
