##parameters=username, password, password_confirmation, REQUEST

from Products.CMFCore.utils import getToolByName

# context.portal_membership
membership_tool = getToolByName(context, 'portal_membership')
member = membership_tool.getMemberById(username)
member.setSecurityProfile(password=password, domains=None)
membership_tool.deletePasswordResetRequest(username)
