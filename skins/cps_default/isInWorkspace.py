##parameters=object=None
##title=Is in a workspace
#$Id$
"""
Return True if the context or the parameter 'object' is a workspace
or inside a workspace.

FIXME: method name doesn't match this docstring.
"""

if not object:
    object = context

try:
    return object.portal_type == 'Workspace' \
        or object.aq_parent.portal_type == 'Workspace'
except AttributeError:
    # FIXME: determine in which case it happens and how to react with the
    # portal's root
    return None
