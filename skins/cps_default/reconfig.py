##parameters=REQUEST
#$Id$

"""This script just save the portal properties from the reconfig_form
template.
"""

container.manage_editProperties(REQUEST)
container.MailHost.smtp_host = REQUEST['smtp_server']
url = '%s/reconfig_form?portal_status_message=psm_portal_reconfigured'
return REQUEST.RESPONSE.redirect(url % container.portal_url())
