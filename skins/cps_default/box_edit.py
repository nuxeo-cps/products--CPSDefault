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

# handle checkbox
for k in ('display_in_subfolder', 'children_only', 'contextual'):
    v = kw.get(k)
    kw[k] = not not v

order = kw.get('order')
if order:
    kw['order'] = int(order)

sf = kw.get('styleformat')
if sf:
    kw['style']=sf.split('@')[0]
    kw['format']=sf.split('@')[1]
    # override with hard coded configuration
    bs = context.getBoxesStyles(type=box_type)
    if bs:
        config = {}
        fmt = bs['fmt']
        for f in fmt:
            if f['style'] == kw['style'] and f['format'] == kw['format']:
                config = f.get('config', {})
                break
        kw.update(config)

    del kw['styleformat']

box.edit(**kw)

if REQUEST is not None:
    psm = 'psm_box_modified'
    action_path = context.getTypeInfo().getActionById('boxes')
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                              (context.absolute_url(), action_path,
                               psm))
return psm
