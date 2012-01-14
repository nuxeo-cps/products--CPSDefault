from Products.CPSDefault.voidresponses import ImsResponseHandler

def make(self):
    ImsResponseHandler.enableIfModifiedSince(self)
