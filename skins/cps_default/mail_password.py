##parameters=userid, REQUEST

try:
    return context.portal_registration.mailPassword(userid, REQUEST)
except "NotFound":
    REQUEST.RESPONSE.redirect("%s/mail_password_form?portal_status_message=%s" %
        (context.absolute_url(), "psm_join_invalid_name"))
