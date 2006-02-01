# $Id$

import unittest

from Products.CMFCore.utils import getToolByName
from Products.CPSCore.setuptool import CPSSetupTool
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from Products.CPSDefault.factory import CPSSiteConfigurator

MANDATORY_EXTENSIONS = CPSSiteConfigurator.mandatory_extensions
DEFAULT_PROFILE_ID = 'CPSDefault:default'


class TestDefaultProfile(CPSTestCase):
    def afterSetUp(self):
        self.login('manager')
        self.dirtool = getToolByName(self.portal, 'portal_directories')
        self.stool = getToolByName(self.portal, 'portal_schemas')
        self.ptool = getToolByName(self.portal, 'portal_cpsportlets')

    def beforeTearDown(self):
        self.logout()

    def importProfile(self, profile_id=DEFAULT_PROFILE_ID,
                      mandatory_extensions=MANDATORY_EXTENSIONS,
                      extension_ids=(), purge_old=True):
        setup_tool = getToolByName(self.portal, CPSSetupTool.id, None)
        if purge_old:
            # Reset toolset and steps
            # XXX this will be moved to a GenericSetup API later
            setup_tool.__init__()
        setup_tool.setImportContext('profile-%s' % profile_id)
        setup_tool.runAllImportSteps(purge_old=purge_old)
        for extension_id in mandatory_extensions + extension_ids:
            setup_tool.setImportContext('profile-%s' % extension_id)
            setup_tool.runAllImportSteps(purge_old=False)
        setup_tool.setImportContext('profile-%s' % profile_id)

    def test_reimport_purging(self):
        members = self.dirtool.members
        self.assertEquals(members.listEntryIds(), ['manager'])

        self.assertEquals('foo' in self.stool.objectIds(), False)
        self.stool.manage_addCPSSchema('foo')
        self.assertEquals('foo' in self.stool.objectIds(), True)

        self.importProfile()

        # do not purge members
        self.assertEquals(members.listEntryIds(), ['manager'])
        # purge schemas
        self.assertEquals('foo' in self.stool.objectIds(), False)


    def test_reimport_without_purging(self):
        members = self.dirtool.members
        self.assertEquals(members.listEntryIds(), ['manager'])

        self.assertEquals('foo' in self.stool.objectIds(), False)
        self.stool.manage_addCPSSchema('foo')
        self.assertEquals('foo' in self.stool.objectIds(), True)

        self.importProfile(purge_old=False)

        # do not purge members
        self.assertEquals(members.listEntryIds(), ['manager'])
        # do not purge schemas
        self.assertEquals('foo' in self.stool.objectIds(), True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDefaultProfile))
    return suite
