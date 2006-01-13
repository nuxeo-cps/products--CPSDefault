##parameters=REQUEST
#$Id$
"""
This script just saves the portal properties from the reconfig_form
template.
"""

portal = context.portal_url.getPortalObject()
form = REQUEST.form

# XXX The portal_properties API is dumb, so we change properties directly
# on the portal object.
portal.manage_changeProperties(
    email_from_name=form.get('email_from_name'),
    email_from_address=form.get('email_from_address'),
    title=form.get('title'),
    description=form.get('description'),
    enable_password_reset=form.get('enable_password_reset'),
    enable_password_reminder=form.get('enable_password_reminder'),
    enable_portal_joining=form.get('enable_portal_joining'),
    )

# Take care of updating the MailHost tool
portal.portal_properties.editProperties({
    'smtp_server': form.get('smtp_server'),
    })

url = '%s/config_form?portal_status_message=psm_portal_reconfigured'
return REQUEST.RESPONSE.redirect(url % portal.portal_url())
