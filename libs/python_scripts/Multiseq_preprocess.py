#!/usr/bin/python
# File created on 27 Jan 2012.
from __future__ import division

try:
     import os, re, gzip, traceback
     from os import makedirs, sys, remove, rename
     from sys import path
     from optparse import OptionParser

     from libs.python_modules.utils.Utility import transform_refgene, reform_barcode_fastq
     from libs.python_modules.utils.multiseq_utils  import parse_command_line_parameters, fprintf
     from libs.python_modules.utils.sysutil import getstatusoutput, pathDelim, open_file
     from libs.python_modules.utils.errorcodes import error_message, get_error_list, insert_error
except:
     print """ Could not load some user defined  module functions"""
     print """ Make sure your typed 'source RiboCensusrc'"""
     print """ """
     print traceback.print_exc(10)
     sys.exit(3)

PATHDELIM = pathDelim()



usage= sys.argv[0] + """ -i file.fna  --min_length N1 ---max_length N2 -log_file logfile.log """ +\
              """ -o outfasta  [ -M map file ]"""

parser = None
def createParser():
    global parser
    epilog = """
This script creates the necessary files from the gene annotations and the barcode read files
   1. bed files
   2. read transformed bed files
"""

    epilog = re.sub(r'[ \t\f\v]+',' ', epilog)

    parser = OptionParser(usage=usage, epilog=epilog)

    parser.add_option("-g", "--gene-annotations", dest="gene_annotations",
                      help='the gene annotation [REQUIRED]')
    parser.add_option("-b", "--barcode-reads", dest="barcode_reads",
                      help='the FASTQ file with barcode reads [REQUIRED]')

    parser.add_option("-o", "--output-folder", dest="output_folder",
                      help='the output folder  [REQUIRED]')
    parser.add_option("-s", "--sample-name", dest="sample_name",
                      help='sample name  [REQUIRED]')

    


def valid_arguments(opts, args):
    state = True
    if opts.gene_annotations == None :
        print 'ERROR: Missing gene annotation file'
        state = False

    if opts.barcode_reads == None :
        print 'ERROR: Missing barcode read FASTQ file'
        state = False

    return state


# the main function

def main(argv, errorlogger = None, runstatslogger = None): 
    global parser
    (opts, args) = parser.parse_args(argv)

    if not valid_arguments(opts, args):
       print usage
       sys.exit(0)

    gene_annotations = opts.gene_annotations
    barcode_reads = opts.barcode_reads
    output_folder = opts.output_folder
    sample_name = opts.sample_name

    transform_refgene(gene_annotations, 400, output_folder + PATHDELIM + sample_name)

    barcodes_txt = output_folder + PATHDELIM + sample_name + ".barcodes.txt"
    reform_barcode_fastq(barcode_reads, barcodes_txt, 12, 8)

    barcodes_sorted_txt = output_folder + PATHDELIM + sample_name + ".barcodes.sorted.txt"
    cmd_barcodes_sort = 'sort -k 1,1 %s > %s' % (barcodes_txt, barcodes_sorted_txt)
    try:
       result = getstatusoutput(cmd_barcodes_sort)
    except:
       return (1, "Cannot sort barcodes successfully")



def Multiseq_preprocess(argv, errorlogger = None, runstatslogger = None):
    createParser()
    try:
       main(argv, errorlogger = errorlogger, runstatslogger = runstatslogger) 
    except:
       insert_error(1)
       return (1,'')

    return (0,'')

# the main function of metapaths
if __name__ == "__main__":
    createParser()
    main(sys.argv[1:])

