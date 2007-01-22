##parameters=REQUEST
# $Id$
"""Script used to call the recursivePublish method.
"""

from Products.CPSDefault.recursivepublish import recursivePublish

proxy = context
recursivePublish(workspace=proxy, context=context)

url = proxy.absolute_url()
psm = 'psm_recursive_publish_done'
REQUEST.RESPONSE.redirect('%s?portal_status_message=%s' % (url, psm))

