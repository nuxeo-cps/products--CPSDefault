##parameters=permission
# $Id$
"""Require the user to have the given permission, otherwise an Unauthorized
exception is raised."""

if not context.portal_membership.checkPermission(permission, context):
    raise 'Unauthorized'
