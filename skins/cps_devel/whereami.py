## Script (Python) "whereami.py"
##parameters=
##

utool = context.portal_url

ob = context
print '<pre>'
print
print 'Zope info ---------------'
print 'object id (context):', ob.getId()
print 'portal_type:', ob.getPortalTypeName()
print ''
print 'absolute_url:', ob.absolute_url()
print 'absolute_url(relative=1):', ob.absolute_url(relative=1)
print 'getPhysicalPath:', ob.getPhysicalPath()
print 'getRelativeContentUrl:', utool.getRelativeContentURL(ob)
print 'getRelativeContentPath:', utool.getRelativeContentPath(ob)
print 'getRelativeUrl:', utool.getRelativeUrl(ob)


print 'aq_parent:', ob.aq_parent.id
print 'aq_inner:', ob.aq_inner.id
print 'container ob.aq_inner.aq_parent:', ob.aq_inner.aq_parent.id

print
print 'CPSDefault info ----------'
print 'here_url = context.absolute_url: ', context.absolute_url()
print 'base_url = context.getBaseUrl: ', context.getBaseUrl()
print 'context_url = context.getContextUrl: ', context.getContextUrl()
print 'in_ws = context.isInWorkspace: ', context.isInWorkspace()
print

try:
    doc = context.getContent()
except:
    doc = context

try:
    print 'Searchable text CPSDocument ---------------'
    print 'text=%s.' % doc.SearchableText()
    print
except:
    pass


print 'CPSDocument ------------'
path = '/'.join(doc.getPhysicalPath())
print 'doc path: %s' % path
print

print 'ZCatalog ---------------'
rid = doc.portal_catalog.getrid(path)
print 'zcat.getrid(%s) = %s' % (path, rid)
print '<a href="portal_catalog/manage_objectInformation?rid=%s>view catalog info</a>' % rid
#zinfo = context.portal_catalog.manage_objectInformation(rid=rid)
#print zinfo
#utool.getRelativeUrl(doc)
#print 'path = %s' % doc.portal_catalog.getpath(-1656972463)

print '</pre>'
return printed
