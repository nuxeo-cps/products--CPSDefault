## Script (Python) "getDateStr"
##parameters=dt=None, fmt='medium'
# $Id$
""" return a string date using the current locale """

locale = context.Localizer.get_selected_language()
if not dt:
    return ''

# XXX this is temporary implementation
# XXX i18n should be handle with message catalogue fmt directly
formats={'short':{'en':'%m/%d/%Y',
                  'fr':'%d/%m/%Y',
                  },
         'medium':{'en':'%m/%d/%Y %H:%M',
                   'fr':'%d/%m/%Y %H:%M',
                     },
         'long':{'en':'%m/%d/%Y %H:%M:%S',
                 'fr':'%d/%m/%Y %H:%M:%S',
                 },
         }

if fmt not in formats.keys():
    fmt = 'long'

if locale in formats[fmt].keys():
    ret = dt.strftime(formats[fmt][locale])
else:
    ret = dt.aCommon()
    
return ret


