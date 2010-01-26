##parameters=sort_by=None, direction=None, hide_folder=False, displayed=None, use_catalog=None, hide_front_pages=False
# $Id: getFolderContents.py 30940 2005-12-22 20:41:54Z fguillaume $
"""
Get a sorted list of contents object
"""

from Products.CPSUtil.session import sessionGet

if not sort_by:
    # Get sort from the session display params
    disp_params = sessionGet(context.REQUEST, 'cps_display_params', {})
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

contents = getFolderContents(context, sort_on=sort_by,
           	             sort_order=direction,
                	     hide_folder=hide_folder,
                             filter_ptypes=displayed)

# yet another datamodel creation. Should cache this in request at some point

if context.portal_type == 'Portal':
    return contents

frontpage = context.getContent().getDataModel().get('frontpage')
if hide_front_pages and frontpage:
	return [proxy for proxy in contents if proxy.getId() != frontpage]

return contents
