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
    # Order and direction
    display_order = form.get("display_order", None)
    if display_order == "None":
        sort_by = None
        direction = None
    else:
        sort_by, direction = display_order.split('_')

    cps_cookie['sort_by'] = sort_by
    cps_cookie['direction'] = direction

    # Style
    format = form.get("display_style", None)
    if format == 'None':
        format = None
    cps_cookie['format'] = format

    # Update cookie
    context.REQUEST.SESSION['cps_display_params'] = cps_cookie

redirection_url = context_url + "/folder_contents"
context.REQUEST.RESPONSE.redirect(redirection_url)
