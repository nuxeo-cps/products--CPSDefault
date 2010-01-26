##parameters=key=None
#$Id: getVocabularyLocalAddressBook.py 49782 2006-10-20 17:48:54Z gracinet $

# This is to be called from a Select Widget on a folder document (Workspace,
# Section)

if key is not None:
    proxy = context[key] # can raise KeyError, is that expected if missing ?

DOC_META_TYPES = ['CPS Proxy Document',
                  'CPS Proxy Folderish Document',
                  'CPS Proxy BTree Folderish Document']

candidates = context.objectItems(DOC_META_TYPES)
return tuple((c, v.Title()) for c, v in candidates)

