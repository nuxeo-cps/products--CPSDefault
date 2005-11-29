##parameters=sort_by=None, direction=None, hide_folder=False, displayed=None, use_catalog=None
# $Id$
"""
Get a sorted list of contents object
"""

if not sort_by:
    # Get sort from the session display params
    disp_params = context.REQUEST.SESSION.get('cps_display_params', {})
    sort_by = disp_params.get('sort_by')
    direction = disp_params.get('direction')

if use_catalog is None:
    # check container configuration with acquisition
    use_catalog = getattr(context, 'use_catalog_for_folder_contents', False)

if not use_catalog:
    # Fetch contents with an context.objectValues()
    from Products.CPSDefault.utils import getFolderContents
else:
    # Use the catalog to get the folder contents
    from Products.CPSDefault.utils import getCatalogFolderContents as getFolderContents
    if sort_by is None:
        sort_by = 'position_in_container'

return getFolderContents(context, sort_on=sort_by,
                         sort_order=direction,
                         hide_folder=hide_folder,
                         filter_ptypes=displayed)
