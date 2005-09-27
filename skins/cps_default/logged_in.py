##parameters=
"""Prepare use login

$Id$
"""

utool = context.portal_url
mtool = context.portal_membership
p_props = context.portal_properties

base_url = utool.getBaseUrl()
is_anon = mtool.isAnonymousUser()
member = mtool.getAuthenticatedMember()

REQUEST = context.REQUEST
RESPONSE = REQUEST.RESPONSE

# Setup skins
if (getattr(utool, 'updateSkinCookie', False) and
    utool.updateSkinCookie()):
    context.setupCurrentSkin()

# Anonymous
if is_anon:
    RESPONSE.expireCookie('__ac', path='/')
    return context.user_logged_in_failed()

login_time = member.getProperty('login_time', None)
first_time = (str(login_time) == '2000/01/01')

if first_time:
    mtool.createMemberArea()
    now = context.ZopeTime()
    member.setProperties(last_login_time=now, login_time=now)
RESPONSE.redirect(base_url)


