##parameters=
# $Id$
"""Get the list of renameable objects from REQUEST's 'ids' list.
"""

# This is bad but we want to keep CMF 1.4's API for now
REQUEST = context.REQUEST

ids = REQUEST.get('ids', [])

objects = []
for id in ids:
    if getattr(context.aq_explicit, id, None) is None:
        continue
    ob = getattr(context, id)
    if not ob.cb_isMoveable():
        continue
    objects.append(ob)

return objects
