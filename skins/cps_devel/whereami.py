##parameters=REQUEST, proxy=None
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
print 'base_url = utool.getBaseUrl: ', utool.getBaseUrl()
print 'context_url = proxy.getContextUrl: ', proxy.getContextUrl()
print 'in_ws = proxy.isInWorkspace: ', proxy.isInWorkspace()
print

doc = proxy.getContent()

doc_path = '/'.join(doc.getPhysicalPath())
proxy_path = '/'.join(proxy.getPhysicalPath())
if 'portal_repository' in doc_path:
    is_proxy = 1
else:
    is_proxy = 0

print 'CPS getContentInfo --------------'
print proxy.getContentInfo()
print

if is_proxy:
    print 'CPS Proxy -----------------------'
    languages = proxy.getProxyLanguages()
    print 'getProxyLanguages: %s' % languages
    print 'default language: %s' % proxy.getDefaultLanguage()
    print 'best language: %s rev: %s' % (proxy.getLanguage(),
                                         proxy.getRevision())
    print


    print 'ZCatalog proxy ---------------'
    proxy_rid = proxy.portal_catalog.getrid(proxy_path)
    if proxy_rid:
        print 'proxy %s' % proxy_path
        print 'zcat.getrid(%s) = %s' % (proxy_path, proxy_rid)
        print '<a href="portal_catalog/manage_objectInformation?rid=%s">view catalog info</a>' % proxy_rid
        print
    if languages:
        for language in languages:
            uid = proxy_path + '/viewLanguage/%s' % language
            proxy_rid = proxy.portal_catalog.getrid(uid)
            print 'language proxy %s' % uid
            print 'language zcat.getrid(%s) = %s' % (uid, proxy_rid)
            if proxy_rid:
                print '<a href="portal_catalog/manage_objectInformation?rid=%s">view catalog info</a>' % proxy_rid
            print
print

print 'ZCatalog doc --------------'
doc_rid = proxy.portal_catalog.getrid(doc_path)
print 'doc %s' % doc_path
print 'zcat.getrid(%s) = %s' % (doc_path, doc_rid)
if doc_rid:
    print '<a href="portal_catalog/manage_objectInformation?rid=%s">view catalog info</a>' % doc_rid

print

try:
    print 'Searchable text CPSDocument ---------------'
    print 'doc.SearchableText=%s.' % doc.SearchableText()
    print
except:
    pass

print '</pre>'

print REQUEST

return printed
