## Script (Python) "whereami.py"
##parameters=
##

utool = context.portal_url

ob = context
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
print 'Searchable text CPSDocument ---------------'
try:
    doc = context.getContent()
except:
    doc = context
print 'text=%s.' % doc.SearchableText()
return printed
