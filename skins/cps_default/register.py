##parameters=password='password', confirm='confirm'

from re import match

request = context.REQUEST
portal_properties = context.portal_properties
portal_registration = context.portal_registration

# converts CMFDefault/RegistrationTool.py sentences into msgids
conversion = {
    'Your password must contain at least 5 characters.':
        'psm_join_password_too_short',
    'Your password and confirmation did not match. Please try again.':
        'psm_join_password_mismatch',
    'You must enter a valid name.':
        'psm_join_invalid_name',
    'The login name you selected is already '
        'in use or is not valid. Please choose another.':
            'psm_join_login_already_used',
    'You must enter a valid email address.':
        'psm_join_invalid_email',
}

# password checking
if not portal_properties.validate_email:
    failMessage = portal_registration.testPasswordValidity(password, confirm)
    if failMessage and request is not None:
        request.set('portal_status_message',
                    conversion.get(failMessage, failMessage))
        return context.join_form(context, request)

# other fields checking
failMessage = portal_registration.testPropertiesValidity(request)
if failMessage:
    request.set('portal_status_message',
                conversion.get(failMessage, failMessage))
    return context.join_form(context, request)

# email validity checking
email = request.get('email', '')
if not match(r'^(\w(\.|\-)?)+@(\w(\.|\-)?)+\.[A-Za-z]{2,4}$', email):
    request.set('portal_status_message', 'psm_join_invalid_email')
    return context.join_form(context, request)

# now adds the member
password = request.get('password') or portal_registration.generatePassword()
username = request['username']
try:
    portal_registration.addMember(username, password, properties=request)
except ValueError:
    request.set('portal_status_message',
                conversion.get(failMessage, failMessage))
    return context.join_form(context, request)

# asked for email sending
if portal_properties.validate_email or request.get('mail_me'):
    portal_registration.registeredNotify(username)

return context.registered(context, request)
