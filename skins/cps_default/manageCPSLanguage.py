##parameters
# -*- coding: iso-8859-15 -*-
# $Id$
"""Make available a new language in a CPS portal with Localizer"""
from Products.CPSCore.utils import manageCPSLanguage

request = context.REQUEST
context_url = context.portal_url.getPortalObject().absolute_url()
template = 'language_manage_form'
psm = ''

if request is not None:
    kw = {}
    kw.update(request.form)
    psm = manageCPSLanguage(context, **kw)

if request is not None:
    request.RESPONSE.redirect('%s/%s?portal_status_message=%s' % (context_url, template, psm))
return psm

