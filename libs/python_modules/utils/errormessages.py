#!/usr/bin/env python


"""Contains general error message for the RiboCensus """

try:
    from os import getenv, makedirs, path, remove
    import re, sys, os, traceback
except:
    print "Cannot load some modules"
    sys.exit(0)
   

class Configuration():

    knownErrors = {}
    def __init__(self):
        try:
            self.file = self.initializeErrorMessages()
        except IOError:
            print "ERROR : Cannot  initialize \"Configuration\" in file " + sys.argv[0]


    def isKnownError(self, errorid):
        """ Checks if the errorid is known or not"""
        _errorid = str(errorid)
        if _errorid in self.knownErrors:
            return True
        return False 

    def getErrorMessage(self, errorid):
        _errorid = str(errorid)
        if self.isKnownError(errorid):
           return self.knownErrors[_errorid]

        return self.knownErrors['0']


    def initializeErrorMessages(self):
        self.knownErrors = { 
             '0': """ Error occured but the reason is not known""" 
           }


if __name__=="__main__":
     v =  Configuration()
     print v.isKnownError('0')
     print v.isKnownError('1')
     print v.getErrorMessage('0')
