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

from zLOG import LOG, INFO, DEBUG, WARNING, ERROR

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
        {'id': 'email_field', 'type': 'string', 'mode': 'w',
         'label': 'Members directory email field'},
        {'id': 'enable_password_reset', 'type': 'boolean',
         'label': 'Password reset enabled', 'mode': 'w'},
        {'id': 'reset_password_request_validity', 'type': 'int', 'mode': 'w',
         'label': 'Password reset request validity (seconds)'},
        {'id': 'enable_password_reminder', 'type': 'boolean',
         'label': 'Enable sending password reminder', 'mode': 'w'},
        )

    email_field = 'email'
    enable_password_reset = True
    reset_password_request_validity = 30*60 # 30 min
    enable_password_reminder = False

    # defaults overloaded from base class
    membersfolder_id = 'members'
    memberfolder_portal_type = 'Workspace'
    memberfolder_roles = ('Owner', 'WorkspaceManager')

    security = ClassSecurityInfo()

    #
    # Members password handling
    #

    security.declarePublic( 'mailPassword' )
    def mailPassword(self, who, REQUEST=None):
        """Email a forgotten password to a member.

        o Raise an exception if user ID is not found.
        """
        if not self.enable_password_reminder:
            raise Unauthorized('Password reminder disabled')

        usernames, email = self._getUsernamesAndEmailFor(who)
        LOG(log_key, DEBUG, "usernames=%r, email=%r" % (usernames, email))

        if email is None or not usernames:
            raise ValueError('The username you entered could not be found.')

        members = [{'login': id,
                    'password':self.getMemberById(id).getPassword()}
                   for id in usernames]

        # Rather than have the template try to use the mailhost, we will
        # render the message ourselves and send it from here (where we
        # don't need to worry about 'UseMailHost' permissions).
        mail_text = self.mail_password_template(self, REQUEST,
                                                email=email,
                                                members=members)

        host = self.MailHost
        host.send(mail_text)

        return self.mail_password_response(self, REQUEST)


    security.declarePublic('requestPasswordReset')
    def requestPasswordReset(self, who, REQUEST=None):
        """Generate a reset token for a password reset and send an email with
        the reset token for confirmation.

        This method can be called with a username or an email address.

        Returns True if a request has been sent.
        Returns False if the username or email cannot be found, or the
        mail cannot be sent.

        Note that the return value shouldn't condition what is displayed
        to a user, as it would leak information about what users exist.
        """
        if REQUEST is not None:
            raise Unauthorized("Not callable TTW")
        LOG(log_key, DEBUG, "Request reset for %r" % who)

        translation_service = getToolByName(self, 'translation_service', None)
        if translation_service is None:
            LOG(log_key, ERROR,
                "translation_service tool not found, could not proceed.")

        portal = getToolByName(self, 'portal_url').getPortalObject()

        portal_encoding = 'ISO-8859-15'
        mail_from_address = portal.getProperty('email_from_address')
        if mail_from_address is None:
            LOG(log_key, WARNING,
                "The portal has no 'email_from_address' defined. "
                "Password reset will not be performed because the users "
                "have to trust who sends them the reset email.")
            return False
        portal_url = portal.absolute_url()

        # XXX: Here we should setup a mean to prevent potential spam.
        # For example all requests should be stored in a dictionary (to
        # assert their uniqueness) and only be processed every hour so
        # if someone is spammed she will received only 12 password reset
        # confirmation messages a day.

        usernames, email = self._getUsernamesAndEmailFor(who)
        LOG(log_key, DEBUG, "usernames=%r, email=%r" % (usernames, email))
        if email is None:
            return False

        client_address = self.REQUEST.getClientAddr()
        var_mappings = {'portal_url': portal_url,
                        'email': email,
                        }
        # The translation is done using the language currently selected by the
        # user on the portal.
        subject = translation_service.translateDefault(
            'email_password_reset_confirmation_subject',
            mapping=var_mappings).encode(portal_encoding)
        now = str(int(time()))
        args = {
            'w': who,
            'd': now,
            't': self._makeToken(who, now),
            }
        visit_url = ('%s/account_reset_password_form?%s'
                     % (portal_url, urlencode(args)))
        var_mappings = {'mail_from_address': mail_from_address,
                        'email': email,
                        'subject': subject,
                        'visit_url': visit_url,
                        'portal_url': portal_url,
                        'client_address': client_address,
                        }
        # The translation is done using the language currently selected by the
        # user on the portal.
        body = translation_service.translateDefault(
            'email_password_reset_confirmation_body',
            mapping=var_mappings).encode(portal_encoding)
        try:
            self.MailHost.send(body,
                               mfrom=mail_from_address,
                               mto=email,
                               subject=subject,
                               encode='8bit')
        except (socket.error, SMTPException, MailHostError), e:
            LOG(log_key, WARNING, "Error while sending reset email "
                "for %s (%s %s)" % (who, e.__class__.__name__,
                                    str(e)))
            return False
        LOG(log_key, INFO, "Reset confirmation email sent to %s, "
            "requesting IP was %s" % (email, client_address))
        return True

    security.declarePrivate('_makeToken')
    def _makeToken(self, who, time):
        """Make a cryptographic token.
        """
        hash = sha.new()
        hash.update(self.getNonce())
        hash.update(who)
        hash.update(time)
        return hash.hexdigest()

    security.declarePublic('isPasswordResetRequestValid')
    def isPasswordResetRequestValid(self, who, time_, token, REQUEST=None):
        """Return whether a request for a password reset is valid or not.
        """
        if REQUEST is not None:
            raise Unauthorized("Not callable TTW")
        result = self._makeToken(who, time_)
        ok = (token == result
              and int(time_)
                  + self.getProperty('reset_password_request_validity')
              >= int(time()))
        if not ok:
            LOG(log_key, WARNING, "Invalid password reset request for %r"
                % who)
        return ok

    security.declarePublic('getUsernamesAndEmailFor')
    def getUsernamesAndEmailFor(self, who, time, token, REQUEST=None):
        """Return all the usernames, ie the accounts, that corresponds to the
        given username or email address.

        This method ensures that a user can only do such a request on from her
        email.
        """
        if REQUEST is not None:
            raise Unauthorized("Not callable TTW")
        if not self.isPasswordResetRequestValid(who, time, token):
            return ([], None)
        usernames, email = self._getUsernamesAndEmailFor(who)
        if not usernames:
            LOG(log_key, INFO, "No usernames for %r" % who)
        return (usernames, email)

    def _getUsernamesAndEmailFor(self, who):
        member = self.getMemberById(who)
        if member is not None:
            usernames = [who]
            email = member.getProperty(self.email_field)
        elif '@' in who:
            email = who
            usernames = self._getUsernamesFromEmail(email)
        else:
            usernames = email = None
        if not usernames or not email:
            return ([], None)
        return (usernames, email)

    def _getUsernamesFromEmail(self, email):
        dir = getToolByName(self, 'portal_directories').members
        return dir._searchEntries(**{self.email_field: [email]})

    # XXX shouldn't be public at all
    security.declarePublic('getEmailFromUsername')
    def getEmailFromUsername(self, username, REQUEST=None):
        """Looks up an email address via the members directory"""
        if REQUEST is not None:
            raise Unauthorized("Not callable TTW")
        members = getToolByName(self, 'portal_directories', None).members
        try:
            member = members._getEntry(username, default=None)
        except KeyError:
            return None
        if member:
            return member.get(self.email_field)
        return None

    security.declarePublic('getFullnameFromId')
    def getFullnameFromId(self, user_id, REQUEST=None):
        """Return the member full name from id
        """
        if REQUEST is not None:
            raise Unauthorized("Not callable TTW")
        try:
            utool = getToolByName(self, 'portal_url')
            portal = utool.getPortalObject()
            dir = portal.portal_directories.members
            fullname = dir._getEntry(user_id)[dir.title_field]
        except (AttributeError, KeyError):
            fullname = user_id
        return fullname

    security.declarePublic('resetPassword')
    def resetPassword(self, usernames, who, time, token, REQUEST=None):
        """Reset the password of the users having the given usernames.

        Usually this script is called with only one username but resetPassword
        works for many users as well.

        This methods returns the new randomly generated password,
        or None if there was a problem.
        """
        if REQUEST is not None:
            raise Unauthorized("Not callable TTW")
        if not self.enable_password_reset:
            raise Unauthorized("Password reset disabled")
        if not usernames:
            return None
        ok_usernames, email = self.getUsernamesAndEmailFor(who, time, token)
        for username in usernames:
            if username not in ok_usernames:
                # Attempt to hack the usernames field
                LOG(log_key, WARNING, "resetPassword: attempted to use %r "
                    "for %r" % (usernames, who))
                return None

        LOG(log_key, INFO, "Resetting password for %r" % (usernames,))
        random.seed()
        password = generatePassword()
        for username in usernames:
            member = self.getMemberById(username)
            if member is None:
                LOG(log_key, ERROR, "resetPassword: user %r not found"
                    % username)
                continue
            user = member.getUser()
            aclu = getToolByName(self, 'acl_users')
            roles = [r for r in user.getRoles()
                     if r not in ['Anonymous', 'Authenticated']]
            aclu._doChangeUser(username, password,
                               roles, user.getDomains())
        return password

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
        ptype_role_prefix = {'Section': ('Section', 'Contributor'),
                             'Workspace': ('Workspace', 'Contributor'),
                             'Members Workspace': ('Workspace', 'Contributor'),
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
