##parameters=REQUEST=None, **kw
# $Id$

wftool = context.portal_workflow

if REQUEST is not None:
    kw.update(REQUEST.form)

folder = context.aq_parent

# Find locked object
docid = context.getDocid()
flr = context.getFromLanguageRevisions()
locked_ob = None
for ob in folder.objectValues():
    try:
        rs = wftool.getInfoFor(ob, 'review_state', None)
        if (rs == 'locked' and
            ob.getDocid() == docid and
            ob.getLanguageRevisions() == flr):
            locked_ob = ob
            break
    except:
        from zLOG import LOG, DEBUG
        LOG('content_checkin_draft', DEBUG, 'exception in folder=%s' % folder)
        raise

if locked_ob is None:
    raise ValueError('Nowhere to checkin')

newid = locked_ob.getId()
wftool.doActionFor(context, 'checkin_draft',
                   dest_container=folder,
                   dest_objects=[locked_ob],
                   checkin_transition="unlock")

if REQUEST is not None:
    url = folder.absolute_url()+'/'+newid
    redirect_url = '%s/?%s' % (url, 'portal_status_message=psm_status_changed')
    REQUEST.RESPONSE.redirect(redirect_url)
