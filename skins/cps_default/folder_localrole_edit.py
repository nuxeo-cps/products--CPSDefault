##parameters=change_type, member_ids=[], member_role='', lr_block=None, lr_unblock=None, REQUEST=None
# $Id$

pmtool = context.portal_membership
ids = member_ids
member = pmtool.getAuthenticatedMember()
member_id = member.getUserName()

group_ids = [group[len('group:'):] 
             for group in ids if group.startswith('group:') ]
member_ids = [user[len('user:'):] 
              for user in ids if user.startswith('user:') ]

if change_type == 'add':
    pmtool.setLocalRoles(context, member_ids, member_role, reindex=0)
    pmtool.setLocalGroupRoles(context, group_ids, member_role, reindex=0)
    context.reindexObjectSecurity()

elif change_type == 'delete':
    pmtool.deleteLocalRoles(context, member_ids, reindex=0)
    pmtool.deleteLocalGroupRoles(context, group_ids, reindex=0)
    context.reindexObjectSecurity()

elif change_type == 'block':
    if lr_block is not None:
        # For security, before blocking everything, we readd the current user
        # as a XyzManager of the current workspace/section.
        for r in pmtool.getCPSCandidateLocalRoles(context):
            if r == 'Manager':
                continue
            if not r.endswith('Manager'):
                continue
            if not member.has_role(r, context):
                continue
            from zLOG import LOG, DEBUG
            pmtool.setLocalRoles(context, (member_id,), r, reindex=0)
        # Block.
        pmtool.setLocalGroupRoles(context, ('role:Anonymous',), '-',
                                  reindex=0)
    elif lr_unblock is not None:
        pmtool.deleteLocalGroupRoles(context, ('role:Anonymous',), '-',
                                     reindex=0)
    context.reindexObjectSecurity()


psm = 'psm_local_roles_changed'

if REQUEST is not None:
    REQUEST.RESPONSE.redirect(
        '%s/folder_localrole_form?portal_status_message=%s' %
        (context.absolute_url(), psm))

