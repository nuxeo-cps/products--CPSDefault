## Script (Python) "changeDisplayParams"
##parameters=
# $Id$
""" Change the order/style of the item display within a folder """

portal_url  = context.portal_url()
context_url = context.REQUEST.get("context_url", context.getContextUrl())

# cps cookie checking
cps_cookie = context.REQUEST.SESSION.get('cps_display_params', {})

form = context.REQUEST.form
if form is not None:
    # Order
    display_order = form.get("display_order", None)
    if  display_order is not None:
        cookieName  = 'sort_by'
        cookieValue = display_order
        cps_cookie[cookieName] = cookieValue
        context.REQUEST.SESSION['cps_display_params'] = cps_cookie
    # Style
    display_style = form.get("display_style", None)
    if display_style is not None:
        cookieName  = 'format'
        cookieValue = display_style
        cps_cookie[cookieName] = cookieValue
        context.REQUEST.SESSION['cps_display_params'] = cps_cookie
    # Direction
    display_direction = form.get("display_direction", None)
    if display_direction is not None:
        cookieName  = 'direction'
        cookieValue = display_direction
        cps_cookie[cookieName] = cookieValue
        context.REQUEST.SESSION['cps_display_params'] = cps_cookie

redirection_url = context_url + "/folder_contents?change_display=1"
context.REQUEST.RESPONSE.redirect(redirection_url)
