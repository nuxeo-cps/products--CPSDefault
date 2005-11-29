##parameters=direction, ids=[], use_catalog=None
# $Id$
"""Move selected objects to the direction."""

if same_type(ids, ''):
    ids = [ids]

if not ids:
    message = 'psm_select_at_least_one_document'
else:
    message = 'psm_item(s)_moved_' + direction
    if direction == "up":
        context.moveObjectsUp(ids)
    elif direction == "down":
        context.moveObjectsDown(ids)
    elif direction == "to_top":
        context.moveObjectsToTop(ids)
    elif direction == "to_bottom":
        context.moveObjectsToBottom(ids)
    else:
        message = 'invalid_direction'
    if use_catalog is None:
        # check container configuration with acquisition
        use_catalog = getattr(context, 'use_catalog_for_folder_contents',
                              False)
    if use_catalog:
        # folder contents is displayed using the catalog
        # we need to reindex the position_in_container index and metadata
        from Products.CPSDefault.utils import reindexFolderContentPositions
        reindexFolderContentPositions(context)

# Keeping the choosen ids while redisplaying the list
context.REQUEST.SESSION['choosen_ids'] = ids

context_url = context.REQUEST.get("context_url", context.getContextUrl())
ret_url = context_url + "folder_contents"

context.REQUEST.RESPONSE.redirect(
    ret_url + '?portal_status_message=%s' % message)
