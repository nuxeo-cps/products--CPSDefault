## Script (Python) "addtoFavorites"
##title=Add item to favorites
##parameters=REQUEST=None
# $Id$

#note: there is another solution that does not rely on HTTP_REFERER:
#have the add_favorites action generate a url with the object to bookmark
#as a parameter to the addtoFavorite script:
#python:portal.portal_url() + '/addtoFavorites?link=' +
#request.URL+'&object=' + object.absolute_url()
#link and object are passed to this script and can be used respectively
#to generate the bookmark URL and to retrieve the object (in order to get
#its title and description)

from ZTUtils import make_query

portal = context.portal_url.getPortalObject()
homeFolder = portal.portal_membership.getHomeFolder()

favorites_id = 'Favorites'

if favorites_id not in homeFolder.objectIds():
  homeFolder.invokeFactory('Workspace', favorites_id)
targetFolder = getattr(homeFolder, favorites_id)

new_id='fav_' + str(int(context.ZopeTime()))

targetFolder.invokeFactory('Link', new_id)

referer = REQUEST.HTTP_REFERER
portal_URL_length = len(portal.portal_url())

#fallback in case HTTP_REFERER is empty
#note: if referer is empty (or incorrect), the bookmark
#might be incorrect - the above-mentioned method fixes this
#but has not been retained because of its lower performace
if referer and len(referer) >= portal_URL_length:
  rurl = portal.portal_url.getPortalPath() + REQUEST.HTTP_REFERER[portal_URL_length:]
else:
  rurl = portal.portal_url.getPortalPath() + '/' + context.portal_url.getRelativeUrl(context)
  
kw = {'title': context.TitleOrId(),
      'description': context.getContent().description,
      'href': rurl}

doc = getattr(targetFolder, new_id).getEditableContent()

doc.edit(**kw)

if REQUEST:
  param_index = rurl.find("?")
  if param_index == -1:
    url = REQUEST.HTTP_SERVER + rurl + '?' +\
          make_query(portal_status_message='psm_added_to_favorites')
  else:    
    url = REQUEST.HTTP_SERVER + rurl + '&' +\
          make_query(portal_status_message='psm_added_to_favorites')
  return REQUEST.RESPONSE.redirect(url)


