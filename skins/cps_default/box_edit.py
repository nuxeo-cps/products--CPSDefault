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

disp = kw.get('display')
if disp:
    del kw['display']
    if disp == 'closed':
        kw['closed'] = 1
    else:  
        kw['closed'] = 0      
        if disp == 'minimized':
            kw['minimized'] = 1
        elif disp == 'maximized':
            kw['minimized'] = 0

order = kw.get('order')
if order:
    kw['order'] = int(order)
    
box.edit(**kw)

context_urlc = context.getContextUrl(concat=1)
if REQUEST is not None:
    psm = 'Box+modified.'
    REQUEST.RESPONSE.redirect('%s/?portal_status_message=%s' % 
                              (context_urlc, psm))
return psm
