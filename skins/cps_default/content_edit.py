## Script (Python) "content_edit"
##title=Update Content and Metadata
##parameters=REQUEST=None, **kw

def tuplify( value ):
    if not same_type( value, () ):
        value = tuple( value )
    temp = filter( None, value )
    return tuple( temp )

if REQUEST is not None:
    kw.update(REQUEST.form)

doc = context.getEditableContent()

try:  
    # setting metadata, title and description are setup by doc.edit()
    if kw.get('subject'):
        doc.setSubject(tuplify(kw['subject']))
        del kw['subject']
    if kw.get('contributors'):
        doc.setContributors(tuplify(kw['contributors']))
        del kw['contributors']
    if kw.get('effective_date'):
        doc.setEffectiveDate(kw['effective_date'])
        del kw['effective_date']
    if kw.get('expiration_date') not in ('None', '', None):
        doc.setExpirationDate(kw['expiration_date'])
        del kw['expiration_date']
    if kw.get('format'):
        doc.setFormat(kw['format'])
        del kw['format']
    if kw.get('language'):
        doc.setLanguage(kw['language'])
        del kw['language']
    if kw.get('rights'):
        doc.setRights(kw['rights'])
        del kw['rights']
    
    if kw.get('allowDiscussion'):
        doc.portal_discussion.overrideDiscussionFor(doc, kw['allowDiscussion'])
        
        
    # setting properties, edit will notify the doc itself with a 'modify_object'
    doc.edit(**kw)
#    context.portal_eventservice.notifyEvent('modify_object', doc, {})
    
    # notifying the proxy
    context.portal_eventservice.notifyEvent('modify_object', context, {})
    
    psm = 'Content+changed.'
except Exception, msg:
    psm = msg

# redirect
if REQUEST:
    if REQUEST.get( 'change_and_edit', 0 ):
        action_id = 'edit'
    elif REQUEST.get( 'change_and_view', 0 ):
        action_id = 'view'
    else:
        action_id = 'metadata'
    action_path = doc.getTypeInfo().getActionById( action_id )

    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' % 
                              (context.absolute_url(), action_path,
                               psm))
return psm
