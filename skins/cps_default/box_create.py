##parameters=REQUEST=None, **kw
# $Id$
"""
Add a box to the context, create a box container if needed.
"""

if REQUEST is not None:
    kw.update(REQUEST.form)

context.manage_addProduct['CPSDefault'].addBoxContainer(quiet=1)
idbc = context.portal_boxes.getBoxContainerId(context)
bc = getattr(context,idbc)

slot_name = kw.get('slot_name')
if slot_name is not None:
    kw['slot'] = slot_name

type_name = kw.get('type_name', 'Text Box')
id = kw.get('title')
if not id:
    id = 'my ' + type_name
id = bc.computeId(compute_from=id)

bc.invokeFactory(type_name, id)
ob = getattr(bc, id)
ob.edit(**kw)

utool = context.portal_url
box_url = utool.getRelativeUrl(ob)

context_url = context.getContextUrl(utool=utool, concat=1)
psm = 'psm_box_created'

if REQUEST is not None:
    action_path = ob.getTypeInfo().immediate_view
    REQUEST.RESPONSE.redirect('%s/%s?box_url=%s&portal_status_message=%s' % 
                              (context_url, action_path, box_url, psm))
return psm
