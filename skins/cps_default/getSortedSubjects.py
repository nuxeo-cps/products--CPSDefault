##parameters=
# $Id$
""" Sorting for display allowedContentTypes
    if allowed=0 return Searchable portaltype"""

from Products.CMFCore.utils import getToolByName

subjectVocabulary = getToolByName(context, 'portal_vocabularies').subject_voc

return subjectVocabulary
