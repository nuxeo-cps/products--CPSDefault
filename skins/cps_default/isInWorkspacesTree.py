##parameters=object=None
##title=Is in a workspace
#$Id$
"""
Return True if the context or the parameter 'object' is in the workspaces tree,
as opposed to the sections tree.
"""

if not object:
    object = context

portal = object.portal_url.getPortalObject()
portal_path = portal.getPhysicalPath()
object_path = object.getPhysicalPath()
relative_path = object_path[len(portal_path):]
return relative_path and relative_path[0] == 'workspaces'
