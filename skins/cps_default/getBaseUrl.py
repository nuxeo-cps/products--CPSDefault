##parameters=utool=None
# $Id$
# return the base url of the cps server, ex: /cps/ or /

#return context.absolute_url(relative=1)+'/'
if not utool:
    utool = context.portal_url
REQUEST = getattr(context, 'REQUEST', None)
if REQUEST is None:
    path_info = ''
else:
    path_info = getattr(REQUEST, 'PATH_INFO', '')

if path_info.startswith('/VirtualHostBase/') :
    # apache detection
    return '/'
else:
    # XXX squid detection
    # classic case
    return utool.getPortalPath()+ '/'
