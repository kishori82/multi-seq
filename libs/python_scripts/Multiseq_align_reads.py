try:
   import  sys, re, csv, traceback
   from os import path, _exit, rename

   import logging.handlers
   from optparse import OptionParser, OptionGroup

   from libs.python_modules.utils.Utility import sample_down_transform_sam

   from libs.python_modules.utils.sysutil import pathDelim
   from libs.python_modules.utils.multiseq_utils import fprintf, printf, eprintf,  exit_process
   from libs.python_modules.utils.sysutil import getstatusoutput


except:
     print """ Could not load some user defined  module functions"""
     print """ Make sure your typed 'source Multiseqsrc'"""
     print """ """
     print traceback.print_exc(10)
     sys.exit(3)

PATHDELIM=pathDelim()

usage = sys.argv[0] + """ -U reads -x refindex -p num_threads --aligner aligner -S samout -B bedout"""

parser = None
def createParser():
    global parser
    epilog = """This script is used for """

    epilog = re.sub(r'\s+',' ', epilog)

    parser = OptionParser(usage=usage, epilog=epilog)

    # Input options

    blast_group =  OptionGroup(parser, 'BLAST parameters')

    blast_group.add_option('-U', '--reads', dest='reads', default=None,
                           help='the reads in FASTQ to map [REQUIRED]')

    blast_group.add_option('-x', '--refindex', dest='refindex', default=None,
                           help='reference genome index location [REQUIRED]')

    blast_group.add_option('-p', '--num_threads', dest='num_threads', default='1', type='str',
                           help='number of BOWTIE2 threads')

    blast_group.add_option('--aligner', dest='aligner',  default=None, choices = ['bowtie2'],
                           help='aligner algorithm [REQUIRED]')

    blast_group.add_option('-S', '--samout', dest='samout', default=None,
                           help='SAM file output [REQUIRED]')

    blast_group.add_option('--q30filter', dest='q30filter', default=0,   action="store_true",
                           help='BED file output [REQUIRED]')

    parser.add_option_group(blast_group)


def main(argv, errorlogger = None, runcommand = None, runstatslogger = None):
    global parser

    options, args = parser.parse_args(argv)

    (code, message) =  _execute_bowtie2(options, logger = errorlogger)

    nameprefix = re.sub(r'.sam$', '', options.samout)

    _convert_to_bam(options.samout, nameprefix + ".bam")

    bedout = nameprefix + ".bed"
    bedout_sampledown = nameprefix + ".sample_down.bed"
    samout_sampledown = nameprefix + ".sample_down.sam"

    sample_down_transform_sam(options.samout, bedout, samout_sampledown, bedout_sampledown, 5000000, options.q30filter)


    if code != 0:
        a= '\nERROR\tCannot successfully execute\n'
        outputStr =  a

        eprintf(outputStr + "\n")

        if errorlogger:
           errorlogger.printf(outputStr +"\n")
        return code

    return 0

def  _convert_to_bam(options, bamout, logger = None):
    args= [ ]

    args.append( 'samtools' )
    args += [ "view -S -b"  ]
    args += [">", bamout]

    try:
       result = getstatusoutput(' '.join(args) )
    except:
       return (1, "Cannot execute samtools successfully")

    return (result[0], result[1])

def  _execute_bowtie2(options, logger = None):
    args= [ ]

    args.append( 'bowtie2' )
    args += [ "-p", options.num_threads ]
    args += ["-x", options.refindex]
    args += ["-U", options.reads]
    args += ["-S", options.samout]

    try:
       result = getstatusoutput(' '.join(args) )
    except:
       return (1, "Cannot execute BOWTIE2 successfully")

    return (result[0], result[1])



def Multiseq_align_reads(argv, extra_command = None, errorlogger = None, runstatslogger =None):
    if errorlogger != None:
       errorlogger.write("#STEP\tALIGN_READS\n")
    createParser()
    try:
       code = main(argv, errorlogger = errorlogger, runcommand= extra_command, runstatslogger = runstatslogger)
    except:
       #insert_error(4)
       return (0,'')

    return (0,'')

if __name__ == '__main__':
    createParser()
    main(sys.argv[1:])

