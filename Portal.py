# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
""" Default portal for CPS
"""

import Globals
from zLOG import LOG, INFO, DEBUG
from Products.CMFDefault.Portal import CMFSite
from Products.ExternalMethod.ExternalMethod import ExternalMethod

class CPSDefaultSite(CMFSite):
    meta_type = 'CPSDefault Site'

Globals.InitializeClass(CPSDefaultSite)

manage_addCPSDefaultSiteForm = Globals.HTMLFile('zmi/manage_addCPSSiteForm', globals())

def manage_addCPSDefaultSite(dispatcher, id,
                      title='CPSDefault Portal',
                      description='',
                      langs_list=None,
                      root_id='root',
                      root_sn='CPS',
                      root_givenName='Root',
                      root_email='root@localhost',
                      root_password1='root',  # XXX TODO: remove this
                      root_password2='root',  # XXX TODO: remove this
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

    
    pr('Creating cpsinstall External Method in CMF Site')
    cpsinstall = ExternalMethod('cpsinstall',
                                'CPSDefault Installer',
                                'CPSDefault.cpsinstall',
                                'cpsinstall')
    portal._setObject('cpsinstall', cpsinstall)
    
    pr('Creating cpsupdate External Method in CMF Site')
    CPSDefaultupdate = ExternalMethod('cpsupdate',
                               'CPSDefault Updater',
                               'CPSDefault.cpsinstall',
                               'cpsupdate')
    portal._setObject('cpsupdate', CPSDefaultupdate)
    
    pr('Executing CPSDefault Installer')
    pr(portal.cpsinstall(), 0)
    
    pr('Executing CPSDefault Updater')
    pr(portal.cpsupdate(langs_list=langs_list), 0)
    
    pr('Configuring CPSDefault Portal')
    # editProperties do not work with ZTC due to usage of REQUEST to send properties :/
    portal.MailHost.smtp_host = 'localhost'
    portal.manage_changeProperties(REQUEST=None, 
                                   kw={
                                       'email_from_name': ('%s %s' % (root_givenName, root_sn)).strip(),
                                       'email_from_address': root_email,
                                       'smtp_server': 'localhost',
                                       }
                                   )
    
    # TODO: use portal_metadirectories to store emails and other stuff
    pr('Creating CPS Administrator account for CPSDefault')
    portal.acl_users._addUser(name=root_id,
                              password=root_password1,
                              confirm=root_password2,
                              roles=('Manager', 'Member'), domains=None)
                                         
    # XXX TODO: remove this test user
    for i in ('1', '2', '3'):
        user='user%s' % i
        pr('Creating test user: %s' % user)
        portal.acl_users._addUser(name=user,
                                  password=user,
                                  confirm=user,
                                  roles=('Member', ), domains=None)

    pr('Done')
    if REQUEST is not None:
        REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')

    return pr('flush')

#EOF
