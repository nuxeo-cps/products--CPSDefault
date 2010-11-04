#!/usr/bin/python
#
# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
# M.-A. Darche <ma.darche@cynode.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Create a zope server, install cps products and start the server.
"""
import os, sys, time
from tempfile import gettempdir
from time import strftime, gmtime
from ConfigParser import ConfigParser, NoOptionError
from funkload.utils import trace

CONF_PATH = "create_zope_server.conf"

def system(cmd):
    """Execute a shell cmd and exit on fail."""
    trace("  sh: %s ... " % cmd)
    ret = os.system(cmd)
    if ret != 0:
        trace("\n### Error: exec return code %s" % ret)
        sys.exit(ret)
    trace("done.\n")


def makeZopeInstance(zope_home, zope_server_path, port,
                     admin_login, admin_password):
    """Make a zope instance."""
    if os.path.exists(zope_server_path):
        trace('Zope server %s already instancied.\n' % zope_server_path)
        return
    trace('Making a zope instance:\n')
    system("%s/bin/mkzopeinstance.py --dir %s --user %s:%s" %
           (zope_home, zope_server_path, admin_login, admin_password))
    trace('Setup zope.conf:\n')
    system("mv %(zs)s/etc/zope.conf %(zs)s/etc/zope.conf.orig" %
           {'zs': zope_server_path})
    system("sed s/8080/%(port)s/g %(zs)s/etc/zope.conf.orig > %(zs)s/etc/zope.conf" % {'zs': zope_server_path, 'port': port})


def setupCPSProducts(zope_server_path, targz=None):
    """Install CPS Products.
    """
    trace('Backup Products:\n')
    system("mv %s/Products %s/Products.%s" % (zope_server_path,
                                              zope_server_path,
                                              time.time()))
    root = 'Products'
    if targz.startswith('latest'):
        cps = 'full' in targz and 'full' or 'base'
        root = 'CPS-3-%s' % cps
        date = strftime('%Y-%m-%d', gmtime())
        targz = 'CPS-3-%s-%s.tgz' % (cps, date)
        tmp_targz = os.path.join(gettempdir(), targz)
        if os.path.exists(tmp_targz):
            trace("Using nightly build temp file %s.\n" % tmp_targz)
        else:
            url = 'http://download.cps-cms.org/nightly/' + targz
            trace("Fetching nigthly latest nigthly build:\n")
            system("wget %s -O %s" % (url, tmp_targz))
        targz = tmp_targz
    trace("Setup Products using a tarball:\n")
    system("cd %s && tar xzf %s" % (zope_server_path, targz))
    if root != 'Products':
        system("mv %s/%s %s/Products" % (zope_server_path, root,
                                         zope_server_path))

    import compileall
    compileall_path = compileall.__file__
    trace("Compiling Products:\n")
    system('python %s -x "(skins|scripts)" %s/Products > /dev/null' %
           (compileall_path, zope_server_path))


def main(conf_path):
    """The main."""
    # read config
    conf = ConfigParser(defaults={'FLOAD_HOME':
                                  os.getenv('FLOAD_HOME','.')})
    trace("### create_zope_server use conf file: %s.\n" % conf_path)
    conf.read(conf_path)
    zope_home = conf.get('main', 'zope_home')
    zope_server_path = conf.get('main', 'zope_server_path')
    port = conf.get('main', 'port')
    admin_login = conf.get('main', 'admin_login')
    admin_password = conf.get('main', 'admin_password')
    try:
        targz = conf.get('main', 'targz')
    except NoOptionError:
        targz = None

    makeZopeInstance(zope_home, zope_server_path, port,
                     admin_login, admin_password)
    setupCPSProducts(zope_server_path, targz)
    # start zs
    trace("### create_zope_server done.\n")


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        main(sys.argv[1])
    else:
        main(CONF_PATH)
