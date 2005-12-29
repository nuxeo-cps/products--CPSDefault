# Copyright (c) 2003-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
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
from Products.CMFDefault.Portal import CMFSite, PortalGenerator
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from AccessControl import ClassSecurityInfo

from zope.interface import implements
from Products.CPSDefault.interfaces import ICPSSite

class CPSDefaultSite(CMFSite):
    """CPS variant of a CMF Portal."""

    implements(ICPSSite)

    meta_type = 'CPSDefault Site'
    portal_type = 'Portal'

    cps_version = ('CPS', 3, 3, 8)

    # Override default OrderSupport behavior for ZMI convenience
    _default_sort_key = 'id'

    security = ClassSecurityInfo()

    _properties = CMFSite._properties + (
        {'id': 'last_upgraded_version', 'type': 'string',
         'label': 'Last upgraded version', 'mode': 'w'},
        # XXX these should be in the portal_membership tool
        {'id': 'enable_password_reset', 'type': 'boolean',
         'label': 'Enable password resetting', 'mode': 'w'},
        {'id': 'enable_password_reminder', 'type': 'boolean',
         'label': 'Enable sending password reminder', 'mode': 'w'},
        {'id': 'enable_portal_joining', 'type': 'boolean',
         'label': 'Enable portal joining', 'mode': 'w'},
        )
    last_upgraded_version = '.'.join(map(str, cps_version[1:]))
    # XXX
    enable_password_reset = True
    enable_password_reminder = False
    enable_portal_joining = False

    security.declarePublic('getCPSVersion')
    def getCPSVersion(self):
        """ returns cps version
        """
        return self.cps_version

Globals.InitializeClass(CPSDefaultSite)

class CPSPortalGenerator(PortalGenerator):
    """Set up a CPS Portal."""
    klass = CPSDefaultSite

manage_addCPSDefaultSiteForm = Globals.HTMLFile('zmi/manage_addCPSSiteForm',
                                                globals())

def manage_addCPSDefaultSite(dispatcher, id,
                             title='CPSDefault Portal',
                             description='',
                             langs_list=None,
                             manager_id='manager',
                             manager_sn='CPS',
                             manager_givenName='Manager',
                             manager_email='',
                             manager_password='',
                             manager_password_confirmation='',
                             REQUEST=None):
    """Add a CPSDefault Site."""

    _log = []
    def pr(bla, zlog=1, _log=_log):
        if bla == 'flush':
            return '<br/>\n'.join(_log)
        _log.append(bla)
        if (bla and zlog):
            LOG('addCPSDefaultSite:', INFO, bla)

    id = id.strip()
    title = title.strip()
    description = description.strip()
    manager_id = manager_id.strip()
    manager_email = manager_email.strip()
    manager_givenName = manager_givenName.strip()
    manager_sn = manager_sn.strip()

    if not id:
        raise ValueError, "You have to provide an id for the portal!"
    if not manager_id:
        raise ValueError, "You have to provide an id for the CPS Administrator!"
    if not manager_email:
        raise ValueError, "You have to provide an email address for the CPS Administrator!"
    if not manager_password:
        raise ValueError, "You have to provide CPS Administrator password!"
    if manager_password != manager_password_confirmation:
        raise ValueError, "Password confirmation does not match password!"

    email_from_name = ('%s %s' % (manager_givenName, manager_sn)).strip()

    pr('Adding a CPSDefault Site')
    gen = CPSPortalGenerator()
    portal = gen.create(dispatcher, id, create_userfolder=0)

    # Ugly hack to get around incompatibility between CMF 1.5 and 1.4
    try:
        gen.setupDefaultProperties(portal, title, description,
                                   email_from_address=manager_email,
                                   email_from_name=email_from_name,
                                   validate_email=0, default_charset='')
    except TypeError:
        gen.setupDefaultProperties(portal, title, description,
                                   email_from_address=manager_email,
                                   email_from_name=email_from_name,
                                   validate_email=0)

    pr('Creating cpsupdate External Method in CPS Site')
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
    pr(portal.cpsupdate(langs_list=langs_list, is_creation=1), 0)

    pr('Configuring CPSDefault Portal')
    # editProperties do not work with ZTC due to usage of REQUEST
    # to send properties :/
    # herve: REQUEST is a mapping. Have you checked using
    #            REQUEST={'smtp_host': 'localhost'}
    #        as an argument?
    portal.MailHost.smtp_host = 'localhost'
    portal.manage_changeProperties(smtp_server='localhost', REQUEST=None)

    pr('Creating CPS Administrator account for CPSDefault')
    mdir = portal.portal_directories.members
    entry = {
        'id': manager_id,
        'password': manager_password,
        'roles': ['Manager', 'Member'],
        'email': manager_email,
        'givenName': manager_givenName,
        'sn': manager_sn,
    }
    mdir.createEntry(entry)

    pr('Done')
    pr('<script type="text/javascript">window.parent.update_menu();</script>')
    if REQUEST is not None:
        REQUEST.RESPONSE.setHeader('Content-Type', 'text/html')

    return pr('flush')
