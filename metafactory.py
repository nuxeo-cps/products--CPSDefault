# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Author: G. Racinet <gracinet@nuxeo.com>
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
"""CPS Site meta factory."""

from copy import deepcopy
import logging

from Acquisition import aq_base

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.GenericSetup.utils import _resolveDottedName
from Products.CPSCore.setuptool import CPSSetupTool
from Products.CPSDefault.factory import CPSSiteConfigurator

logger = logging.getLogger('CPSDefault.metafactory')

class CPSSiteMetaConfigurator(CPSSiteConfigurator):
     """ A configurator that manages a bunch of extension profiles.

     Uses the concept of meta_profiles: a list of profiles, with parameters
     exposed at creation form time, and set after loading all the profiles.

     Concrete utilisations should subclass to set 'meta_profiles' and
     'metas_order' attributes.

     See doc/developer/metafactory.txt for examples.
     """


     addForm = PageTemplateFile('zmi/siteMetaAddForm', globals())

     meta_profiles = {}
     metas_order = ()

     base_profile = 'CPSDefault:default'
     form_heading = ''
     post_action = ''

     def __init__(self, site=None):
         if site is not None:
             self.site = site

     def prepareOptions(self, options):
         """Add metaprofiles. """

         CPSSiteConfigurator.prepareOptions(self, options)
         opt_metas = []
         for m_id in self.metas_order:
             m_profile = self.meta_profiles[m_id]
             optional = m_profile.get('optional', False)
             if optional or m_profile.get('parameters'):
                 info = {'id': m_id,
                         'title': m_profile['title'],
                         'optional': optional,
                         }
                 opt_metas.append(info) # info will be modified in-place
                 params = m_profile.get('parameters')

                 if params is None:
                     continue
                 try:
                      klass = _resolveDottedName(params['class'])
                 except (ImportError, AttributeError), err:
                      info['disabled'] = 'Error: %s' % err
                      continue

                 classname = klass.__name__

                 # properties
                 wanted_props = params.get('properties')
                 if wanted_props is not None:
                     info['parameters'] = [
                         prop for prop in deepcopy(klass._properties)
                         if prop['id'] in wanted_props]
                     # prefixing to avoid collision
                     for prop in info['parameters']:
                         prop['id'] = '%s-%s' % (classname, prop['id'])
                 else:
                     info['parameters'] = []

                 # other attributes; TODO: use possibly existing Z3 schema
                 for attr in params.get('attributes', []):
                     info['parameters'].append(
                         {'id': "%s-%s" % (classname, attr),
                          'label': attr})

         options['meta_profiles'] = opt_metas
         options['form_heading'] = getattr(self, 'form_heading')
         options['post_action'] = getattr(self, 'post_action')

     def createAdministrator(self, *args):
          """ Do nothing. """
          pass

     def parseForm(self, **kw):
          # Required by password but will be discarded
          kw['manager_id'] = 'nonvoid'
          kw['password'] = 'nonvoid'
          kw['password_confirm'] = 'nonvoid'
          CPSSiteConfigurator.parseForm(self, **kw)

     def afterImport(self, **kw):
          """Take care of meta_profiles.

          Called after base profiles and mandatory extensions imports."""

          CPSSiteConfigurator.afterImport(self, **kw)
          self.importMetaProfiles(**kw)

     def _importMetaProfile(self, m_profile):
          """ Import a single meta profile. """

          setup_tool = getattr(self, 'setup_tool', None)
          if setup_tool is None:
              setup_tool = self.site.portal_setup
          for extension_id in m_profile['extensions']:
            setup_tool.setImportContext('profile-%s' % extension_id)
            setup_tool.runAllImportSteps()

     def _applyParameters(self, params, **kw):
          """Apply user input parameters to site.

          At this time, these are properties on a single object. """

          if not 'class' in params:
              return
          klass = _resolveDottedName(params.get('class'))

          props = params.get('properties', ())

          classname = klass.__name__
          cl_len = len(classname) + 1
          obj = self.site.unrestrictedTraverse(params['rpath'])
          if props:
              prop_dict = dict((key[cl_len:], value)
                               for key, value in kw.items()
                               if key.startswith(classname) and \
                               key[cl_len:] in props and value)
              obj.manage_changeProperties(**prop_dict)

          attrs = params.get('attributes', ())
          for attr in attrs:
              value = kw.get('%s-%s' % (classname, attr), '')
              if value:
                  setattr(obj, attr, value)

     def paramsSnapshot(self, metas):
         """Read existing values of parameters associated to a meta.

         provides them in a dict ready to be used by _applyParameters
         """

         snapshot = {}
         for m_id in metas:
             m_profile = self.meta_profiles[m_id]
             params = m_profile.get('parameters')
             if not params:
                 continue

             klass = _resolveDottedName(params.get('class'))
             classname = klass.__name__

             obj = self.site.unrestrictedTraverse(params['rpath'])

             attrs = params.get('properties', ()) + params.get('attributes',
                                                               ())
             for attr in attrs:
                 snapshot['%s-%s' % (classname, attr)] = getattr(aq_base(obj),
                                                                 attr)

         return snapshot


     def importMetaProfiles(self, **kw):
          """ Import meta profiles."""

          requested_metas = kw.get('requested_metas', ())
          imported_metas = []

          if getattr(self.site, 'meta_profiles', None) is None:
              self.site.manage_addProperty('meta_profiles', [], 'tokens')

          for m_id in self.metas_order:
               m_profile = self.meta_profiles[m_id]
               if m_id in requested_metas or not m_profile.get('optional',
                                                               False):
                    before = m_profile.get('before_import')
                    after = m_profile.get('after_import')

                    if before is not None:
                         before(self.site, **kw)
                    self._importMetaProfile(m_profile)
                    imported_metas.append(m_id)

                    self._applyParameters(m_profile.get('parameters',{}),
                                              **kw)
                    if after is not None:
                         after(self.site, **kw)

          self.site.manage_changeProperties(meta_profiles=imported_metas)

     def replayMetaProfiles(self, with_hooks=False):
         """ Replay meta profiles but saves parameters."""

         m_ids = self.site.meta_profiles
         snapshot = self.paramsSnapshot(m_ids)
         for m_id in m_ids:
             m_profile = self.meta_profiles[m_id]

             before = m_profile.get('before_import')
             if with_hooks and before is not None:
                 before(self.site, **snapshot)

             self._importMetaProfile(m_profile)
             self._applyParameters(m_profile.get('parameters', ()), **snapshot)

             after = m_profile.get('after_import')
             if with_hooks and after is not None:
                 after(self.site, **snapshot)


     def addConfiguredSite(self, dispatcher, site_id, **kw):
          """Add a CPS site according to meta_profiles selected in form."""

          CPSSiteConfigurator.addConfiguredSite(self, dispatcher,
                                               site_id, self.base_profile, **kw)



_cpsconfigurator = CPSSiteMetaConfigurator()

# GR: straight from CPSDefault.factory
# Just do the same with your subclass
# Do the following dance because bound methods don't play well with
# constructors registered for products.

def addConfiguredMetaSiteForm(dispatcher):
    """Form to add a CPS Site from ZMI.
    """
    return _cpsconfigurator.addConfiguredSiteForm(dispatcher)

def addConfiguredMetaSite(dispatcher, REQUEST=None, **kw):
    """Add a CPSSite according to profile and extensions.
    """
    if REQUEST is not None:
        kw.update(REQUEST.form)
    return _cpsconfigurator.addConfiguredSite(dispatcher, REQUEST=REQUEST, **kw)

class FakeSetupTool(CPSSetupTool):
     """For tests and examples.

     >>> tool = FakeSetupTool()
     >>> tool.setImportContext('profile-Spam:egg')
     Pointing at Spam:egg
     >>> tool.runAllImportSteps()
     Imported
     """

     _properties = CPSSetupTool._properties + (
         {'id': 'witness', 'type': int},)

     def setImportContext(self, context_str):
          print "Pointing at %s" % context_str[len("profile-"):]

     def runAllImportSteps(self):
         self.witness = 0
         print "Imported"
