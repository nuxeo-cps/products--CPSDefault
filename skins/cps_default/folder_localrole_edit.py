##parameters=change_type, member_ids=[], member_role='', REQUEST=None
# $Id$

pmtool = context.portal_membership
ids = member_ids

group_ids = [group[len('group:'):] 
             for group in ids if group.startswith('group:') ]
member_ids = [user[len('user:'):] 
              for user in ids if user.startswith('user:') ]

if change_type == 'add':
    pmtool.setLocalRoles(context, member_ids, member_role)
    pmtool.setLocalGroupRoles(context, group_ids, member_role)

else:
    pmtool.deleteLocalRoles(context, member_ids)
    pmtool.deleteLocalGroupRoles(context, group_ids, member_role)

psm = 'psm_local_roles_changed'

if REQUEST is not None:
    REQUEST.RESPONSE.redirect(
        '%s/folder_localrole_form?portal_status_message=%s' %
        (context.absolute_url(), psm))

