##parameters=RESPONSE
# $Id$
"""
Override CMF's personalize_form that is not applicable and causes
problems.
"""

from Products.CMFCore.utils import getToolByName
from urllib import urlencode

utool = getToolByName(context, 'portal_url')
mtool = getToolByName(context, 'portal_membership')

uid = mtool.getAuthenticatedMember().getId()

RESPONSE.redirect(utool()+'/cpsdirectory_entry_view?'
                  +urlencode({'dirname': 'members',
                              'id': uid}))
