## Script (Python) "box_create"
##parameters=REQUEST=None, **kw
# $Id$
"""Add a box to the context, create a box container if needed."""

if REQUEST is not None:
    kw.update(REQUEST.form)

context.manage_addProduct['CPSDefault'].addBoxContainer(quiet=1)
idbc = context.portal_boxes.getBoxContainerId(context)
bc = getattr(context,idbc)


type_name = kw.get('type_name', 'Text Box')
id = kw.get('title')
if not id:
    id = 'my ' + type_name
id = bc.computeId(compute_from=id)

bc.invokeFactory(type_name, id)
ob = getattr(bc, id)
utool = context.portal_url
box_url = utool.getRelativeUrl(ob)

context_url = context.getContextUrl(utool=utool, concat=1)
if REQUEST is not None:
    psm = 'psm_box_created'
    action_path = ob.getTypeInfo().immediate_view
    REQUEST.RESPONSE.redirect('%s/%s?box_url=%s&portal_status_message=%s' % 
                              (context_url,action_path, box_url, psm))
return psm
