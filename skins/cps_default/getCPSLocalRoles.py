## Script (Python) "getCPSLocalRoles.py"
##parameters=mtool=None, base_url=None, context_url=None
##
# $Id$
""" get Merged Local Roles filtering non CPS Roles. """

if mtool is None:
    mtool = context.portal_membership

if base_url is None: 
    base_url = context.getBaseUrl()

if context_url is None:
    context_url = context.getContextUrl()

# Get the list of Roles from the tool
dict_roles = mtool.getMergedLocalRoles(context, withpath=1)

# filter remove non CPS roles
for user in dict_roles.keys():
    for item in dict_roles[user]:
        item['roles'] = [x for x in item['roles'] if x not in ('Owner', 'Member')]
    dict_roles[user] = [x for x in dict_roles[user] if len(x['roles'])]

    if not len(dict_roles[user]):
        del dict_roles[user]

#find editable user with local roles defined in the context
editable_users = []
for user in dict_roles.keys():
    for item in dict_roles[user]:
        if base_url+item['url'] == context_url:
            editable_users.append(user)
            continue
    
return dict_roles, editable_users

