#!/usr/bin/python
# File created on 27 Jan 2012.
from __future__ import division

__author__ = "Kishori M Konwar"
__copyright__ = "Copyright 2017, RiboCensus"
__credits__ = ["r"]
__version__ = "1.0"
__maintainer__ = "Kishori M Konwar"
__status__ = "Release"

try:
     import os, re, sys, traceback
     from os import makedirs, sys, remove, rename
     from sys import path
     from optparse import OptionParser
except:
     print """ Could not load some user defined  module functions"""
     print """ Make sure your typed 'source RiboCensusrc'"""
     print """ """
     print traceback.print_exc(10)
     sys.exit(3)

usage= sys.argv[0] + """ -n v regions   -o outfasta """

parser = None
def createParser():
    global parser
    epilog = """ This script computes the stats for similarity of OTU wrt the number of v region matche"""

    epilog = re.sub(r'[ \t\f\v]+',' ', epilog)

    parser = OptionParser(usage=usage, epilog=epilog)
    parser.add_option("-n", "--min_vregions", type='int', dest="min_vregions", default=3,
                      help='minimum number of vregions')
    parser.add_option("-o", "--output", dest="output_file",  help='the output file')
    



def filter_sequence(sequence):
   if isAminoAcidSequence(sequence):
       return sequence

   return  longest_sequence

def completeSequences():

    vpatt=re.compile(r'>.+_(\d+)_V[\d][.]{3}')

    completeSeqs={}
    counts = {}
    for V in [ "V1", "V2", "V3", "V4", "V5", "V6",  "V7", "V8", "V9" ]:
        with open("combined." + V + ".clstr", 'r') as fin:
          for  line in fin:
             res = vpatt.search(line)
             if res:
                 num=  res.group(1)
                 if not num in counts:
                    counts[num] = 0
                 counts[num] += 1

    for key, value in counts.iteritems():
      if value == 9:
         completeSeqs[key] = True
    return completeSeqs

def read_clusters(complete_seqs, V):
   cpatt=re.compile(r'^>Cluster')
   vpatt=re.compile(r'>.+_(\d+)_V[\d][.]{3}')
   clusters =[]
   group=[]

   with open("combined." + V + ".clstr", 'r') as fin:
     for  line in fin:
       cres = cpatt.search(line)
       if cres:
          if len(group)>=2:
             clusters.append(group)
          group=[]
 
       vres = vpatt.search(line)
       if vres:
           num=  vres.group(1)
           group.append(num)
   return clusters
       

def main(argv, errorlogger = None, runstatslogger = None): 
    global parser
    (opts, args) = parser.parse_args(argv)

    complete_seqs = completeSequences()
    matches = {}
    clusters = {}
    for V in [ "V1", "V2", "V3", "V4", "V5", "V6",  "V7", "V8", "V9" ]:
        clusters[V]=read_clusters(complete_seqs, V)
        for cluster in clusters[V]:
           l=len(cluster)
           for i in range(0, l-1):
              for j in range(i+1, l):
                 if cluster[i] > cluster[j]:
                    a = cluster[i] 
                    b = cluster[j]
                 else:
                    b = cluster[i] 
                    a = cluster[j]

                 if not a in matches:
                    matches[a] = {}

                 if not b in matches[a]:
                    matches[a][b] = 0

                 matches[a][b] += 1

    N = 0
    print "Num sequences : ", len(complete_seqs)
    print "Num possible pairs     : ", int(len(complete_seqs)*(len(complete_seqs) -1 )/2)

    counts = [0 for x in range(0, 9) ]

    for a in matches:
       for b in matches[a]:
           counts[matches[a][b]-1] += 1
           N += 1
     
    print "Num of at least one V regions matching pairs     : ", N

    for i in range(0, 9):
       print "Num matches in " ,i+1, "V-regions: ", "\t",  counts[i],  "\t%.2f%%" %(counts[i]/N*100)

# the main function of metapaths
if __name__ == "__main__":
    createParser()
    main(sys.argv[1:])

