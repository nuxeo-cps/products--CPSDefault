# -*- coding: iso-8859-15 -*-
# (C) Copyright 2003-2009 Nuxeo SA <http://nuxeo.com>
# Authors:
# Florent Guillaume <fg@nuxeo.com>
# G. Racinet <georges@racinet.fr>
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

import os, sys
import unittest
from DateTime import DateTime
from OFS.Image import File
from AccessControl import Unauthorized

from Products.CMFCore.utils import _getViewFor
from Products.CMFCore.utils import getToolByName

from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from Products.CPSSchemas.Widget import widgetname
from Products.CPSUtil.tests.web_conformance import assertWellFormedXml
from Products.CPSUtil.text import get_final_encoding

from document_definitions import getDocumentSchemas

DOCUMENT_TYPES = ['Chapter', 'News Item', 'File', 'Flash Animation',
                  'Glossary', 'Image', 'Section', 'FAQ', 'Page', 'ZippedHtml', 'Book',
                  'Link', 'ImageGallery', 'Workspace', 'Press Release', 'Flexible',
                  'FAQitem', 'Document', 'GlossaryItem', 'EventDoc']

class DummyResponse:
    def __init__(self):
        self.headers = {}
        self.data = ''

    def setHeader(self, key, value):
        self.headers[key] = value

    def write(self, data):
        self.data += data

    def redirect(self, url):
        self.redirect_url = url


def randomText(max_len=10):
    import random
    return ''.join(
        [chr(random.randint(32, 128)) for i in range(0, max_len)])


