##parameters=REQUEST=None, **kw
# $Id$
"""
Delete a box.

FIXME: which one ?
"""

if REQUEST is not None:
    kw.update(REQUEST.form)

box_url = kw.get('box_url', [])

box = context.restrictedTraverse(box_url)
bc = box.aq_parent
bc.manage_delObjects(box.getId())

if REQUEST is not None:
    psm = 'psm_box_deleted'
    action_path = 'box_manage_form'
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                              (context.absolute_url(), action_path,
                               psm))
return psm
