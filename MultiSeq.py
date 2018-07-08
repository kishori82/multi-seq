from __future__ import division

__author__ = "Kishori M Konwar"
__copyright__ = "Copyright 2017, Multiseq"
__credits__ = [""]
__version__ = "1.0"
__maintainer__ = "Kishori M Konwar"
__status__ = "Release"

#from  libs.starcluster.test import  teststarcluster as sctest
#import sys

try:
     import sys, traceback, re, inspect, signal, shutil 
     from os import makedirs, sys, listdir, environ, path, _exit
     #from commands import getstatusoutput
     from optparse import OptionParser
     
     from libs.python_modules.utils import multiseq_utils
     from libs.python_modules.utils.utils import *
     from libs.python_modules.utils.multiseq_utils  import parse_command_line_parameters, eprintf, halt_process, exit_process, WorkflowLogger, generate_log_fp
     from libs.python_modules.utils.parse  import parse_multiseq_parameters, parse_parameter_file
     from libs.python_modules.pipeline.multiseq_pipeline import  print_to_stdout, no_status_updates
     from libs.python_modules.utils.sysutil import pathDelim
     from libs.python_modules.pipeline.multiseq import run_multiseq, get_parameter, read_pipeline_configuration
     from libs.python_modules.annotate import *

     from libs.python_modules.diagnostics.parameters import *

     from libs.python_modules.pipeline.sampledata import *
     from libs.python_modules.pipeline.jobscreator import Params
     from libs.python_modules.utils import globalcodes
except:
   print(""" Could not load some user defined  module functions""")
   print(""" Make sure your typed \"source Multiseqrc\" """)
   print("""\n""")
   print(traceback.print_exc(10))
   sys.exit(3)


cmd_folder = path.abspath(path.split(inspect.getfile( inspect.currentframe() ))[0])

PATHDELIM =  str(pathDelim())

multiseq_config = """config/multiseq_config.txt"""
multiseq_param_file = """multiseq_params.txt"""
multiseq_param = """config/""" + multiseq_param_file

script_info={}
script_info['brief_description'] = """A workflow script for creating Gene Expression Matrix for Drop-Seq  scRNA-Seq outptut"""
script_info['script_description'] = \
    """ This script starts the Multi-Seq pipeline run for Drop-Seq reads. It requires FASTQ files as input
    containing sequences to process, an output directory for results to be placed. It also requires the and 
    optionally configuration file
    configuration files, multiseq_config.txt and multiseq_params.txt in the config/ directory, 
    to be updated with the location of resources on your system.
    """
script_info['script_usage'] = []


usage=  sys.argv[0] + """ -i input_dir -o output_dir -p parameters.txt For more options:  ./Multiseq.py -h """

parser = None
def createParser():
    global parser
    parser = OptionParser(usage)
    parser.add_option("-b", "--barcodes", dest="barcodes", default=None, 
                      help='the FASTQ file with barcode reads [REQUIRED]')
    parser.add_option("-r", "--reads", dest="reads",
                      help='the FASTQ file with cDNA  reads [REQUIRED]')
    parser.add_option("-g", "--gene-annot", dest="geneannot",  default=None,
                      help='the gene annotation file [REQUIRED]')
    parser.add_option("-G", "--refgenome", dest="refgenome", default=None,
                      help='the FASTA file with reference genome [REQUIRED]')

    parser.add_option("-o", "--output_dir", dest="output_dir", default=None,  
                       help='the output dir to store results of various sample[REQUIRED]')

    parser.add_option("--refindexdir", dest="refindex_dir", default=None,
                      help='the dir for the reference genome index for aligner [REQUIRED]')
    parser.add_option("--refindexname", dest="refindex_name", default=None,
                      help='the name for the reference genome index for aligner [REQUIRED]')

    parser.add_option('-p','--parameter_fp', dest="parameter_fp",
                       help='path to the parameter file ')
    parser.add_option("-c", "--config_filer", dest="config_file",
                      help='pipeline_configuratin file [DEFAULT: \"Multiseq/multiseq_config.txt\"]')

    #ith out of order completion \ time-stamps in the \'workflow_log.txt\' 
    parser.add_option("-v", "--verbose", dest="verbose", type='int',  default=0,
                      help="print the underlying command on the stdout [0:command, 1:input  default:0]")
    
    parser.add_option("-s", "--sample", dest="sample",  default=None,
                      help="sample name [REQUIRED]" )
    



def valid_arguments(opts, args):
    """ checks if the supplied arguments are adequate """
    if (opts.barcodes and opts.reads and opts.output_dir and opts.geneannot and opts.refgenome):
       return True
    else:
       return False


def removeSuffix(sample_subset_in):
    sample_subset_out = []
    for sample_name in sample_subset_in:
       mod_name = re.sub('.(fasta|fas|fna|faa|gff|gbk|fa)$','',sample_name)
       sample_subset_out.append(mod_name)

    return sample_subset_out


def halt_on_invalid_input(input_output_list, filetypes, sample_subset):

    for samplePath in input_output_list.keys():
       sampleName =  path.basename(input_output_list[samplePath]) 

       ''' in the selected list'''
       if not sampleName in sample_subset:
          continue

       if filetypes[samplePath][0]=='UNKNOWN':
          eprintf("ERROR\tIncorrect input sample %s. Check for bad characters or format\n!", samplePath)
          return False

    return True
          

def sigint_handler(signum, frame):
    eprintf("Received TERMINATION signal\n")
    exit_process()

