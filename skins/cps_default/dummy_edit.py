## Script (Python) "dummy_edit"
##parameters=body, description, choice=' Change '
##title=Edit a dummy
doc = context.getContent()
try:
    from Products.CMFDefault.utils import scrubHTML
    body = scrubHTML( body ) # Strip Javascript, etc.
    description = scrubHTML( description )
 
    doc.edit(body=body, description=description)

    qst='portal_status_message=Dummy+document+changed.'

    if choice == ' Change and View ':
        target_action = doc.getTypeInfo().getActionById( 'view' )
    else:
        target_action = doc.getTypeInfo().getActionById( 'edit' )

    context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                    , target_action
                                                    , qst
                                                    ) )
except Exception, msg:
    target_action = doc.getTypeInfo().getActionById( 'edit' )
    context.REQUEST.RESPONSE.redirect(
        '%s/%s?portal_status_message=%s' % ( context.absolute_url()
                                           , target_action
                                           , msg
                                           ) )
