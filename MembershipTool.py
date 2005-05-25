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

import sys
import socket
import random
import sha

from urllib import urlencode
from time import time
from smtplib import SMTPException
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from zLOG import LOG, DEBUG, PROBLEM, ERROR

from Products.MailHost.MailHost import MailHostError
from Products.CMFCore.utils import getToolByName
from Products.CPSCore.CPSMembershipTool import CPSMembershipTool
from Products.CPSUtil.id import generatePassword
from zLOG import LOG, INFO, DEBUG, PROBLEM, ERROR

log_key = 'CPSDefault.MembershipTool'

class MembershipTool(CPSMembershipTool):
    """A MembershipTool with additional functionnalities over
    the CPSCore MembershipTool.
    """
    meta_type = 'CPS Membership Tool'

    _properties = (
        {'id': 'reset_password_request_validity', 'type': 'int', 'mode': 'w',
         'label': 'Number of seconds a reset password request is considered valid'},
        )
    reset_password_request_validity = 3600 * 12

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
            email = member.getProperty('email')
        elif username_or_email.find('@'):
            LOG(log_key, DEBUG, "username_or_email is an email")
            members_directory = self.portal_directories.members
            # Here we use the _searchEntries() method instead of the
            # searchEntries() method that only returns entries the current user
            # is allowed to consult.
            user_ids = members_directory._searchEntries(email=username_or_email)
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
        user_ids = members_directory._searchEntries(email=email)
        return user_ids


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
        if portal_cpscalendar:
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
        member_entry = members_directory.getEntry(member_id)
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

InitializeClass(MembershipTool)


def addMembershipTool(dispatcher, **kw):
    """Add a membership tool"""
    mt = MembershipTool(**kw)
    id = mt.getId()
    container = dispatcher.Destination()
    container._setObject(id, mt)
    mt = container._getOb(id)
