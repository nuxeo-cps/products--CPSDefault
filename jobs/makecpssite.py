# Copyright (c) 2010 Georges Racinet <http://www.racinet.fr>
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
"""Make a cps site.

This is not a cpsjob in the strict sense, because these require an existing
CPS site to run.
"""

import logging
import sys

import transaction
from AccessControl.SecurityManagement import newSecurityManager
from Products.CPSUtil import cpsjob
from Products.CPSDefault.factory import CPSSiteConfigurator

class JobCPSSiteConfigurator(CPSSiteConfigurator):
    """Subclassing to make a few things optional."""

    def parseForm(self, **kw):
        if kw['manager_id']:
            kw['password_confirm'] = kw['password']
            CPSSiteConfigurator.parseForm(self, **kw)


def login(app, user_id):
    aclu = app.acl_users
    try:
        user = aclu.getUser(user_id).__of__(aclu)
    except KeyError:
        logger.fatal("Please run this as a registered toplevel Zope user.")
        sys.exit(1)

    if not user.has_role('Manager'):
        logger.error("The user %s doesn't have the Manager role", user_id)
        sys.exit(1)

    newSecurityManager(None, user)

def main(app):
    optparser = cpsjob.optparser
    optparser.add_option('-m', '--manager-id', dest='manager_id', default='',
                         help="Create a manager, with this id")
    optparser.add_option('-p', '--manager-password', dest='password',
                         default='',
                         help="Password of the manager to create")
    optparser.add_option('-e', '--manager-email', dest='manager_email',
                         default='',
                         help="Email of the manager to create")

    options, args = optparser.parse_args()
    portal_id = args[0]

    kw = options.__dict__
    login(app, kw.pop('user_id'))
    app = cpsjob.makerequest(app)

    configurator = JobCPSSiteConfigurator()
    configurator.addConfiguredSite(app, portal_id, 'CPSDefault:default',
                                   **options.__dict__)
    transaction.commit()


# invocation through zopectl run
if __name__ == '__main__':
    main(app)

