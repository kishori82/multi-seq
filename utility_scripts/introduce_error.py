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
     import os, re, gzip, traceback, random
     from os import makedirs, sys, remove, rename
     from sys import path
     from optparse import OptionParser

     from libs.python_modules.utils.utils import isFastaFile, isVregionFile, isMultiNodeFile
     from libs.python_modules.utils.multiseq_utils  import parse_command_line_parameters, fprintf
     from libs.python_modules.utils.sysutil import getstatusoutput, pathDelim, open_file
     from libs.python_modules.utils.fastareader  import FastaReader
     from libs.python_modules.utils.errorcodes import error_message, get_error_list, insert_error
except:
     print """ Could not load some user defined  module functions"""
     print """ Make sure your typed 'source RiboCensusrc'"""
     print """ """
     print traceback.print_exc(10)
     sys.exit(3)

PATHDELIM = pathDelim()



usage= sys.argv[0] + """ -i file.fna  -o output -e p"""

parser = None
def createParser():
    global parser
    epilog = """ """

    epilog = re.sub(r'[ \t\f\v]+',' ', epilog)

    parser = OptionParser(usage=usage, epilog=epilog)

    parser.add_option("-i", "--input_file", dest="input_fasta",
                      help='the input fasta filename [REQUIRED]')
    parser.add_option("-o", "--output_file", dest="output_fasta",
                      help='the output fasta filename [REQUIRED]')
    parser.add_option("-e", "--error", dest="error", type='float', default =0.0,
                      help='percentage of error')
    


def valid_arguments(opts, args):
    state = True
    if opts.input_fasta == None :
        print 'ERROR: Missing input fasta file'
        state = False

    if opts.output_fasta == None :
        print 'ERROR: Missing output fasta file'
        state = False

    return state



class FastaRecord(object):
    def __init__(self, name, sequence):
        self.name = name
        self.sequence = sequence

#    return FastaRecord(title, sequence)

def read_fasta_records(input_file):
    records = []
    sequence=""
    name=""
    while 1:
         line = input_file.readline()
         if line == "": 
            if sequence!="" and name!="":
               records.append(FastaRecord(name, sequence))
            return  records

         if line=='\n':
            continue

         line = line.rstrip()
         if  line.startswith(">") :
            if sequence!="" and name!="":
               records.append(FastaRecord(name, sequence))

            name = line.rstrip()
            sequence =""
         else:
            sequence = sequence + line.rstrip()
    return records

        

def main(argv, errorlogger = None, runstatslogger = None): 
    global parser
    (opts, args) = parser.parse_args(argv)

    if not valid_arguments(opts, args):
       print usage
       sys.exit(0)

    random.seed(a=1)
    outfile = open(opts.output_fasta, 'w') 

    fastareader= FastaReader(opts.input_fasta)
    """ process one fasta sequence at a time """
    mutate = ['A', 'T', 'C', 'G']
    lengths_str=""

    eff_rate = opts.error*1.25
    for record in fastareader:
        seqname = record.name
        seq = record.sequence

        nseq = list(seq)
        for i in range(0, len(seq)):
           if random.random() < eff_rate:
                nseq[i] =  random.choice(mutate)
           else:
                nseq[i] = seq[i]

        fprintf(outfile, "%s\n", seqname)
        fprintf(outfile, "%s\n", ''.join(nseq))

    outfile.close()


# the main function of metapaths
if __name__ == "__main__":
    createParser()
    main(sys.argv[1:])

