## Script (Python) "folder_localrole_edit"
##parameters=change_type
##title=Set local roles
##
pm = context.portal_membership
ids = context.REQUEST.get('member_ids', ())


group_ids = [group[len('group:'):] for group in ids if group.startswith('group:') ]
member_ids = [user[len('user:'):] for user in ids if user.startswith('user:') ]

member_role = context.REQUEST.get('member_role', '')


if change_type == 'add':
    pm.setLocalRoles( obj=context
                    , member_ids=member_ids
                    , member_role=member_role
                    )
    pm.setLocalGroupRoles( context, group_ids, member_role)

else:
    pm.deleteLocalRoles( obj=context
                       , member_ids=member_ids
                       )
    pm.deleteLocalGroupRoles(context, group_ids)

psm='psm_local_roles_changed'

context.REQUEST.RESPONSE.redirect(
    '%s/folder_localrole_form?portal_status_message=%s' %
    (context.absolute_url(), psm))

