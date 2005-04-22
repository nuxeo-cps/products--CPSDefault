"""Unit tests for CPSSkins i18n

Adapted from plone-i18n

References:
http://i18n.kde.org/translation-howto/check-gui.html#check-msgfmt
http://cvs.sourceforge.net/viewcvs.py/plone-i18n/i18n/tests/
"""


import os, os.path, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
import unittest
from glob import glob
from gettext import GNUTranslations

# FIXME : where is it coming from ?
i18n_lib_here = True
try:
    from msgfmt import Msgfmt, PoSyntaxError
except ImportError:
    i18n_lib_here = False

_TESTS_PATH = os.path.split(__file__)[0]
if not _TESTS_PATH:
    _TESTS_PATH = '.'

try:
    import commands
except ImportError:
    if os.name != 'posix':
        raise ImportError("The i18n tests only runs on posix systems, \
                           such as Linux, \
               due to a dependency on Python's commands.getstatusoutput().")


def canonizeLang(lang):
    return lang.lower().replace('_', '-')

def getLanguageFromPath(path):
    # get file
    file = path.split('/')[-1]
    # strip of .po
    file = file[:-3]
    lang = file.split('-')[1:][-1:]
    return '-'.join(lang)

def getPoPath():
    import Products
    product_file = getattr(Products, 'CPSDefault').__file__
    product_path = os.path.dirname(product_file)
    po_path = os.path.join(product_path, 'i18n')
    return po_path

def getPoFiles():
    po_path = getPoPath()
    po_files = [f for f in os.listdir(po_path) if f.endswith('.po')]
    print po_files
    return po_files


class TestPOT(ZopeTestCase.ZopeTestCase):
    potFile = None

    def testNoDuplicateMsgId(self):
        """Check that there are no duplicate msgid:s in the pot files"""
        cmd='grep ^msgid %s/../i18n/%s|sort|uniq --repeated' % (
            _TESTS_PATH, potFile)
        status = commands.getstatusoutput(cmd)
        assert len(status[1])  == 0, "Duplicate msgid:s were found:\n\n%s" \
                                     % status[1]


class TestPoFile(ZopeTestCase.ZopeTestCase):
    poFile = None

    def testPoFile(self):
        po = self.poFile
        poName = po
        file = open(os.path.join(getPoPath(), po), 'r')
        try:
            lines = file.readlines()
        except IOError, msg:
            self.fail('Can\'t read po file %s:\n%s' % (poName,msg))
        file.close()
        try:
            mo = Msgfmt(lines)
        except PoSyntaxError, msg:
            self.fail('PoSyntaxError: Invalid po data syntax in file %s:\n%s' \
                      % (poName, msg))
        except SyntaxError, msg:
            self.fail('SyntaxError: Invalid po data syntax in file %s \
                      (Can\'t parse file with eval():\n%s' % (poName, msg))
        except Exception, msg:
            self.fail('Unknown error while parsing the po file %s:\n%s' \
                      % (poName, msg))

        try:
            tro = GNUTranslations(mo.getAsFile())
        except UnicodeDecodeError, msg:
            self.fail('UnicodeDecodeError in file %s:\n%s' % (poName, msg))
        except PoSyntaxError, msg:
            self.fail('PoSyntaxError: Invalid po data syntax in file %s:\n%s' \
                      % (poName, msg))

        domain = tro._info.get('domain', None)
        self.failUnless(domain, 'Po file %s has no domain!' % po)

        language_new = tro._info.get('language-code', None) # new way
        language_old = tro._info.get('language', None) # old way
        language = language_new or language_old

        self.failIf(language_old, 'The file %s has the old style language flag \
                                   set to %s. Please remove it!' \
                                  % (poName, language_old))

        self.failUnless(language, 'Po file %s has no language!' % po)

        fileLang = getLanguageFromPath(po)
        fileLang = canonizeLang(fileLang)
        language = canonizeLang(language)
        self.failUnless(fileLang == language,
            'The file %s has the wrong name or wrong language code. \
             expected: %s, got: %s' % \
             (poName, language, fileLang))


class TestMsg(ZopeTestCase.ZopeTestCase):
    poFile = None
    potFile = None

    def checkMsgExists(self,po,template):
        """Check that each existing message is translated and
           that there are no extra messages."""
        cmd='LC_ALL=C msgcmp --directory=%s/../i18n %s %s' % (
            _TESTS_PATH, po,template)
        status = commands.getstatusoutput(cmd)
        if status[0] != 0:
            return status
        return None

    def testMsgExists(self):
        """
        """
        po = self.poFile
        pot = self.potFile
        poName = po.split('/')[-1]
        failed = []
        res = self.checkMsgExists(po, pot)
        if res != None:
            output = res[1].split('\n')
            if len(output) > 10:
                output = output[:10]
                output.append('... <more errors>')
            output = '\n'.join(output)
            msg="Comparing '%s' with '%s' raised an error, \
                 exit code of msgcmp is: %s\n%s" % \
                (poName, pot ,res[0], output)
            self.fail(msg)

tests=[]
# FIXME : where is it coming from ?
if i18n_lib_here:
    for potFile in ['custom.pot', 'cpsdefault.pot']:
        class TestOnePOT(TestPOT):
            potFile = potFile
        tests.append(TestOnePOT)
    
        for poFile in getPoFiles():
            class TestOneMsg(TestMsg):
                poFile = poFile
                potFile = potFile
            tests.append(TestOneMsg)
    
            class TestOnePoFile(TestPoFile):
                poFile = poFile
                potFile = potFile
            tests.append(TestOnePoFile)


def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

