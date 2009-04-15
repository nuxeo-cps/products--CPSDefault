# (C) Copyright 2009 Association Paris-Montagne
# Author: Georges Racinet <georges@racinet.fr>
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
"""
    View that knows how to perform switch user operations against CPSUserFolder
"""
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from Products.CPSUserFolder.interfaces import ICPSUserFolder

SU_INPUT_NAME = "su_name"
SU_BUTTON_NAME = "su"
SU_STOP_BUTTON_NAME = "su_stop"

class SwitchUserView(BrowserView):

    def getAclu(self):
        aclu = getToolByName(self.context, 'acl_users')
        if not ICPSUserFolder.providedBy(aclu):
            raise RuntimeError("User folder isn't a CPSUserFolder")
        return aclu


    def switchUser(self):
        form = self.request.form
        su_stop = form.get(SU_STOP_BUTTON_NAME)
        if su_stop:
            return self.unSwitchUser()

        su_go = form.get(SU_BUTTON_NAME)
        if not su_go:
            return

        su_name = form.get(SU_INPUT_NAME)
        if su_name is not None:
            su_name = su_name.strip()
        resp = self.request.RESPONSE
        if su_name:
            self.getAclu().requestUserSwitch(su_name, resp=resp,
                                           portal=self.context)
        resp.redirect(self.context.absolute_url())

    def getSuInputName(self):
        return SU_INPUT_NAME

    def getSuButtonName(self):
        return SU_BUTTON_NAME

    def getSuStopButtonName(self):
        return SU_STOP_BUTTON_NAME

    def getActiveSwitchUserName(self):
        return self.getAclu().getSwitchUserName(self.request)

    def unSwitchUser(self):
        self.getAclu().requestUserUnSwitch(resp=self.request.RESPONSE,
                                           portal=self.context)
        self.request.RESPONSE.redirect(self.context.absolute_url())
