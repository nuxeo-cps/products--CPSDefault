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
    cookieName  = 'sort_by'

    if display_order == "None":
        cookieValue = None
        direction = 'asc'
    elif display_order == 'title_asc':
        cookieValue = 'title'
        direction = 'asc'
    elif display_order == 'title_desc':
        cookieValue = 'title'
        direction = 'desc'
    elif display_order == 'date_asc':
        cookieValue = 'date'
        direction = 'asc'
    elif display_order == 'date_desc':
        cookieValue = 'date'
        direction = 'desc'
    elif display_order == 'status_asc':
        cookieValue = 'status'
        direction = 'asc'
    elif display_order == 'status_desc':
        cookieValue = 'status'
        direction = 'desc'
    else:
        cookieValue = None
        direction = None

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
    display_direction = direction
    if display_direction is not None:
        cookieName  = 'direction'
        cookieValue = display_direction
        cps_cookie[cookieName] = cookieValue
        context.REQUEST.SESSION['cps_display_params'] = cps_cookie

redirection_url = context_url + "/folder_contents"
context.REQUEST.RESPONSE.redirect(redirection_url)
