## Script (Python) "give_attendee_manager"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state_change
##title=
##
context = state_change.object 
from Products.CMFCore.utils import getToolByName       
mtool = getToolByName(context, 'portal_membership')
user_id = mtool.getAuthenticatedMember().getUser().getId()
mtool.setLocalRoles(context, [user_id],
                        'AttendeeManager', reindex=1)
