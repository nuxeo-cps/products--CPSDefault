##parameters=REQUEST=None
# $Id$
"""Add a Link document in the favorites folder in homefolder, pointing towards
current document

Script checks that homefolder exists and that user can create content in it. If
the favorites folder does not exists, it is created in homefolder. Script
assumes that user can create content in its favorites folder.

The script could check if a link towards current document is already in the
favorites. This part of the code is commented out because it is costly.
"""

from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.utils import getToolByName

utool = getToolByName(context, 'portal_url')
mtool = getToolByName(context, 'portal_membership')

home_folder = mtool.getHomeFolder()

if (home_folder is None
    or not mtool.checkPermission(AddPortalContent, home_folder)):
    # cannot add favorites
    psm = 'psm_cannot_create_favorites'
else:
    favorites_id = 'Favorites'

    # create favorites folder if it does not exist
    if favorites_id not in home_folder.objectIds():
        # try to i18n the title using UI locale,
        # still better than just an english id
        cpsmcat = context.translation_service
        title = cpsmcat('action_view_favorites')
        title = title.encode('iso-8859-15', 'ignore')
        home_folder.invokeFactory('Workspace', favorites_id, Title=title)
        fav_folder = getattr(home_folder, favorites_id)

    fav_folder = getattr(home_folder, favorites_id)

    # XXX AT: This link will break if the portal name changes for instance...
    new_link = utool.getPortalPath() + '/' + utool.getRpath(context)

    # check that the link does not already exists
    link_exists = False
    # XXX AT: commented because it could be costly
    # Cannot query Relation as it is not indexed by default
    #for fav in fav_folder.objectValues():
    #    if getattr(fav, 'portal_type', None) == 'Link':
    #        try:
    #            fav_link = fav.getContent().Relation()
    #        except AttributeError:
    #            continue
    #        if fav_link == new_link:
    #            link_exists = True
    #            break

    if link_exists is True:
        psm = 'psm_already_in_favorites'
    else:
        # get info about the document to set the link info
        link_kws = {}
        link_kws['Relation'] = new_link
        doc = context.getContent()
        try:
            link_kws['Title'] = doc.title_or_id()
            link_kws['Description'] = doc.Description()
        except AttributeError:
            link_kws['Title'] = context.getId()

        new_id = 'fav_' + str(int(context.ZopeTime()))
        fav_folder.invokeFactory('Link', new_id, **link_kws)
        psm = 'psm_added_to_favorites'

if REQUEST is not None:
    url = context.absolute_url() + '?'
    url += 'portal_status_message=' + psm
    return REQUEST.RESPONSE.redirect(url)
