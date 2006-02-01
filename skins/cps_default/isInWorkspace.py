##parameters=object=None
##title=Is in a workspace
#$Id$
"""
Return True if the context or the parameter 'object' is a workspace
or inside a workspace.
"""

ws = ['Workspace', 'Members Workspace']
if not object:
    object = context

try:
    return object.portal_type in ws \
        or object.aq_parent.portal_type in ws
except AttributeError:
    # FIXME: determine in which case it happens and how to react with the
    # portal's root
    return None
