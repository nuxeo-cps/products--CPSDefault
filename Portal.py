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
from Products.CMFDefault.Portal import CMFSite, PortalGenerator
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from AccessControl import ClassSecurityInfo

class CPSDefaultSite(CMFSite):
    """CPS variant of a CMF Portal."""
    meta_type = 'CPSDefault Site'
    portal_type = 'Portal'
    enable_portal_joining = 1
    cps_version = ('CPS', 3, 3, 0)

    security = ClassSecurityInfo()

    _properties = CMFSite._properties + (
        {'id': 'enable_portal_joining', 'type': 'boolean',
         'title': 'Enable portal joining'},
    )

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

    if not manager_email:
        raise ValueError, "You have to provide an email address for the CPS Administrator!"
    if not manager_password:
        raise ValueError, "You have to provide CPS Administrator password!"
    if manager_password != manager_password_confirmation:
        raise ValueError, "Password confirmation does not match password!"

    id = id.strip()
    title = title.strip()
    description = description.strip()
    manager_givenName = manager_givenName.strip()
    manager_sn = manager_sn.strip()
    email_from_name = '%s %s' % (manager_givenName, manager_sn)
    manager_email = manager_email.strip()

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
    pr(portal.cpsupdate(langs_list=langs_list, is_creation=1 ), 0)

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
    if REQUEST is not None:
        REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')

    return pr('flush')
