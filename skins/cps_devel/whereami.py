##parameters=proxy=None
##

utool = context.portal_url

if proxy is None:
    proxy = context

print '<pre>'
print
print 'Zope info ---------------'
print 'object id (context):', proxy.getId()
print 'portal_type:', proxy.getPortalTypeName()
print ''
print 'absolute_url:', proxy.absolute_url()
print 'absolute_url(relative=1):', proxy.absolute_url(relative=1)
print 'getPhysicalPath:', proxy.getPhysicalPath()
print 'getRelativeContentUrl:', utool.getRelativeContentURL(proxy)
print 'getRelativeContentPath:', utool.getRelativeContentPath(proxy)
print 'getRelativeUrl:', utool.getRelativeUrl(proxy)


print 'aq_parent:', proxy.aq_parent.id
print 'aq_inner:', proxy.aq_inner.id
print 'container proxy.aq_inner.aq_parent:', proxy.aq_inner.aq_parent.id

print
print 'CPSDefault info ----------'
print 'here_url = proxy.absolute_url: ', proxy.absolute_url()
print 'base_url = proxy.getBaseUrl: ', proxy.getBaseUrl()
print 'context_url = proxy.getContextUrl: ', proxy.getContextUrl()
print 'in_ws = proxy.isInWorkspace: ', proxy.isInWorkspace()
print

try:
    doc = proxy.getContent()
except:
    doc = proxy


doc_path = '/'.join(doc.getPhysicalPath())
proxy_path = '/'.join(proxy.getPhysicalPath())

print 'ZCatalog proxy ---------------'
proxy_rid = proxy.portal_catalog.getrid(proxy_path)
print 'proxy %s' % proxy_path
print 'zcat.getrid(%s) = %s' % (proxy_path, proxy_rid)
print '<a href="portal_catalog/manage_objectInformation?rid=%s">view catalog info</a>' % proxy_rid
print

print 'ZCatalog doc --------------'
doc_rid = proxy.portal_catalog.getrid(doc_path)
print 'doc %s' % doc_path
print 'zcat.getrid(%s) = %s' % (doc_path, doc_rid)
print '<a href="portal_catalog/manage_objectInformation?rid=%s">view catalog info</a>' % doc_rid

print

try:
    print 'Searchable text CPSDocument ---------------'
    print 'doc.SearchableText=%s.' % doc.SearchableText()
    print
except:
    pass



print '</pre>'
return printed