class TestDocuments(CPSTestCase):
    def afterSetUp(self):
        # adding a ws reader user to test access rigths
        mtool = getToolByName(self.portal, 'portal_membership')
        mdir = getToolByName(self.portal, 'portal_directories').members
        mdir._createEntry({'id': 'wsreader', 'roles': ('Member',)})
        self.ws = self.portal.workspaces
        mtool.setLocalRoles(self.ws, ['wsreader'], 'WorkspaceReader')

        self.login('manager')
        self.document_schemas = getDocumentSchemas()
        # GR This is lame, intended for compat with the sequel
        # that expects the good ol' dict from CPS 3.3's getDocumentTypes
        # which is now otherwise unused
        self.document_types = dict((k,None) for k in DOCUMENT_TYPES)
        # getFolderContents check SESSION to get user display choice
        self.portal.REQUEST.SESSION = {}
        self.portal.REQUEST.form = {}

    def beforeTearDown(self):
        self.logout()

    attr_values_1 = {'1 Subject': ['1 New Subject',],
                     '1 Title': '1 New Title',
                     '1 Description': '1 New Description'}
    def testCreateDocumentsInWorkspacesRoot(self):
        for doc_type in self.document_types.keys():
            if doc_type in ('Section',):
                continue
            doc_id = doc_type.lower()

            try:
                self.ws.invokeFactory(doc_type, doc_id)
            except:
                # Can't be caught properly in here.
                # raise 'ValueError', 'No such content type: %s' % type_name
                # from the TypesTool
                # in the CMF version there's no Workspace content type
                if doc_type == 'Workspace':
                    break
            else:
                proxy = getattr(self.ws, doc_id)
                try:
                    doc = proxy.getEditableContent()
                except AttributeError:
                    doc = proxy

                self._validateDocument(proxy, doc)
                self._testAttributeValues(doc)

                # testing edition
                # contributors is not expected to change during edition
                expected_invariable = {}
                expected_invariable['Contributors'] = doc.contributors
                expected_invariable['Creator'] = doc.Creator()
                doc.edit(proxy=proxy, **self.attr_values_1)
                self._validateDocument(proxy, doc)
                self._testAttributeValues(doc, self.attr_values_1)
                self._testAttributeValues(doc, expected_invariable)

                # test edit permission
                self.login('wsreader')
                self.assertRaises(Unauthorized, doc.edit,
                                  proxy=proxy, **self.attr_values_1)
                doc._edit(proxy=proxy, **self.attr_values_1)
                self.login('manager')

        # Now testing global view for the container
        self.assert_(self.ws.folder_view())

    def _validateDocument(self, proxy, doc):
        self._testDefaultAttributes(doc)
        self.assertEquals(doc.getAdditionalContentInfo(proxy), {})
        # Rendering / default view test (on the proxy)
        self._testRendering(doc, proxy=proxy)
        self._testMetadataRendering(doc, proxy=proxy)
        self._testEditRendering(doc, proxy=proxy)
        # Normal View
        view = _getViewFor(proxy)
        self.assert_(view())
        assertWellFormedXml(doc.exportAsXML(proxy=proxy), "exportAsXML")

    # Standard conversion to attributes for special metadata schema.
    field_to_attr = {
        'Creator': None,
        'CreationDate': 'creation_date',
        'Title': 'title',
        'Subject': 'subject',
        'Description': 'description',
        'Contributors': 'contributors',
        'ModificationDate': 'modification_date',
        'EffectiveDate': 'effective_date',
        'ExpirationDate': 'expiration_date',
        'Format': 'format',
        'Language': 'language',
        'Rights': 'rights',
        'Coverage': 'coverage',
        'Source': 'source',
        'Relation': 'relation',
        'ziparchiveuploader': None, # computed field with no write to attr
        }

    def _testDefaultAttributes(self, doc):
        type_info = doc.getTypeInfo()
        for schema in type_info.schemas:
            for prop_name in self.document_schemas[schema].keys():
                attr_name = self.field_to_attr.get(prop_name, prop_name)
                if attr_name is None:
                    # Not expected to be an attribute at all.
                    continue
                self.assert_(hasattr(doc, attr_name))

    def _testAttributeValues(self, doc, attr_expected=None):
        # size of the document must be > 0
        self.assert_(doc.get_size() > 0)
        if attr_expected is not None:
            type_info = doc.getTypeInfo()
            for schema in type_info.schemas:
                for prop_name in self.document_schemas[schema].keys():
                    if prop_name not in attr_expected.keys():
                        continue
                    attr_name = self.field_to_attr.get(prop_name, prop_name)
                    if attr_name is None:
                        # Not expected to be an attribute at all.
                        continue
                    self.assertEquals(getattr(doc, attr_name),
                                      attr_expected[prop_name],
                                      'attr %s is %s expected %s' % (
                        attr_name, getattr(doc, attr_name),
                        attr_expected[prop_name]))

    def _testRendering(self, doc, proxy):
        res = doc.render(proxy=proxy)
        self.assert_(res)
        main, cidparts = doc.renderEmail(proxy=proxy)
        self.assert_(res)

    def _testMetadataRendering(self, doc, proxy):
        res = doc.render(request=None, proxy=proxy, layout_mode='view',
                         cluster='metadata')
        self.assert_(res)
        res = doc.render(request=None, proxy=proxy, layout_mode='edit',
                         cluster='metadata')
        self.assert_(res)

    def _testEditRendering(self, doc, proxy):
        res = doc.render(request=None, proxy=proxy, layout_mode='edit')
        self.assert_(res)

    def testCreateDocumentsInWorkspacesRootThroughWFTool(self):
        try:
            wft = self.portal.portal_workflow
            for doc_type in self.document_types.keys():
                if doc_type in ('Section', ):
                    continue
                wft.invokeFactoryFor(self.ws, doc_type, doc_type.lower())
        except AttributeError:
            # CMF
            pass

    def testMetadata(self):
        id = 'testMetadataNews'
        self.ws.invokeFactory('News Item', id)
        proxy = getattr(self.ws, id)
        try:
            doc = proxy.getEditableContent()
        except AttributeError:
            doc = proxy

        metadata = ('Title', 'Description', 'Subject', 'Contributors',
                    'CreationDate', 'ModificationDate',
                    # We get into trouble because
                    # EffectiveDate == ExpirationDate below
                    #'EffectiveDate', 'ExpirationDate',
                    'Format', 'Rights', 'Creator', 'Source', 'Relation',
                    'Coverage')
        data = {}
        form = {}
        for name in metadata:
            if name == 'Relation':
                v = 'http://www.nuxeo.com'
            elif name.endswith('Date'):
                date = '2004/01/01'
                hour = '23'
                minute = '59'
                v = DateTime('%s %s:%s' % (date, hour, minute))
                form[widgetname(name + '_d')] = date
                form[widgetname(name + '_h')] = hour
                form[widgetname(name + '_m')] = minute
            elif name == 'Contributors':
                v = ['The %s' % name]
            elif name in ('Subject',):
                v = []
            else:
                v = 'The %s' % name
            data[name] = v
            form[widgetname(name)] = v

        request = self.portal.REQUEST
        request.form = form
        rendered, is_valid, ds = doc.renderEditDetailed(request=request,
                                                        proxy=proxy,
                                                        layout_id='metadata')
        self.assert_(is_valid, 'invalid input: ' + str(ds.errors) +
                     'ds = ' + str(ds))
        for k, v in data.items():
            self.assertEquals(ds[k], v)

    def testNews(self):
        self.ws.invokeFactory('News Item', 'news')
        proxy = self.ws.news

        try:
            doc = proxy.getEditableContent()
        except AttributeError:
            doc = proxy

        # Test doc has default values
        for prop_name in self.document_schemas['newsitem'].keys():
            # XXX: Default values are not always as defined in
            # getDocumentSchemas(). I consider this as a bug.
            self.assert_(hasattr(doc, prop_name))

        TITLE = u"Un titre accentu\xe9"
        CONTENT = u"L'\xe9t\xe9 est bientôt termin\xe9"

        doc.edit(proxy=proxy, Title=TITLE)
        self.assertEquals(doc.Title(), TITLE)

        doc.edit(proxy=proxy, content=CONTENT)
        self.assertEquals(doc.content, CONTENT)
        self.assertEquals(
            doc.getAdditionalContentInfo(proxy)['summary'], CONTENT)

        # Test view

        view = proxy.cpsdocument_view()
        if not isinstance(view, unicode):
            view = view.decode(get_final_encoding(proxy))
        self.assert_(TITLE in view)
        self.assert_(CONTENT in view)

        # Test summary for long content
        from Products.CPSDocument.CPSDocument import SUMMARY_MAX_LEN
        very_long_content = 'A very long content' * 100
        doc.edit(proxy=proxy, content=very_long_content)
        self.assertEquals(
            doc.getAdditionalContentInfo(proxy)['summary'],
            very_long_content[0:SUMMARY_MAX_LEN] + '...')

    def testFile(self):
        self.ws.invokeFactory('File', 'file1')

        proxy = self.ws.file1
        try:
            doc = proxy.getEditableContent()
        except AttributeError:
            doc = proxy

        self.assertEquals(doc.file, None)
        self.assertEquals(proxy['file'], None)
        #XXX move download tests to the proxy behavior
        #XXX self.assertEquals(doc.downloadFile('file'), '')

        # Edit file as string
        text = randomText()
        ftext = File('file', 'something.txt', text)
        doc.edit(proxy=proxy, file=ftext)
        self.assertEquals(str(doc.file), text)
        self.assertEquals(str(proxy['file']), text)
        #XXX self.assertEquals(doc.downloadFile('file'), text)

        # XXX: theses tests are not enough, this the *proxy*'s behavior
        # is not correct, not the document's.
        #response = DummyResponse()
        #doc.downloadFile('file', response)
        #self.assertEquals(response.data, text)
        #self.assertEquals(response.headers['Content-Type'],
        #    'application/octet-stream')
        #self.assertEquals(response.headers['Content-Length'],
        #    len(text))
        #self.assertEquals(response.headers['Content-Disposition'],
        #    "inline; filename=file")

        if 0: # XXX Don't know hown to do that
            # Edit
            class FieldStorage:
                def __init__(self, **kw):
                    for k, v in kw.items():
                        setattr(self, k, v)
            from StringIO import StringIO
            from ZPublisher.HTTPRequest import FileUpload
            text = randomText()
            file = StringIO(text)
            fs = FieldStorage(file=file, headers={"Content-Type": "text/html"},
                filename="filename")
            fileupload = FileUpload(fs)

            doc.renderEdit(file=fileupload)

            response = DummyResponse()
            doc.downloadFile('file', response)
            self.assertEquals(response.data, text)
            self.assertEquals(response.headers['Content-Type'],
                'application/octet-stream')
            self.assertEquals(response.headers['Content-Length'],
                len(text))
            self.assertEquals(response.headers['Content-Disposition'],
                "inline; filename=filename")

    def testFileCalledFile(self):
        self.ws.invokeFactory('File', 'file')
        proxy = self.ws.file
        try:
            doc = proxy.getContent()
        except AttributeError:
            doc = proxy
        self.assert_(proxy['file'])

    def testFlexible(self):
        self.ws.invokeFactory('Flexible', 'flex')
        try:
            doc = self.ws.flex.getContent()
        except AttributeError:
            doc = self.ws.flex
        tinfo = doc.getTypeInfo()
        wid = tinfo.flexibleAddWidget(doc, 'flexible_content', 'link')
        doc.edit(link_href_f0='http://test.nohost')
        self.assertEquals(doc.link_href_f0, 'http://test.nohost')

    def testDocumentSearch(self):
        # The aim of this test is first to assert that documents can be queried.
        # But the true aim of this test is to assert that one discovered bug is
        # truly fixed and for good. The bug in question was that tuples couldn't
        # be used as portal_type query parameters.
        # So this test assert that text, list and tuple can equally be used as
        # portal_type query parameter.
        #
        # XXX : This test is not relevent at the moment as the search script
        # does not run the same way during unit tests and during real life
        # exploitation. A note on the matter has been added in
        # CPSDefault/skins/cps_default/search.py

        document_types = self.document_types.keys()

        # Search done with the catalog
        catalog = self.portal.portal_catalog
        query = {'SearchableText': ''}
        proxies = catalog(**query)
        #print "proxies count = %s" % len(proxies)

        # Subsequent searches done with the search script
        proxies = self.ws.search(query={'SearchableText': ''})
        #print "proxies count = %s" % len(proxies)

        proxies = self.ws.search(query={'portal_type': document_types[0],
                                        })
        #print "proxies count = %s" % len(proxies)

        proxies = self.ws.search(query={'portal_type': [document_types[0],
                                                        document_types[1],
                                                        document_types[2]]
                                        })
        #print "proxies count = %s" % len(proxies)

        proxies = self.ws.search(query={'portal_type': (document_types[0],
                                                        document_types[1],
                                                        document_types[2])
                                        })
        #print "proxies count = %s" % len(proxies)


        # XXX: what next?

    def testObjectCreationWithMetadataForDataModel(self):

        #
        # Test passing kw to invokeFactory to initialize data model.
        # Test standard working case with key values included within the dm
        #

        doc_type = 'File'
        doc_id = doc_type.lower()

        self.ws.invokeFactory(doc_type, doc_id, Title='title',
                              Description='description')

        proxy = getattr(self.ws, doc_id)
        doc = proxy.getContent()

        self.assertEqual(doc.Title(), 'title')
        self.assertEqual(doc.Description(), 'description')

        self.ws.manage_delObjects([doc_id])

        self.assert_(doc_id not in self.ws.objectIds())

    def testObjectCreationWithNonValideValuesForDataModel(self):

        # Non working case with key values not included within the dm

        doc_type = 'File'
        doc_id = doc_type.lower()

        self.ws.invokeFactory(doc_type, doc_id, xx='title', yy='description')

        proxy = getattr(self.ws, doc_id)
        doc = proxy.getContent()

        self.assertEqual(getattr(doc, 'xx', None), None)
        self.assertEqual(getattr(doc, 'yy', None), None)

        self.ws.manage_delObjects([doc_id])

        self.assert_(doc_id not in self.ws.objectIds())

    def testObjectCreationWithNonMetadataValuesForDataModel(self):

        # Non special metadata case working

        doc_type = 'File'
        doc_id = doc_type.lower()

        file_instance = File('x', 'x', 'xx')
        self.ws.invokeFactory(doc_type, doc_id, file=file_instance)

        proxy = getattr(self.ws, doc_id)
        doc = proxy.getContent()

        dm = doc.getTypeInfo().getDataModel(doc, proxy)
        self.assert_('file' in dm.keys())

        self.assertEqual(doc.file, file_instance)

        self.ws.manage_delObjects([doc_id])

        self.assert_(doc_id not in self.ws.objectIds())

    def testGetDataModel(self):

        # test getDataModelMethod

        doc_type = 'File'
        doc_id = doc_type.lower()

        file_instance = File('x', 'x', 'xx')
        self.ws.invokeFactory(doc_type, doc_id, file=file_instance)

        proxy = getattr(self.ws, doc_id)
        doc = proxy.getContent()

        # Fetch the dm directly with the CPSDocument.getDataModel()
        dm = doc.getDataModel(proxy=proxy)
        self.assert_(dm)

        # Fetch the dm though the getTypeInfo()
        dm2 = doc.getTypeInfo().getDataModel(doc, proxy=proxy)
        self.assert_(dm2)

        # unwrap file protections and check that they are the same
        dm._unProtectFiles()
        dm2._unProtectFiles()
        self.assertEqual(dm, dm2)

    def test_validate_pre_commit_hook(self):
        # this no more mis-placed than the previous one :-)

        def pre_hook(dm, proxy=None, **kw):
            proxy.freezeProxy()

        self.ws.invokeFactory('Workspace', 'test',
                              Title='test', Description='Old')
        proxy = self.ws.test
        ob = proxy.getContent()

        request = self.portal.REQUEST
        request.form = {widgetname('Description') : 'New descr'}
        ob.validate(request=request, proxy=proxy, pre_commit_hook=pre_hook)

        proxy = self.ws.test
        # modification was done
        self.assertEquals(proxy.getContent().Description(), 'New descr')
        # hook was called
        self.assertEquals(proxy.getRevision(), 2)
        # and that was before the DM commit
        self.assertEquals(proxy.getContent(rev=1).Description(), 'Old')

    def testFlashDocument(self):

        doc_type = 'Flash Animation'
        doc_id = doc_type.lower()

        from Products.CPSDocument import tests
        TEST_SWF = os.path.join(tests.__path__[0], 'test.swf')

        data = open(TEST_SWF, 'r').read()
        file_instance = File('x', 'x', data)

        # Done at upload time usually
        file_instance.content_type = 'application/x-shockwave-flash'

        self.ws.invokeFactory(doc_type, doc_id, file=file_instance)

        proxy = getattr(self.ws, doc_id)

        # Render the document
        ob = proxy.getContent()
        res = ob.render(layout_mode='view',
                        layout_id='flash_animation',
                        proxy=proxy)

        # XXX test the HTML rendering

    def testSearchableText(self):

        # Test the SearchableText method

        doc_type = 'File'
        doc_id = doc_type.lower()

        file_instance = File('x', 'x', '')
        self.ws.invokeFactory(doc_type, doc_id, file=file_instance)
        proxy = getattr(self.ws, doc_id)

        # edit Title
        doc = proxy.getEditableContent()
        doc.edit(proxy=proxy, Title='a title')

        stext = doc.SearchableText()

        # It should return at least the title right now.
        self.assert_(stext)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDocuments))
    return suite
