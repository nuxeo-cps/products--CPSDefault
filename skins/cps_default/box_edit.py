## Script (Python) "box_edit"
##parameters=REQUEST=None, **kw
# $Id$
"""Edit an existing box."""

if REQUEST is not None:
    kw.update(REQUEST.form)

box_url = kw['box_url']
del kw['box_url']
box_category = kw['box_category']
del kw['box_category']

box = context.restrictedTraverse(box_url)

# handle box display
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
for k in ('display_in_subfolder', 'display_only_in_subfolder',
          'children_only', 'contextual'):
    v = kw.get(k)
    kw[k] = not not v


# handle center box slot
# center box are use in folder_view to skin only one folder
slot = kw.get('slot')
if slot == 'center':
    kw['display_only_in_subfolder'] = 0
    kw['display_in_subfolder'] = 0


# handle integer
order = kw.get('order')
if order:
    kw['order'] = int(order)

# handle provider type
sf = kw.get('providertype')
if sf:
    kw['provider']=sf.split('@')[0]
    kw['btype']=sf.split('@')[1]
    # override with hard coded configuration
    category = context.getBoxTypes(category=box_category)
    if category:
        config = {}
        types = category['types']
        for t in types:
            if t['provider'] == kw['provider'] and t['id'] == kw['btype']:
                config = t.get('config', {})
                break
        kw.update(config)

    del kw['providertype']

box.edit(**kw)

if REQUEST is not None:
    psm = 'psm_box_modified'
    action_path = context.getTypeInfo().getActionById('boxes')
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                              (context.absolute_url(), action_path,
                               psm))
return psm
