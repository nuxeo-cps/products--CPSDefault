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
from Products.ExternalMethod.ExternalMethod import ExternalMethod

from Products.GenericSetup.utils import _resolveDottedName

from Products.CMFCore.utils import SimpleItemWithProperties
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

     replay_external_method = {'id': 'replay_profiles',
                               'description': "Upgrade the configuration "
                               "that was specified in site creation form",
                               'module': 'CPSDefault.replay_meta_profiles',
                               'function': 'replay'}

     def __init__(self, site=None):
         if site is not None:
             self.site = site

     def getUndisclosedParams(self):
          """Give the list of sensitive property values not to be displayed.

          Used by replay external method."""

          res = []
          for m_id, m_profile in self.meta_profiles.items():
               params = m_profile.get('parameters', {})
               res.extend((m_id + '-' + pid
                           for pid in params.get('undisclosed', ())))
          return res

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

                 # properties
                 wanted_props = params.get('properties')
                 if wanted_props is not None:
                     info['parameters'] = [
                         prop for prop in deepcopy(klass._properties)
                         if prop['id'] in wanted_props]
                     # prefixing to avoid collision
                     for prop in info['parameters']:
                         prop['id'] = '%s-%s' % (m_id, prop['id'])
                 else:
                     info['parameters'] = []

                 # other attributes; TODO: use possibly existing Z3 schema
                 for attr in params.get('attributes', []):
                     info['parameters'].append(
                         {'id': "%s-%s" % (m_id, attr),
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

          d = self.replay_external_method
          if not d:
               return

          meth = ExternalMethod(d['id'], d['description'],
                                d['module'], d['function'])
          self.site._setObject(d['id'], meth)

     def _importMetaProfile(self, m_profile, steps=(), excluded_steps=()):
          """ Import a single meta profile. """

          setup_tool = getattr(self, 'setup_tool', None)
          if setup_tool is None:
              setup_tool = self.site.portal_setup

          for extension_id in m_profile['extensions']:
            logger.info("Pointing to extension profile %r", extension_id)
            context = 'profile-%s' % extension_id
            if not steps:
                 setup_tool.runAllImportStepsFromProfile(
                      context, excluded_steps=excluded_steps)
            else:
                 for step in steps:
                      if step not in excluded_steps:
                           setup_tool.runImportStepFromProfile(context, step)

     def _applyParameters(self, prefix, params, **kw):
          """Apply user input parameters to site.

          At this time, these are properties on a single object.
          Keys in params and kw must be prefixed with prefix and a dash.
          """

          if not 'class' in params:
              return
          klass = _resolveDottedName(params.get('class'))

          props = params.get('properties', ())

          pref_len = len(prefix) + 1
          try:
               obj = self.site.unrestrictedTraverse(params['rpath'])
          except (KeyError, AttributeError):
               # see #2263
               logger.error("Could not lookup object %r "
                            "even after profiles loading.", params['rpath'])
               return

          if props:
              prop_dict = dict((key[pref_len:], value)
                               for key, value in kw.items()
                               if key.startswith(prefix) and \
                               key[pref_len:] in props and value)
              obj.manage_changeProperties(**prop_dict)

          attrs = params.get('attributes', ())
          for attr in attrs:
              value = kw.get('%s-%s' % (prefix, attr), '')
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

             try:
                  obj = self.site.unrestrictedTraverse(params['rpath'])
             except (KeyError, AttributeError):
                  logger.info(
                       "Could not lookup object at %s for parameter "
                       "snapshot. This may be normal.")
                  continue

             attrs = params.get('properties', ()) + params.get('attributes',
                                                               ())
             for attr in attrs:
                 snapshot['%s-%s' % (m_id, attr)] = getattr(aq_base(obj),
                                                                 attr)

         return snapshot

     def listProfiles(self):
          """List all profile identifiers in order, starting from base profile.
          """
          res = [self.base_profile]
          for m_id in self.metas_order:
               res.extend(self.meta_profiles[m_id]['extensions'])
          return res

     def importMetaProfiles(self, **kw):
          """ Import meta profiles."""

          requested_metas = kw.get('requested_metas', ())
          imported_metas = []

          setup_tool = self.site.portal_setup

          if getattr(self.site, 'meta_profiles', None) is None:
              self.site.manage_addProperty('meta_profiles', [], 'lines')

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

                    self._applyParameters(m_id, m_profile.get('parameters',{}),
                                              **kw)
                    if after is not None:
                         after(self.site, **kw)

                    cat = m_profile.get('upgrade_category')
                    if cat is not None:
                         setup_tool._setCurrentVersion(cat, None)

          self_dotted_name = '.'.join((self.__module__,
                                       self.__class__.__name__))
          self.site.manage_changeProperties(meta_profiles=imported_metas)
          # no need for this one to be user managed ever -> simple attr
          self.site.configurator=self_dotted_name

     def replayMetaProfiles(self, steps=(), excluded_steps=(),
                            with_hooks=False):
         """ Replay meta profiles but saves parameters.

         If limited to some import steps, no hooks will be applied
         """

         tool = self.site.portal_setup
         if steps:
              with_hooks = False
              full = False
         else:
              full = True

         m_ids = self.site.meta_profiles
         snapshot = self.paramsSnapshot(m_ids)

         logger.info("Pointing to base profile %r", self.base_profile)
         if full:
              tool.reinstallProfile('profile-%s' % self.base_profile,
                                    excluded_steps=excluded_steps)
         else:
              context = 'profile-%s' % self.base_profile
              for step in steps:
                   if step not in excluded_steps:
                        tool.runImportStepFromProfile(context, step,
                                                      purge_old=True)

         for m_id in m_ids:
             m_profile = self.meta_profiles[m_id]

             before = m_profile.get('before_import')
             if with_hooks and before is not None:
                 before(self.site, **snapshot)

             self._importMetaProfile(m_profile, steps=steps,
                                     excluded_steps=excluded_steps)
             self._applyParameters(m_id, m_profile.get('parameters', ()),
                                   **snapshot)

             after = m_profile.get('after_import')
             if with_hooks and after is not None:
                 after(self.site, **snapshot)

         if getattr(self.site, 'meta_profiles', None) is None:
              self.site.manage_addProperty('meta_profiles', [], 'lines')
         self.site.manage_changeProperties(meta_profiles=m_ids)
         self_dotted_name = '.'.join((self.__module__,
                                      self.__class__.__name__))
         self.site.configurator=self_dotted_name


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

     The Fake Setup Tool strongly enforces the deprecation of the
     setImportContext method
     >>> try: tool.setImportContext('profile-Spam:egg')
     ... except NotImplementedError: print 'ok, it raised'
     ok, it raised
     >>> tool.runAllImportStepsFromProfile('profile-Spam:egg', purge_old=True)
     Purged and imported 'profile-Spam:egg'
     >>> tool.runAllImportStepsFromProfile('profile-Spam:ham', purge_old=False)
     Imported 'profile-Spam:ham'
     >>> tool.runImportStepFromProfile('profile-Foo:bar', 'layouts',
     ...                               purge_old=False)
     Import step profile 'profile-Foo:bar', step 'layouts'
     >>> tool.runImportStepFromProfile('profile-Foo:bar', 'layouts',
     ...                               purge_old=True)
     Purge and import step profile 'profile-Foo:bar', step 'layouts'
     """

     _properties = CPSSetupTool._properties + (
         {'id': 'witness', 'type': int},)

     def setImportContext(self, *a, **kw):
          """This is deprecated in current setup tool API."""
          raise NotImplementedError

     def runAllImportStepsFromProfile(self, profile_id,
                                      purge_old=False, excluded_steps=()):
         self.witness = 0
         if excluded_steps:
              print 'Excluded steps: %r' % excluded_steps
         msg = purge_old and "Purged and imported " or "Imported "
         print msg + '%r' % profile_id

     def runImportStepFromProfile(self, profile_id, step_id, purge_old=False):
          """This uses the mock of the older setImportContext API.

          Not a problem for a mock object, and we don't have to update the
          tests that depend on it.
          """
          msg = purge_old and "Purge and import step " or "Import step "
          print msg + 'profile %r, step %r' % (profile_id, step_id)

     def reinstallProfile(self, context_id, **kw):
         pass



class SampleTool(SimpleItemWithProperties):
     """A sample object for the doctest."""

     def __init__(self, id, **kw):
          self._setId(id)

     _properties = SimpleItemWithProperties._properties + (
          {'id': 'ldap_bind_dn', 'mode': 'w',
           'type': 'string', 'label': 'Sample tool bind'},
          {'id': 'pass', 'type': 'string', 'label': 'PASS'},
          )
     
