##parameters=REQUEST
# $Id$
""" Change the order/style of the item display within a folder """

context_url = REQUEST.get('context_url', context.getContextUrl())

# Retrieve display preference from session
display_params = REQUEST.SESSION.get('cps_display_params', {})

form = REQUEST.form

if form is not None:
    # Order and direction
    display_order = form.get('display_order')
    # "None" means use folder ordering
    if display_order == 'None' or not display_order:
        sort_by = None
        direction = None
    else:
        sort_by, direction = display_order.split('_')

    display_params['sort_by'] = sort_by
    display_params['direction'] = direction

    # Style
    format = form.get('display_style')
    if format:
        # XXX:
        # "None" means default here whereas None means "don't change"
        if format == 'None':
            format = None
        display_params['format'] = format

    # Update session
    REQUEST.SESSION['cps_display_params'] = display_params

redirection_url = context_url + '/folder_contents'
REQUEST.RESPONSE.redirect(redirection_url)
