##parameters=REQUEST
# $Id$
""" Change the order/style of the item display within a folder """

context_url = REQUEST.get("context_url", context.getContextUrl())

# cps cookie checking
cps_cookie = REQUEST.SESSION.get('cps_display_params', {})

form = REQUEST.form

if form is not None:
    # Order and direction
    display_order = form.get("display_order")
    if display_order == "None" or not display_order:
        sort_by = None
        direction = None
    else:
        sort_by, direction = display_order.split('_')

    cps_cookie['sort_by'] = sort_by
    cps_cookie['direction'] = direction

    # Style
    format = form.get("display_style")
    if format == 'None':
        format = None

    cps_cookie['format'] = format

    # Update cookie
    REQUEST.SESSION['cps_display_params'] = cps_cookie

redirection_url = context_url + "/folder_contents"
REQUEST.RESPONSE.redirect(redirection_url)
