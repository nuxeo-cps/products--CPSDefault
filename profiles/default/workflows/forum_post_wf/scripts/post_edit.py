## Script (Python) "post_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state_change
##title=
##
object = state_change.object
subject = state_change.kwargs.get('subject', '')
author = state_change.kwargs.get('author', '')
msg = state_change.kwargs.get('message', '')
pid = state_change.kwargs.get('parent_id', '')

kw = {'Title': subject,
      'Description': msg,
      'author': author,
      'parent_id': pid,
      'proxy': object}

object.getEditableContent().edit(**kw)
