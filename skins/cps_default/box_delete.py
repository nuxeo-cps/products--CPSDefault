## Script (Python) "box_delete"
##parameters=REQUEST=None, **kw
# $Id$
"""Delete boxes."""

if REQUEST is not None:
    kw.update(REQUEST.form)

ids = kw.get('ids', [])

for boxurl in ids:
    box = context.restrictedTraverse(boxurl)
    bc = box.aq_parent
    bc.manage_delObjects(box.id)


if REQUEST is not None:
    psm = 'psm_box_deleted'
    action_path = context.getTypeInfo().getActionById('boxes')
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                              (context.absolute_url(), action_path,
                               psm))
return psm
