## Script (Python) "box_edit"
##parameters=REQUEST=None, **kw
# $Id$
"""Edit an existing box."""

if REQUEST is not None:
    kw.update(REQUEST.form)

box_url = kw['box_url']
del kw['box_url']
box_type = kw['box_type']
del kw['box_type']

box = context.restrictedTraverse(box_url)

sf = kw.get('styleformat')
if sf:
    styles = context.getBoxesStyles(type=box_type)
    kw['style']=sf.split('@')[0]
    kw['format']=sf.split('@')[1]
    del kw['styleformat']

disp = kw.get('display_box')
if disp:
    del kw['display_box']
    if disp == 'closed':
        kw['closed'] = 1
    else:
        kw['closed'] = 0
        if disp == 'minimized':
            kw['minimized'] = 1
        elif disp == 'maximized':
            kw['minimized'] = 0

disf = kw.get('display_in_subfolder')
kw['display_in_subfolder'] = not not disf

order = kw.get('order')
if order:
    kw['order'] = int(order)

box.edit(**kw)

if REQUEST is not None:
    psm = 'psm_box_modified'
    action_path = context.getTypeInfo().getActionById('boxes')
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                              (context.absolute_url(), action_path,
                               psm))
return psm
