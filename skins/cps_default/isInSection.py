##parameters=object=None
#$Id$
"""Return True if the context or the parameter 'object' is in a Section
or is a Section itselft.
"""

types = ['Section']
if not object:
    object = context

return object.portal_type in types or object.aq_parent.portal_type in types
