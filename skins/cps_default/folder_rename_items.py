##parameters=
# $Id$
"""
Get the list of renameable objects from REQUEST's 'ids' list.
"""

# This is bad but we want to keep CMF 1.4's API for now
REQUEST = context.REQUEST

ids = REQUEST.get('ids', [])

objects = []
for id in ids:
    ob = getattr(context.aq_inner.aq_explicit, id, None)
    if ob is None:
        continue
    if not ob.cb_isMoveable():
        continue
    objects.append(ob)

return objects
