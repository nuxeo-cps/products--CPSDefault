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
    # XXX Nothing was actually unlocked...
    newid = context.getId()
else:
    newid = locked_ob.getId()
    wftool.doActionFor(context, 'abandon_draft')

if REQUEST is not None:
    url = folder.absolute_url()+'/'+newid
    redirect_url = '%s/?%s' % (url, 'portal_status_message=psm_status_changed')
    REQUEST.RESPONSE.redirect(redirect_url)
