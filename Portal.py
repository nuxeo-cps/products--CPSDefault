# Copyright (c) 2003 Nuxeo SARL <http://nuxeo.com>
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
""" Default portal for CPS
"""

import Globals
from zLOG import LOG, INFO, DEBUG
from Products.CMFDefault.Portal import CMFSite
from Products.ExternalMethod.ExternalMethod import ExternalMethod

class CPSDefaultSite(CMFSite):
    """This class is never instantiated and only serves for class registration"""
    # XXX Note that whatever you will write here will never be used since
    # manage_addCPSDefaultSite instantiates a CMFSite.
    meta_type = 'CPSDefault Site'

Globals.InitializeClass(CPSDefaultSite)

manage_addCPSDefaultSiteForm = Globals.HTMLFile('zmi/manage_addCPSSiteForm',
    globals())

def manage_addCPSDefaultSite(dispatcher, id,
                             title='CPSDefault Portal',
                             description='',
                             langs_list=None,
                             root_id='root',
                             root_sn='CPS',
                             root_givenName='Root',
                             root_email='root@localhost',
                             root_password1='',
                             root_password2='',
                             enable_portal_joining=1,
                             REQUEST=None):
    """Add a CPSDefault Site."""

    _log = []
    def pr(bla, zlog=1, _log=_log):
        if bla == 'flush':
            return '\n'.join(_log)
        _log.append(bla)
        if (bla and zlog):
            LOG('addCPSDefaultSite:', INFO, bla)

    if not root_password1:
        raise ValueError, 'You have to fill CPS Administrator password!'
    if root_password1 != root_password2:
        raise ValueError, 'Password confirmation does not match password'

    pr('Adding a CPSDefault Site')
    container = dispatcher.Destination()
    pr('Creating CMF Site')
    container.manage_addProduct['CMFDefault'].manage_addCMFSite(id,
                    title=title,
                    description=description,
                    create_userfolder=0)
    portal = getattr(container, id)
    portal.portal_type = 'Portal'
    portal.manage_addProperty('enable_portal_joining', enable_portal_joining,
                              'boolean')

    pr('Creating cpsinstall External Method in CMF Site')
    cpsinstall = ExternalMethod('cpsinstall',
                                'CPSDefault Installer',
                                'CPSDefault.cpsinstall',
                                'cpsinstall')
    portal._setObject('cpsinstall', cpsinstall)

    pr('Creating cpsupdate External Method in CMF Site')
    cpsupdate = ExternalMethod('cpsupdate',
                               'CPSDefault Updater',
                               'CPSDefault.cpsinstall',
                               'cpsupdate')
    portal._setObject('cpsupdate', cpsupdate)

    pr('Creating benchmark External Method')
    benchmarktimer = ExternalMethod('BenchmarkTimer',
                                    'BenchmarkTimer',
                                    'CPSDefault.benchmarktimer',
                                    'BenchmarkTimerInstance')
    portal._setObject('Benchmarktimer', benchmarktimer)


    pr('Creating i18n Updater Support')
    i18n_updater = ExternalMethod('i18n Updater',
                                  'i18n Updater',
                                  'CPSDefault.cpsinstall',
                                  'cps_i18n_update')
    portal._setObject('i18n Updater', i18n_updater)

    pr('Executing CPSDefault Installer')
    pr(portal.cpsinstall(), 0)

    pr('Executing CPSDefault Updater')
    pr(portal.cpsupdate(langs_list=langs_list), 0)

    pr('Configuring CPSDefault Portal')
    # editProperties do not work with ZTC due to usage of REQUEST
    # to send properties :/
    portal.MailHost.smtp_host = 'localhost'
    portal.manage_changeProperties(REQUEST=None,
                                   email_from_name='%s %s' %
                                       (root_givenName.strip(), root_sn.strip())
                                   email_from_address=root_email.strip(),
                                   smtp_server='localhost',
    )

    # TODO: use portal_metadirectories to store emails and other stuff
    pr('Creating CPS Administrator account for CPSDefault')
    portal.acl_users.userFolderAddUser(name=root_id,
                                       password=root_password1,
                                       roles=('Manager', 'Member'), domains=[])

    pr('Done')
    if REQUEST is not None:
        REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')

    return pr('flush')

#EOF
