##parameters=came_from=None
"""Prepare user login

$Id$
"""

from urllib import unquote

def checkRedirect(portal, mtool):
    to_member_home = False
    to_workspaces = False
    has_home = mtool.getHomeFolder()
    if has_home:
        to_member_home = True
    if not has_home and mtool.checkPermission('View', portal.workspaces):
        to_workspaces = True
    return to_member_home, to_workspaces

utool = context.portal_url
mtool = context.portal_membership
dtool = context.portal_directories
portal = utool.getPortalObject()
portal_absolute_url = portal.absolute_url()

redirect_url = came_from
redirect_to_portal = False
to_member_home = False
to_workspaces = False

is_anon = mtool.isAnonymousUser()
member = mtool.getAuthenticatedMember()

if not redirect_url or redirect_url.endswith('/logged_out'):
    if not is_anon:
        to_member_home, to_workspaces = checkRedirect(portal, mtool)
    if (not to_member_home) and (not to_workspaces):
        redirect_to_portal = True
else:
    redirect_url = unquote(redirect_url)
    # One can be redirected from an http page while the login is done from an
    # https page. This is a fix for #1205.
    # A better option here would be to replace the previous portal_absolute_url
    # prefix in the redirect_url by the current portal absolute URL.
    if not redirect_url.startswith(portal_absolute_url):
        if not is_anon:
            to_member_home, to_workspaces = checkRedirect(portal, mtool)
        if (not to_member_home) and (not to_workspaces):
            redirect_to_portal = True

if to_member_home:
    redirect_url = mtool.getHomeFolder().absolute_url()
elif to_workspaces:
    redirect_url = portal.workspaces.absolute_url()
elif redirect_to_portal:
    redirect_url = portal_absolute_url

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

login_time = member.getProperty('login_time', '2000/01/01')
first_time = (str(login_time) == '2000/01/01')

if first_time and dtool.members.hasEntry(member.getId()):
    mtool.createMemberArea()
    now = context.ZopeTime()
    member.setProperties(last_login_time=now, login_time=now)

RESPONSE.redirect(redirect_url)
