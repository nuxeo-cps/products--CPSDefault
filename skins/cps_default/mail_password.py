##parameters=username, REQUEST

try:
    return context.portal_registration.mailPassword(username, REQUEST)
except ValueError:
    REQUEST.RESPONSE.redirect("%s/account_lost_password_form?portal_status_message=%s" %
        (context.absolute_url(), 'psm_join_invalid_name'))
