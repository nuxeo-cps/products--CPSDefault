##parameters=REQUEST
#$Id$
"""
This script just saves the portal properties from the reconfig_form
template.
"""

form = REQUEST.form

# It is better here to avoid the following call, because if the REQUEST is
# passed, manage_changeProperties will return an unneeded HTML form which is
# overkill and in some cases has produced some undesirable effects.
#
#container.portal_properties.manage_changeProperties(REQUEST)
#
# So we call manage_changeProperties with explicit properties
container.portal_properties.manage_changeProperties(
    email_from_name=form.get('email_from_name'),
    email_from_address=form.get('email_from_address'),
    smtp_server=form.get('smtp_server'),
    title=form.get('title'),
    description=form.get('description'),
    enable_password_reset=form.get('enable_password_reset'),
    enable_password_reminder=form.get('enable_password_reminder'),
    enable_portal_joining=form.get('enable_portal_joining'),
    )

url = '%s/reconfig_form?portal_status_message=psm_portal_reconfigured'
return REQUEST.RESPONSE.redirect(url % container.portal_url())
