## Script (Python) "whereami.py"
##parameters=
##

utool = context.portal_url

ob = context
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

return printed 
