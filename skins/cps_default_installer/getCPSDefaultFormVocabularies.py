##parameters=
#$Id$
"""Return CPSDefault forms vocabularies."""

vocabularies = {
    'search_review_state_voc': {
        'type': 'CPS Method Vocabulary',
        'data': {'get_vocabulary_method': 'getVocabularySearchReviewState'
                 },
        },
    'search_portal_type_voc': {
        'type': 'CPS Method Vocabulary',
        'data': {'get_vocabulary_method': 'getVocabularySearchPortalType'
                 },
        },

    }

return vocabularies
