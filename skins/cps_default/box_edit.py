##parameters=REQUEST=None, **kw
# $Id$
"""
Edit an existing box.

FIXME: which one ?
"""

if REQUEST is not None:
    kw.update(REQUEST.form)

if kw.get('back'):
    return REQUEST.RESPONSE.redirect('%s/box_manage_form' %
                                     (context.absolute_url()))

box_url = kw['box_url']
del kw['box_url']
box_category = kw['box_category']
del kw['box_category']

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
          'children_only', 'contextual', 'zoom','display_managers',
          'authorized_only','show_root', 'display_description',
          'display_icons', 'i18n', 'no_recurse'):
    kw[k] = test(kw.has_key(k), 1, 0)

# handle empty selection in contentbox_edit_form
if not kw.get('query_portal_type'):
    kw['query_portal_type'] = ['']

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
    kw['provider'], kw['btype'] = sf.split('@')
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

# handle contentbox
if kw.has_key('display_order'):
    display_order = kw['display_order']
    if display_order == "None" or not display_order:
        kw['sort_by'] = None
        kw['direction'] = None
    else:
        kw['sort_by'], kw['direction'] = display_order.split('_')
    del kw['display_order']

if kw.has_key('display_style'):
    kw['display'] = kw['display_style']
    if kw['display'] == 'None':
        kw['display'] = None
    del kw['display_style']

box = context.restrictedTraverse(box_url)
box.edit(**kw)

psm = 'psm_box_modified'

if REQUEST is not None:
    if kw.get('change_and_edit'):
        action_path = box.getTypeInfo().immediate_view
        psm = psm + '&box_url=' + box_url
    else:
        action_path = 'box_manage_form'
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                              (context.absolute_url(), action_path,
                               psm))
return psm
