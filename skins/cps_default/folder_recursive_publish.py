##parameters=REQUEST
# $Id$
"""Script used to call the recursivePublish method.
"""

from Products.CPSDefault.recursivepublish import recursivePublish

target_section_rpath = REQUEST.form.get('target_section_rpath')
proxy = context
recursivePublish(proxy, target_section_rpath, context)

url = proxy.absolute_url()
psm = 'psm_recursive_publish_done'
REQUEST.RESPONSE.redirect('%s?portal_status_message=%s' % (url, psm))

