# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
"""
    SSS3 Sample Skeleton Site for CPS3
"""

import Globals
from zLOG import LOG, INFO, DEBUG
from Products.CMFDefault.Portal import CMFSite
from Products.ExternalMethod.ExternalMethod import ExternalMethod

class Sss3Site(CMFSite):
    meta_type = 'Sss3 Site'

Globals.InitializeClass(Sss3Site)

manage_addSss3SiteForm = Globals.HTMLFile('zmi/manage_addCPSSiteForm', globals())

def manage_addSss3Site(dispatcher, id,
                      title='Sss3 Portal',
                      description='',
                      langs_list=None,
                      root_id='root',
                      root_sn='CPS',
                      root_givenName='Root',
                      root_email='root@cps',
                      root_password1='root',  # XXX TODO: remove this
                      root_password2='root',  # XXX TODO: remove this
                      REQUEST=None):
    """Add a Sss3 Site."""

    _log = []
    def pr(bla, zlog=1, _log=_log):
        if bla == 'flush':
            return '\n'.join(_log)
        _log.append(bla)
        if (bla and zlog):
            LOG('addSss3Site:', INFO, bla)

    if not root_password1:
        raise ValueError, 'You have to fill CPS Administrator password!'
    if root_password1 != root_password2:
        raise ValueError, 'Password confirmation does not match password'

    pr('Adding a Sss3 Site')
    container = dispatcher.Destination()
    pr('Creating CMF Site')
    container.manage_addProduct['CMFDefault'].manage_addCMFSite(id,
                    title=title,
                    description=description,
                    create_userfolder=0)
    portal = getattr(container, id)

    
    pr('Creating cpsinstall External Method in CMF Site')
    cpsinstall = ExternalMethod('cpsinstall',
                                'SSS3 Installer',
                                'SSS3.cpsinstall',
                                'cpsinstall')
    portal._setObject('cpsinstall', cpsinstall)
    
    pr('Creating cpsupdate External Method in CMF Site')
    sss3update = ExternalMethod('cpsupdate',
                               'SSS3 Updater',
                               'SSS3.cpsinstall',
                               'cpsupdate')
    portal._setObject('cpsupdate', sss3update)
    
    pr('Executing Sss3 Installer')
    pr(portal.cpsinstall(), 0)
    
    pr('Executing Sss3 Updater')
    pr(portal.cpsupdate(langs_list=langs_list), 0)
    
    pr('Configuring Sss3 Portal')
    portal.portal_properties.editProperties(
        {
            'email_from_name': ('%s %s' % (root_givenName, root_sn)).strip(),
            'email_from_address': root_email,
            'smtp_server': 'localhost',
        }
    )
    
    # TODO: use portal_metadirectories to store emails and other stuff
    pr('Creating CPS Administrator account for Sss3')
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
