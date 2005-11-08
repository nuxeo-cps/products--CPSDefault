# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
# Florent Guillaume <fg@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

from zLOG import LOG, INFO, DEBUG, PROBLEM, ERROR

import sys
import socket
import random
import sha

from urllib import urlencode
from time import time
from smtplib import SMTPException

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized

from Products.MailHost.MailHost import MailHostError
from Products.CMFCore.utils import getToolByName
from Products.CPSCore.CPSMembershipTool import CPSMembershipTool
from Products.CPSUtil.id import generatePassword

log_key = 'CPSDefault.MembershipTool'

class MembershipTool(CPSMembershipTool):
    """A MembershipTool with additional functionnalities over
    the CPSCore MembershipTool.
    """
    meta_type = 'CPS Membership Tool'

    _properties = CPSMembershipTool._properties + (
        {'id': 'reset_password_request_validity', 'type': 'int', 'mode': 'w',
         'label': 'Number of seconds a reset password request is considered valid'},
        {'id': 'email_field', 'type': 'string', 'mode': 'w',
         'label': 'Field for email address'},
        )

    reset_password_request_validity = 3600 * 12
    email_field = 'email'

    security = ClassSecurityInfo()

    #
    # Members password handling
    #

    security.declarePublic('requestPasswordReset')
    def requestPasswordReset(self, username_or_email):
        """Generate a reset token for a password reset and send an email with
        the reset token for confirmation.

        This method can be called with both a username or an email address.
        """
        LOG(log_key, DEBUG, "username_or_email = %s" % username_or_email)
        # XXX: Here we should setup a mean to prevent potential spam.
        # For example all requests should be stored in a dictionary (to assert
        # their uniqueness) and only be processed every hour so if someone is
        # spammed she will received only 12 password reset confirmation messages
        # a day.
        username = None
        email = None
        member = self.getMemberById(username_or_email)
        if member is not None:
            LOG(log_key, DEBUG, "member is not None")
            username = username_or_email
            email = member.getProperty(self.email_field)
        elif username_or_email.find('@'):
            LOG(log_key, DEBUG, "username_or_email is an email")
            members_directory = self.portal_directories.members
            # Here we use the _searchEntries() method instead of the
            # searchEntries() method that only returns entries the current user
            # is allowed to consult.
            user_ids = members_directory._searchEntries(
                **{self.email_field: [username_or_email]})
            LOG(log_key, DEBUG, "user_ids %s" % user_ids)
            if user_ids != []:
                email = username_or_email
        LOG(log_key, DEBUG, "username = %s" % username)
        LOG(log_key, DEBUG, "email = %s" % email)
        if username is None and email is None:
            raise ValueError("The user you have specified cannot be found.")

        # Generating a token based either on the email address
        request_emission_time = str(int(time()))
        hash_object = sha.new()
        hash_object.update(email)
        hash_object.update(request_emission_time)
        hash_object.update(self.getNonce())
        reset_token = hash_object.hexdigest()

        try:
            mail_from_address = getattr(self.portal_properties,
                                        'email_from_address')
        except (AttributeError):
            LOG(log_key, PROBLEM,
                "Your portal has no \"email_from_address\" defined. \
                Reseting password will not be performed because the users have \
                to trust who send them this reset password email.")
        mail_to_address = email
        subject = ("[%s] Password reset confirmation for %s"
                   % (self.portal_url(), email))
        # d:  the date of the request emission
        # t:  the token
        args = {'email': email, 'd': request_emission_time, 't': reset_token}
        if username is not None:
            args.update({'username': username})
        visit_url = ("%s/account_reset_password_form?%s"
                     % (self.portal_url(), urlencode(args)))
        # TODO: i18n
        content = """\
From: %s
To: %s
Subject: %s
Content-Type: text/plain; charset=iso-8859-15
Mime-Version: 1.0
%s
"""
        content = content % (
            mail_from_address, mail_to_address, subject,
            """\
Dear user,

You (or someone) have requested to reset the password for the account(s) having
%s as email address. Most probably the reason for this reset request is that the
password for this/those account(s) has been lost.

If you have not requested this reset, please do ignore this message.

You can reset your password by simply visiting the following page:
%s

Thank you, and we look forward to seeing you back at %s soon!

Sincerely,

--
The %s administration team
"""
            % (email, visit_url, self.portal_url(), self.portal_url()))
        try:
            self.MailHost.send(content,
                               mto=mail_to_address, mfrom=mail_from_address,
                               subject=subject, encode='8bit')
        except (socket.error, SMTPException, MailHostError):
            LOG(log_key, PROBLEM,
                "Error while sending reset token email")
        result = {'reset_token': reset_token,
                  'emission_time': request_emission_time,
            }
        return result


    security.declarePublic('isPasswordResetRequestValid')
    def isPasswordResetRequestValid(self, email, emission_time, reset_token):
        """Return wether a request for a password reset is valid or not."""
        hash_object = sha.new()
        hash_object.update(email)
        hash_object.update(emission_time)
        hash_object.update(self.getNonce())
        result = hash_object.hexdigest()
        if (reset_token == result
            and int(emission_time)
            + self.getProperty('reset_password_request_validity')
            >= int(time())):
            return True
        return False


    security.declarePublic('getUsernamesFromEmail')
    def getUsernamesFromEmail(self, email, emission_time, reset_token):
        """Return all the usernames, ie the accounts, that corresponds to the
        given email address.

        This method ensures that a user can only do such a request on from her
        email.
        """
        if not self.isPasswordResetRequestValid(email,
                                                emission_time, reset_token):
            LOG(log_key, INFO, "Method getUsernamesFromEmail is used with a "
                "wrong email address (the one of the reset token).")

        members_directory = self.portal_directories.members
        # Here we use the _searchEntries() method instead of the
        # searchEntries() method that only returns entries the current user
        # is allowed to consult.
        user_ids = members_directory._searchEntries(**{self.email_field: [email]})
        return user_ids

    security.declarePublic('getEmailFromUsername')
    def getEmailFromUsername(self, username):
        """Looks up an email address via the members directory"""
        members = getToolByName(self, 'portal_directories', None).members
        try:
            member = members._getEntry(username, default=None)
        except KeyError:
            return None
        if member:
            return member.get(self.email_field)
        return None

    security.declarePublic('getFullNameFromId')
    def getFullnameFromId(self, user_id, REQUEST=None):
        """Return the member full name from id
        """

        # We don't wanna user to be able to call this from restricted
        # code
        if REQUEST is not None:
            raise Unauthorized(
                "You cannot call this method from restricted code")
        try:
            utool = getToolByName(self, 'portal_url')
            portal = utool.getPortalObject()
            dir = portal.portal_directories.members
            fullname = dir._getEntry(user_id)[dir.title_field]
        except (AttributeError, KeyError):
            fullname = user_id
        return fullname

    security.declarePublic('resetPassword')
    def resetPassword(self, usernames, email, emission_time, reset_token):
        """Reset the password of the users having the given usernames.

        The users must all have the same email address.
        Usually this script is called with only one username but resetPassword
        works for many users as well.

        This methods returns a dictionary containing
        1. the new randomly generated password
        2. a boolean telling if the password resetting has been successful
        """
        result = {'new_password': None,
                  'reset_password_success': True,
                  }
        if not self.isPasswordResetRequestValid(email,
                                                emission_time, reset_token):
            LOG(log_key, INFO,
                "An invalid password reset request has been received.")
            return result
        random.seed()
        new_password = generatePassword()
        for username in usernames:
            member = self.getMemberById(username)
            if member is None:
                LOG(log_key, PROBLEM, "The user %s cannot be found." % username)
                result['reset_password_success'] = False
            user = member.getUser()
            self.acl_users._doChangeUser(username, new_password,
                                         user.getRoles(), user.getDomains())
        result['new_password'] = new_password
        return result


    #
    # Member area creation
    #

    security.declarePrivate('_createMemberContentAsManager')
    def _createMemberContentAsManager(self, member, member_id, member_folder):
        """Create the content of the member area.

        Executed with Manager privileges.

        Additional actions done in CPSDefault:
        - create personal calendar
        """
        # inherited method
        CPSMembershipTool._createMemberContentAsManager(self, member,
                                                        member_id, member_folder)
        portal_cpscalendar = getToolByName(self, 'portal_cpscalendar', None)
        if portal_cpscalendar is not None:
            create_calendar = getattr(portal_cpscalendar, 'create_member_calendar', 1)
            if create_calendar:
                try:
                    portal_cpscalendar.createMemberCalendar(member_id)
                # If the Calendar portal types has been removed, we will
                # get a ValueError exception here.
                except ValueError:
                    pass

    security.declarePrivate('_notifyMemberAreaCreated')
    def _notifyMemberAreaCreated(self, member, member_id, member_folder):
        """Perform special actions after member content has been created

        Additional actions done in CPSDefault:
        - set the member area title using the user's title
        """
        # inherited method
        CPSMembershipTool._notifyMemberAreaCreated(self, member,
                                                   member_id, member_folder)
        # get the user's title
        members_directory = self.portal_directories.members
        member_entry = members_directory._getEntry(member_id, default=None)
        if member_entry is None:
            return
        member_title = member_entry.get(members_directory.title_field)
        if not member_title:
            member_title = member_id
        # set the member area title, assuming user can edit it
        doc = member_folder.getEditableContent()
        doc.setTitle(member_title)


    #
    # Miscellaneous helper methods
    #

    security.declarePrivate('getNonce')
    def getNonce(self):
        """The nonce is a random string different for each instance of
        CPSMembershipTool that is used to generate unique hash values.

        If ZEO is used, each server will have the same nonce.
        """
        try:
            # Here we use a variable instance so that each ZEO server will have
            # the same nonce.
            nonce = self._nonce
        except AttributeError:
            self._nonce = ''.join(random.sample('.:;_-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                                                  random.randint(10, 15)))
            nonce = self._nonce
        return nonce

    #
    # Local roles management utilities
    #

    # XXX This has to be made more flexible using registries
    security.declarePublic('getCPSCandidateLocalRoles')
    def getCPSCandidateLocalRoles(self, obj):
        """ Get relevant local roles according to the context.

        Roles are already filtered using the base method  getCPSCandidateLocalRoles
        method, now filter them according to the context.
        """
        # List local roles according to the context
        cps_roles = CPSMembershipTool.getCPSCandidateLocalRoles(self, obj)
        cps_roles.reverse()

        # XXX a better way of doing is that is necessarly
        # Filter them for CPS
        cps_roles = [x for x in cps_roles if x not in ('Owner', 'Member',
                                                       'Reviewer', 'Manager',
                                                       'Authenticated')]
        # filter roles by portal type using prefix
        # XXX TODO relevant roles should be store in the portal_types tool
        ptype_role_prefix = {'Section': ('Section',),
                             'Workspace': ('Workspace'),
                             'Wiki': ('Contributor', 'Reader'),
                             'Calendar': ('Workspace',),
                             'CPSForum': ('Forum',),
                             'Chat': ('Chat',),
                             'CPS Calendar': ('Attendee',),
                             'Blog': ('BlogManager', 'BlogPoster'),
                             }
        ptype = obj.portal_type
        if ptype in ptype_role_prefix.keys():
            contextual_roles = []
            for role_prefix in ptype_role_prefix[ptype]:
                for cps_role in cps_roles:
                    if cps_role.startswith(role_prefix):
                        contextual_roles.append(cps_role)
            cps_roles = contextual_roles

        return cps_roles


    security.declarePublic('getCPSLocalRoles')
    def getCPSLocalRoles(self, obj, cps_roles=None):
        """Get local roles dictionnary filtered using relevant roles in
        context and tell if local roles are blocked using this dictionnary
        """
        dict_roles = self.getMergedLocalRolesWithPath(obj)
        local_roles_blocked = 0

        # get info about role blockings
        anon_infos = dict_roles.get('group:role:Anonymous')
        blocked_rpaths = []
        if anon_infos is not None:
            for role_info in anon_infos:
                if '-' in role_info['roles']:
                    rpath = role_info['url']
                    blocked_rpaths.append(rpath)

        blocked_rpath = ''
        if blocked_rpaths:
            # consider latest blocking
            blocked_rpaths.sort()
            blocked_rpath = blocked_rpaths[-1]
            # check if roles are blocked at current level
            url_tool = getToolByName(self, 'portal_url')
            local_rpath = url_tool.getRpath(obj)
            if blocked_rpath == local_rpath:
                local_roles_blocked = 1

        # filter blocked roles and roles not relevant in context
        if cps_roles is None:
            cps_roles = self.getCPSCandidateLocalRoles(obj)
        for item, role_infos in dict_roles.items():
            for role_info in role_infos:
                if blocked_rpath:
                    rpath = role_info['url']
                    # skip roles set STRICTLY above blocking ; roles set at the
                    # blocking_rpath level have to be kept
                    if rpath.find(blocked_rpath) == -1:
                        role_info['roles'] = []
                        continue
                roles = role_info['roles']
                role_info['roles'] = [r for r in roles if r in cps_roles]

            # delete role info if no roles are left
            dict_roles[item] = [x for x in dict_roles[item] if x['roles']]

            # delete items that do not have any role to display
            if not dict_roles[item]:
                del dict_roles[item]

        return dict_roles, local_roles_blocked


    security.declarePublic('getCPSLocalRolesRender')
    def getCPSLocalRolesRender(self, obj, cps_roles, filtered_role=None):
        """Get dictionnaries that will be used by the template presenting local
        roles.

        Return 2 lists and 2 dictionnaries: sorted members, members dictionnary
        with member ids as keys and a dictionnary describing their roles as
        values, and the same for groups.

        Also return information about local roles blocking.

        If filtered_role is set to one of the relevant local roles, only
        display users with given role (inherited or not), and their other roles
        if they have some.
        """
        # XXX need to be broken in sub methods

        # directories, used for users/groups rendering
        dirtool = getToolByName(self, 'portal_directories')
        mdir = dirtool.members
        mdir_title_field = mdir.title_field
        gdir = dirtool.groups
        gdir_title_field = gdir.title_field
        dict_roles, local_roles_blocked = self.getCPSLocalRoles(obj, cps_roles)
        utool = getToolByName(self, 'portal_url')
        rpath = utool.getRpath(obj)

        # fill members and groups dictionnaries
        members = {}
        groups = {}
        for item, role_infos in dict_roles.items():
            # fill info about each role for given item
            here_roles = {}
            inherited_roles = {}
            has_roles = 0
            has_local_roles = 0
            # default info for each role to be presented
            for role in cps_roles:
                here_roles[role] = {
                    'here': 0,
                    'inherited': 0,
                    }
            for role_info in role_infos:
                role_url = role_info['url']
                if role_url == rpath:
                    here = 1
                else:
                    here = 0
                # maybe skip inherited blocked roles
                if here or not local_roles_blocked:
                    for role in role_info['roles']:
                        # take filtering on roles into account
                        if not filtered_role or role == filtered_role:
                            has_roles = 1
                        # fill info even if role is filtered
                        if here:
                            here_roles[role]['here'] = 1
                            has_local_roles = 1
                        else:
                            here_roles[role]['inherited'] = 1
                            if inherited_roles.get(role) is None:
                                inherited_roles[role] = [role_url]
                            else:
                                inherited_roles[role].append(role_url)
            # skip if all roles have been filtered
            if not has_roles:
                continue
            # fill members and groups rendering info (title, input name) + computed
            # roles info
            if item.startswith('user:'):
                member_id = item[len('user:'):]
                member_title = ''
                entry = mdir.getEntry(member_id, None)
                if entry is not None:
                    member_title = entry.get(mdir_title_field)
                members[item] = {
                    'title': member_title or member_id,
                    'role_input_name': 'role_user_' + member_id,
                    'here_roles': here_roles,
                    'inherited_roles': inherited_roles,
                    'has_local_roles': has_local_roles,
                    }
            elif item.startswith('group:'):
                group_id = item[len('group:'):]
                group_title = ''
                entry = gdir.getEntry(group_id, None)
                if entry is not None:
                    group_title = entry.get(gdir_title_field)
                groups[item] = {
                    'title': group_title or group_id,
                    # XXX AT: no ':' accepted, change it for role:Anonymous and
                    # role:Authenticated groups
                    'role_input_name': 'role_group_' + group_id.replace(':', '_'),
                    'here_roles': here_roles,
                    'inherited_roles': inherited_roles,
                    'has_local_roles': has_local_roles,
                    }

        # sort members and groups on title
        sort = [(v.get(mdir_title_field), k) for k, v in members.items()]
        sort.sort()
        sorted_members = [x[1] for x in sort]
        sort = [(v.get(gdir_title_field), k) for k, v in groups.items()]
        sort.sort()
        sorted_groups = [x[1] for x in sort]
        return sorted_members, members, sorted_groups, groups, local_roles_blocked


    security.declarePublic('blockLocalRoles')
    def blockLocalRoles(self, obj):
        """Block local roles acquisition on given object

        Acquisition blocking is made adding the '-' role to the group of
        anonymous users.
        """
        member = self.getAuthenticatedMember()
        if not member.has_role('Manager'):
            # Prevent user from losing local roles management rights: readd the
            # current user as a XyzManager of the current workspace/section
            # before blocking.
            member_id = member.getUserName()
            candidate_roles = self.getCPSCandidateLocalRoles(obj)
            local_manager_roles = [x for x in candidate_roles
                                   if x in self.roles_managing_local_roles
                                   and x != 'Manager']
            for r in local_manager_roles:
                self.setLocalRoles(obj, (member_id,), r, reindex=0)
        # Block and reindex
        self.setLocalGroupRoles(obj, ('role:Anonymous',), '-')


    security.declarePublic('unblockLocalRoles')
    def unblockLocalRoles(self, obj):
        """Block local roles acquisition on given object

        Acquisition blocking is made deleting the '-' role to the group of
        anonymous users.
        """
        self.deleteLocalGroupRoles(obj, ('role:Anonymous',), '-')


InitializeClass(MembershipTool)


def addMembershipTool(dispatcher, **kw):
    """Add a membership tool"""
    mt = MembershipTool(**kw)
    id = mt.getId()
    container = dispatcher.Destination()
    container._setObject(id, mt)
    mt = container._getOb(id)
