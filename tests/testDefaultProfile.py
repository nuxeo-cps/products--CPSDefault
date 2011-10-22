# $Id$

import unittest

from Products.CMFCore.utils import getToolByName
from Products.CPSCore.setuptool import CPSSetupTool
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase

DEFAULT_PROFILE_ID = 'CPSDefault:default'


class TestDefaultProfile(CPSTestCase):

    def afterSetUp(self):
        self.login('manager')
        self.setup_tool = getToolByName(self.portal, CPSSetupTool.id)

    def beforeTearDown(self):
        self.logout()

    def test_reimport_purging(self):
        dirtool = getToolByName(self.portal, 'portal_directories')
        stool = getToolByName(self.portal, 'portal_schemas')

        members = dirtool.members
        self.assertEquals(members.listEntryIds(), ['manager'])

        self.assertEquals('foo' in stool.objectIds(), False)
        stool.manage_addCPSSchema('foo')
        self.assertEquals('foo' in stool.objectIds(), True)

        profile_id = 'profile-' + DEFAULT_PROFILE_ID
        self.setup_tool.reinstallProfile(profile_id, create_report=False)

        # do not purge members
        self.assertEquals(members.listEntryIds(), ['manager'])
        # purge schemas
        self.assertEquals('foo' in stool.objectIds(), False)


    def test_reimport_without_purging(self):
        dirtool = getToolByName(self.portal, 'portal_directories')
        stool = getToolByName(self.portal, 'portal_schemas')

        members = dirtool.members
        self.assertEquals(members.listEntryIds(), ['manager'])

        self.assertEquals('foo' in stool.objectIds(), False)
        stool.manage_addCPSSchema('foo')
        self.assertEquals('foo' in stool.objectIds(), True)

        profile_id = 'profile-' + DEFAULT_PROFILE_ID
        self.setup_tool.importProfile(profile_id, create_report=False)

        # do not purge members
        self.assertEquals(members.listEntryIds(), ['manager'])
        # do not purge schemas
        self.assertEquals('foo' in stool.objectIds(), True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDefaultProfile))
    return suite
