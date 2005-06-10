##parameters=REQUEST=None
# $Id$
"""
FIXME: add docstring
"""

# Note: there is another solution that does not rely on HTTP_REFERER:
# have the add_favorites action generate a url with the object to bookmark
# as a parameter to the addtoFavorite script:
# python:portal.portal_url() + '/addtoFavorites?link=' +
# request.URL+'&object=' + object.absolute_url()
# link and object are passed to this script and can be used respectively
# to generate the bookmark URL and to retrieve the object (in order to get
# its title and description).

# TODO: check that link doesn't exist already.

from ZTUtils import make_query

portal = context.portal_url.getPortalObject()
homeFolder = portal.portal_membership.getHomeFolder()

favorites_id = 'Favorites'

if favorites_id not in homeFolder.objectIds():
    # try to i18n the title using UI locale,
    # still better than just an english id
    cpsmcat = context.translation_service
    title = cpsmcat('action_view_favorites').encode('iso-8859-15', 'ignore')
    homeFolder.invokeFactory('Workspace', favorites_id)
    targetFolder = getattr(homeFolder, favorites_id)
    targetFolder.getEditableContent().edit(Title=title)
    context.portal_eventservice.notifyEvent('modify_object', targetFolder, {})

targetFolder = getattr(homeFolder, favorites_id)

new_id = 'fav_' + str(int(context.ZopeTime()))

targetFolder.invokeFactory('Link', new_id)

referer = REQUEST.HTTP_REFERER
portal_URL_length = len(portal.portal_url())

# Fallback in case HTTP_REFERER is empty.
# Note: if referer is empty (or incorrect), the bookmark
# might be incorrect - the above-mentioned method fixes this
# but has not been retained because of its lower performace.
if referer and len(referer) >= portal_URL_length:
    referer_url = portal.portal_url.getPortalPath() + \
        REQUEST.HTTP_REFERER[portal_URL_length:]
else:
    referer_url = portal.portal_url.getPortalPath() + '/' + \
        context.portal_url.getRelativeUrl(context)

kw = {'Title': context.TitleOrId(),
      'Description': context.getContent().description,
      'Relation': referer_url}

doc = getattr(targetFolder, new_id).getEditableContent()

doc.edit(**kw)

if REQUEST is not None:
    if referer_url.count('portal_status_message'):
        query = ''
    else:
        query = make_query(portal_status_message='psm_added_to_favorites')
    if '?' in referer_url:
        url = REQUEST.HTTP_SERVER + referer_url + '&' + query
    else:
        url = REQUEST.HTTP_SERVER + referer_url + '?' + query
    return REQUEST.RESPONSE.redirect(url)