def main(argv):
    global parser
    (opts, args) = parser.parse_args()
    if not valid_arguments(opts, args):
       print(usage)
       sys.exit(0)

    eprintf("COMMAND : %s\n", sys.argv[0] + ' ' +  ' '.join(argv))
    # initialize the input directory or file

    barcodes = opts.barcodes
    reads = opts.reads
    refgeneanot = opts.geneannot
    refgenome = opts.refgenome
    refindex_dir = opts.refindex_dir
    refindex_name=opts.refindex_name
    sample_name = opts.sample

    output_dir = path.abspath(opts.output_dir)
    verbose = opts.verbose
    globalerrorlogger = WorkflowLogger(generate_log_fp(output_dir, basefile_name='global_errors_warnings'),
                                       open_mode='w')

    if opts.config_file:  #if provided with command line
       config_file = opts.config_file
    elif path.exists(multiseq_config):  #if the file exists in the current folder
       config_file=multiseq_config
    else:  # otherwise get it from config/ folder 
       config_file = cmd_folder + PATHDELIM + multiseq_config
    
    # try to load the parameter file    
    try:
       if opts.parameter_fp:   # if provided with command line
          parameter_fp= opts.parameter_fp
       elif path.exists(multiseq_param_file):  # if multiseq_params exists in current folder
          parameter_fp =  multiseq_param_file
       else:   # otherwise get it from config/ folder 
          parameter_fp = cmd_folder + PATHDELIM + multiseq_param
    except IOError:
        raise(IOError, "Can't open parameters file (%s). Does it exist? Do you have read access?" % opts.parameter_fp )

        
    if verbose:
        status_update_callback = print_to_stdout
    else:
        status_update_callback = no_status_updates

    
    command_line_params={}
    command_line_params['verbose']= opts.verbose

    if not path.exists(parameter_fp):
        eprintf("%-10s: No parameters file %s found!\n" %('WARNING', parameter_fp))
        eprintf("%-10s: Creating a parameters file %s found!\n" %('INFO', parameter_fp))
        create_multiseq_parameters(parameter_fp, cmd_folder)
    params=parse_multiseq_parameters(parameter_fp)
    parameter = Parameters()
    paramobj = Params(params)


    if not path.isfile(barcodes):
        eprintf("%-10s: File %s does not exist!\n" % ('WARNING', barcodes))
        halt_process(0)
    if not path.isfile(reads):
        eprintf("%-10s: File %s does not exist!\n" % ('WARNING', reads))
        halt_process(0)
    if not path.isfile(refgeneanot):
        eprintf("%-10s: File %s does not exist!\n" % ('WARNING', refgeneanot))
        halt_process(0)
    if not path.isfile(refgenome):
        eprintf("%-10s: File %s does not exist!\n" % ('WARNING', refgenome))
        halt_process(0)
    if not os.path.isdir(refindex_dir):
        eprintf("%-10s: Folder %s does not exist!\n" % ('WARNING', refindex_dir))
        halt_process(0)
    if not path.exists(opts.output_dir):
        eprintf("%-10s: Folder %s does not exist!\n", opts.output_dir)
        halt_process(1)


    #check the pipeline configuration
    if not path.exists(config_file):
        eprintf("%-10s: No config file %s found!\n" %('WARNING', config_file))
        eprintf("%-10s: Creating a config file %s!\n" %('INFO', config_file))
        if not environment_variables_defined("MULTISEQ_PATH"):
           eprintf("%-10s: shell variable %s not defined to generate config file %s!\n" %('INFO', 'MULTISEQ_PATH', config_file))
           sys.exit(0)

        status = create_multiseq_configuration(config_file, cmd_folder)
        if status[0]==1:
           eprintf("%s", status[1])
           halt_process(0)
    config_settings = read_pipeline_configuration(config_file, globalerrorlogger)

    #if not staticDiagnose(config_settings, params, logger = globalerrorlogger):
    #    eprintf("ERROR\tFailed to pass the test for required scripts and inputs before run\n")
    #    globalerrorlogger.printf("ERROR\tFailed to pass the test for required scripts and inputs before run\n")
    #    halt_process(0)

    samplesData = {}
    try:
         # load the sample information 
         print("RUNNING Multiseq version 1.0")

         s = SampleData()
         s.setParameter('PROTOCOL_NAME', "DROP-SEQ")
         s.setParameter('SEQ_TYPE', "cDNA")
         s.setParameter('ref_genome_sequences',refgenome)
         s.setParameter('ref_gene_annotations', refgeneanot)
         s.setParameter('refindex_dir', refindex_dir)
         s.setParameter('refindex_name', refindex_name)
         s.setParameter('sample_name', sample_name)
         s.setInputOutput(inputFiles=[barcodes, reads], output_dir=output_dir)
         s.prepareToRun()

         run_multiseq(
                   s,
                   globallogger=globalerrorlogger,
                   command_line_params=command_line_params,
                   params=params, config_settings=config_settings,
                   status_update_callback=status_update_callback
              )
    except:
       exit_process(str(traceback.format_exc(10)), logger= globalerrorlogger )


    
    eprintf("            ***********                \n")
    eprintf("INFO : FINISHED PROCESSING THE SAMPLES \n")
    eprintf("             THE END                   \n")
    eprintf("            ***********                \n")
    #eprintf(" EXIT CODE %s\n", globalcodes.exit_code)
    halt_process(0)

# the main function of multiseq
if __name__ == "__main__":
    createParser()
    main(sys.argv[1:])    
    

