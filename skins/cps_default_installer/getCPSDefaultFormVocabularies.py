##parameters=
#$Id$
"""Return CPSDefault forms vocabularies."""

vocabularies = {
    'review_state_voc': {
        'type': 'CPS Vocabulary',
        'data': {'tuples': (('work', 'Work', 'label_work'),
                            ('pending', 'Pending', 'label_pending'),
                            ('published', 'Published', 'label_published'),
                            )},
        },

    }

return vocabularies
