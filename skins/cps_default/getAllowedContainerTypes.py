## Script (Python) "getAllowedContainerTypes"
##parameters=portal_type
#$Id$
"""
This script returns all portal_types in which
portal_type is authorized (None if no restriction)
"""

#'*' as an item in the sequence value associated with a portal_type
#means that this portal_type is authorized everywhere
#e.g. 'Image': ['*',]
allowed_content_types = {
    'FAQitem': ['FAQ',],
    'GlossaryItem': ['Glossary',],
    'Page': ['Book',],
    }

cactypes = context.getCustomAllowedContainerTypes()
allowed_content_types.update(cactypes)

#returning None means that there is no restriction on this portal_type
res = allowed_content_types.get(portal_type,None)
if res is None or len(res) == 0 or '*' in res:
    return None
else:
    return res
