#!/usr/bin/env python




"""Contains general utility code for the multiseq project"""

try:
    from shutil import rmtree
    from StringIO import StringIO
    from os import getenv, makedirs, path, remove
    from operator import itemgetter
    from os.path import abspath, exists, dirname, join, isdir
    from collections import defaultdict
    from optparse import make_option
    import re, sys, os, traceback
except:
    print "Cannot load some modules"
    sys.exit(0)
   

class Parameters():
    """Contains the acceptable values of the configuration 
    If you want to add any new module, you will have to add the new algorithm 
    this configuration file."""

    acceptableValues = {}


    def __init__(self):
      pass


    def isValid1(self, key1):
        if key1 in self.acceptableValues:
            return True
        return False 

    def getValidValues1(self, key1):
        if self.isValid1(key1):
           return self.acceptableValues.keys()
        return []


    def isValid2(self, key1, key2):
        if not self.isValid1(key1):
            return False

        if not key2 in  self.acceptableValues[key1]:
            return False

        return True 

    def getValidValues2(self, key1, key2):
        if self.isValid2(key1, key2):
           return self.acceptableValues[key1][key2].keys()
        return []

    def getAcceptableParameters(self):
        return self.acceptableValues 


    def getRunSteps(self, activeOnly = False):
        steps = []
        for step in self.acceptableValues['multiseq_steps']:
            if activeOnly==False  or self.acceptableValues['multiseq_steps'][step] in [ 'redo', 'yes' ]:
               steps.append(step)
        return steps





if __name__=="__main__":
     v =  Parameters()
