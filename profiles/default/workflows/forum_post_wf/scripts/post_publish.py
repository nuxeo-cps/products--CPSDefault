## Script (Python) "post_publish"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state_change
##title=
##
object = state_change.object
forum = object.aq_inner.aq_parent
forum.getContent().postPublished(object.id, proxy=forum)
