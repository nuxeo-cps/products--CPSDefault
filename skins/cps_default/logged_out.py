##parameters=
REQUEST = context.REQUEST

if context.portal_membership.isAnonymousUser():
    url = context.portal_url()+'/?portal_status_message=description_logout_success'
    REQUEST.RESPONSE.redirect(url)
    return

# still logged in at zope level
REQUEST.RESPONSE.redirect('/manage_zmi_logout')
