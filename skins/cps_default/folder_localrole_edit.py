## Script (Python) "folder_localrole_edit"
##parameters=change_type
##title=Set local roles
##
pm = context.portal_membership
ids = context.REQUEST.get('member_ids', ())

groupids = [group for group in ids if group.startswith('role:') ]
member_ids = [ user for user in ids if not user.startswith('role:') ]


if change_type == 'add':
    pm.setLocalRoles( obj=context
                    , member_ids=member_ids
                    , member_role=context.REQUEST.get('member_role', '')
                    )
    for groupid in groupids:
        context.manage_addLocalGroupRoles(groupid=groupid, roles=[context.REQUEST.get('member_role'),])
        
else:
    pm.deleteLocalRoles( obj=context
                       , member_ids=member_ids
                       )
    context.manage_delLocalGroupRoles(groupids=groupids)
    
qst='?portal_status_message=Local+Roles+changed.'

context.REQUEST.RESPONSE.redirect( context.absolute_url() + '/folder_localrole_form' + qst )
