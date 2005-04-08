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
#
# Replace MonkeyPatch of Membershiptool by real object use
#
# $Id$

import sys
import socket
import random
import sha
from time import time
from smtplib import SMTPException
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import nobody
from AccessControl.User import UnrestrictedUser
from AccessControl.Permissions import manage_users as ManageUsers
from Acquisition import aq_base, aq_parent, aq_inner

from Products.MailHost.MailHost import MailHostError
from Products.CMFCore.permissions import View, ManagePortal
from Products.CMFCore.permissions import ListPortalMembers
from Products.CMFCore.ActionsTool import ActionInformation as AI
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CPSCore.CPSMembershipTool import CPSMembershipTool
from Products.CPSUtil.id import generatePassword
from zLOG import LOG, INFO, DEBUG, PROBLEM, ERROR


class MembershipTool(CPSMembershipTool):
    """A MembershipTool with additional functionnalities over
    the CPSCore MembershipTool.
    """
    meta_type = 'CPS Membership Tool'

    # The number of seconds that a reset password request is considered valid
    reset_password_request_validity = 3600 * 12

    security = ClassSecurityInfo()


    security.declarePublic('requestPasswordReset')
    def requestPasswordReset(self, username):
        """Generate a reset token for a password reset and send an email with
        the reset token for confirmation.
        """
        # XXX: Here we should setup a mean to prevent potential spam.
        # For example all requests should be stored in a dictionary (to assert
        # their uniqueness) and only be processed every hour so if someone is
        # spammed she will received only 12 password reset confirmation messages
        # a day.
        member = self.getMemberById(username)
        if member is None:
            raise ValueError("The username cannot be found.")
        email_address = member.getProperty('email')
        request_emission_time = str(int(time()))
        hash_object = sha.new()
        hash_object.update(username)
        hash_object.update(request_emission_time)
        hash_object.update(self.getNonce())
        reset_token = hash_object.hexdigest()
        try:
            mail_from_address = getattr(self.portal_properties,
                                        'email_from_address')
        except (AttributeError):
            LOG('CPSCore.CPSMembershipTool', PROBLEM,
                "Your portal has no \"email_from_address\" defined. \
                Reseting password will not be performed because the users have \
                to trust who send them this reset password email.")
        mail_to_address = email_address
        subject = "Password reset confirmation"
        # d:  the date of the request emission
        # t:  the token
        visit_url = ("%s/account_reset_password_form?username=%s&d=%s&t=%s"
                     % (self.portal_url(),
                        username, request_emission_time, reset_token))
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
            mail_from_address, email_address, subject,
            "You can reset your password at the page %s"
            % visit_url)

        try:
            self.MailHost.send(content,
                               mto=mail_to_address, mfrom=mail_from_address,
                               subject=subject, encode='8bit')
        except (socket.error, SMTPException, MailHostError):
            LOG('CPSCore.CPSMembershipTool', PROBLEM,
                "Error while sending reset token email")
        result = {'reset_token': reset_token,
                  'emission_time': request_emission_time,
            }
        return result


    security.declarePublic('isPasswordResetRequestValid')
    def isPasswordResetRequestValid(self, username, emission_time, reset_token):
        """Return wether a request for a password reset is valid or not."""
        member = self.getMemberById(username)
        if member is None:
            raise ValueError("The username cannot be found.")
        hash_object = sha.new()
        hash_object.update(username)
        hash_object.update(emission_time)
        hash_object.update(self.getNonce())
        result = hash_object.hexdigest()
        if (reset_token == result
            and int(emission_time) + self.reset_password_request_validity >=
            int(time())):
            return True
        return False


    security.declarePublic('resetPassword')
    def resetPassword(self, username, emission_time, reset_token):
        """Reset a user's password

        This methods returns a dictionary containing
        1. the new randomly generated password
        2. a boolean telling if the password resetting has been successful
        """
        result = {'new_password': None,
                  'reset_password_success': False,
                  }
        if not self.isPasswordResetRequestValid(username,
                                                emission_time, reset_token):
            LOG('CPSCore.CPSMembershipTool', INFO,
                "An invalid password reset request has been received.")
            return result
        member = self.getMemberById(username)
        if member is None:
            raise ValueError("The username cannot be found.")
        email_address = member.getProperty('email')
        random.seed()
        new_password = generatePassword()
        user = member.getUser()
        self.acl_users._doChangeUser(username, new_password,
                                     user.getRoles(), user.getDomains())
        result['new_password'] = new_password
        result['reset_password_success'] = True
        return result


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
