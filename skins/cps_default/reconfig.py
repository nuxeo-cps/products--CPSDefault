##parameters=
#$Id$

"""
This script just save the portal properties from the reconfig_form template.
"""

REQUEST=context.REQUEST
context.portal_properties.editProperties(REQUEST)
return REQUEST.RESPONSE.redirect(context.portal_url() + \
                                 '/reconfig_form?portal_status_message=%s' \
                                 % ('psm_portal_reconfigured', ))
