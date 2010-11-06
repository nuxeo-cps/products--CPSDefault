=================================
CPS Funkload tests and benchmarks
=================================

These tests require the use of FunkLoad_.
And thus FunkLoad_ must be installed.

.. _FunkLoad: http://funkload.nuxeo.org/


Testing an existing Zope server setup
=====================================

WARNING this test will create a new cps site (if not present) with
new accounts defined in the passwords.txt file
DO NOT run this against a production site !!!

you need to set up the Zope admin password in the passwords.txt then::

  make test URL=http://localhost:8080/cps_test

Note that ``cps_test`` is the cps id that will be created if not present.


Benching
========

Run a reproducible bench testing for readers and writers scenarii,
this takes about 25 minutes::

  make RAZ && make && make bench

Reports are saved into report folder.

Benching an existing Zope server setup is also possible::

  make bench URL=http://localhost:8080/cps_test

Benchmark platform and benchmarking constraints
-----------------------------------------------

- Benchmarks should be done on the same platform.

- The system should not have a running desktop environment (such as KDE or
  Gnome) running.

- There should be no other task running on the system, such as an open working
  Mercurial repository, Trac, Apache web server, etc.

- The filesystem should be in order of preference: ext4, XFS, ext3


Testing the latest CPS nightly build
===================================

::
  make


If a functional test fails look at the log/cps-test.xml file and search for
Failure or Error.

See FunkLoad_ documentation to re-launch a single test.


Testing a TARGZ archive
=======================

::

  # edit create_zope_server.conf comment the targz entry, then
  make RAZ && make


Other targets
=============

To volumize the ZODB a bit during 3 minutes (~150 docs) then pack the zodb::

  make volumize

To bench readers (2 benches anonymous and members 5 minutes each)::

  make readers

To bench writers (2 benches publishing and doc creation 5 minutes each)::

  make writers

Remove and reinstall the Zope server::

  make RAZ

Stop everything (credential, monitor and Zope servers)::

  make stop

Start everything (credential, monitor and Zope servers)::

  make start

View the Zope event log::

  make log


See the Makefile for more targets


default configuration
~~~~~~~~~~~~~~~~~~~~~

- the Zope instance is ./var/fl_zope
  defined in create_zope_server.conf and Makefile

- create_zope_server expect a Zope 2.9 available in /opt/Zope2.9
  defined in create_zope_server.conf

- zope url: http://localhost:55580/
  defined in create_zope_server.conf and used in Cps.conf

- cps url http://localhost:55580/fl_cps
  defined in Cps.conf

- credentiald http://localhost:55501/
  defined in credential.conf and used in Cps.conf

- monitord http://localhost:55502/
  defined in monitor.conf and used in Cps.conf

- Zope and CMF credentials see password.txt and groups.txt


.. Local Variables:
.. mode: rst
.. End:
.. vim: set filetype=rst:
