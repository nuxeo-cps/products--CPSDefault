##parameters=
# $Id$
""" Sorting for display allowedContentTypes
    if allowed=0 return Searchable portaltype"""

from Products.CMFCore.utils import getToolByName
from zLOG import LOG, DEBUG

logKey = 'getSortedSubjects'

subjectVocabulary = getToolByName(context, 'portal_vocabularies').subject_voc
LOG(logKey, DEBUG, "subjectVocabulary = %s" % str(subjectVocabulary))


return subjectVocabulary
