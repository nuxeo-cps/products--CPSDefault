## Script (Python) "addtoFavorites"
##title=Add item to favourites
##parameters=
##$Id$

from zLOG import LOG,DEBUG

portal = context.portal_url.getPortalObject()
homeFolder = portal.portal_membership.getHomeFolder()

favorites_id = 'Favorites'

if favorites_id not in homeFolder.objectIds():
  portal.portal_workflow.invokeFactoryFor(homeFolder,'Workspace',favorites_id)
targetFolder = getattr(homeFolder, favorites_id)

new_id='fav_' + str(int(context.ZopeTime()))
myPath=context.portal_url.getRelativeUrl(context)

portal.portal_workflow.invokeFactoryFor(targetFolder,'Link',new_id)

doc = getattr(targetFolder,new_id).getEditableContent()

kw = {'title':context.TitleOrId(),
      'description':context.getContent().description,
      'href':context.portal_url.getPortalPath() + '/' + myPath}

doc.edit(**kw)

url = '%s/?portal_status_message=psm_added_to_favorites' % context.absolute_url()
return context.REQUEST.RESPONSE.redirect(url)
