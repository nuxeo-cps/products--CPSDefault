##parameters=object=None
##title=Is in a workspace
#$Id$

"""
Return a true value if the context is or is in a workspace.
"""

if not object:
    object = context

try:
    return object.portal_type == 'Workspace' or object.aq_parent.portal_type == 'Workspace'
except AttributeError:
    # XXX determine in which case it happens and how to react with the
    # portal's root
    return None
