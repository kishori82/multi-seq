#!/usr/bin/python



try:
   from optparse import make_option
   from os import makedirs,  path, listdir, remove, rename, _exit
   import os, sys, errno, shutil, re
   from glob import glob
   from datetime import date
   #from multiseq_utils  import pars[s._command_line_parameters

   from libs.python_modules.utils.sysutil import getstatusoutput, pathDelim
   #from libs.python_modules.utils.utils import *, hasInput, createFolderIfNotFound
   from libs.python_modules.utils.utils import *
   from libs.python_modules.utils.parse  import parse_multiseq_parameters
   from libs.python_modules.pipeline.multiseq_pipeline import  execute_tasks

   from libs.python_modules.utils.multiseq_utils import exit_process, WorkflowLogger, generate_log_fp

   from libs.python_modules.pipeline.sampledata import *
   from libs.python_modules.pipeline.jobscreator import *
   from libs.python_modules.pipeline.commands import *
   import libs.python_scripts

except:
     print """ Could not load some user defined  module functions"""
     print """ Make sure your typed \"source RiboCensusrc\""""
     print """ """
     print traceback.print_exc(10)
     sys.exit(3)



PATHDELIM = pathDelim()


def copyFile(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

def dry_run_status( commands ):
    for command in commands:
        printf("%s", command[0])
        if command[4] == True:
           printf("%s", " Required")
        else:
           printf("%s", " Not Required")
    printf("\n")


def get_refdb_name( dbstring ):
    dbstring = dbstring.rstrip()
    dbstring = dbstring.lstrip()
    dbstring = dbstring.lower() 
    return dbstring



#gets the parameter value from a category as.ecified in the 
# parameter file
def get_parameter(params, category, field, default = None):
    if params == None:
      return default

    if category in params:
        if field in params[category]:
            return params[category][field]
        else:
            return default
    return default


# parameter file
def get_make_parameter(params,category, field, default = False):
    if category in params:
        if field in params[category]:
            return params[category][field]
        else:
            return default
    return default

def get_pipeline_steps(steps_log_file):
    try:
       logfile = open(steps_log_file, 'r')
    except IOError:
       eprintf("Did not find %s!\n", logfile) 
       eprintf("Try running in \'complete\' run-type\n")
    else:
       lines = logfile.readlines()

    pipeline_steps = None
    return pipeline_steps


def write_run_parameters_file(fileName, parameters):
    try:
       paramFile = open(fileName, 'w')
    except IOError:
       eprintf("Cannot write run parameters to file %s!\n", fileName)
       exit_process("Cannot write run parameters to file %s" %(fileName) )

#       16s_rRNA      {'min_identity': '40', 'max_evalue': '0.000001', 'min_bitscore': '06', 'refdbs': 'silva_104_rep_set,greengenes_db_DW'}
    paramFile.write("\nRun Date : " + str(date.today()) + " \n")

    paramFile.write("\n\nNucleotide Quality Control parameters[s.n")
    paramFile.write( "  min length" + "\t" + str(parameters['quality_control']['min_length']) + "\n")

    paramFile.write("\n\nORF prediction parameters[s.n")
    paramFile.write( "  min length" + "\t" + str(parameters['orf_prediction']['min_length']) + "\n")
    paramFile.write( "  algorithm" + "\t" + str(parameters['orf_prediction']['algorithm']) + "\n")


    paramFile.write("\n\nAmino acid quality control and annotation parameters[s.n")
    paramFile.write( "  min bit score" + "\t" + str(parameters['annotation']['min_score']) + "\n")
    paramFile.write( "  min seq length" + "\t" + str(parameters['annotation']['min_length']) + "\n")
    paramFile.write( "  annotation reference dbs" + "\t" + str(parameters['annotation']['dbs']) + "\n")
    paramFile.write( "  min BSR" + "\t" + str(parameters['annotation']['min_bsr']) + "\n")
    paramFile.write( "  max evalue" + "\t" + str(parameters['annotation']['max_evalue']) + "\n")

    paramFile.write("\n\nPathway Tools parameters[s.n")
    paramFile.write( "  taxonomic pruning " + "\t" + str(parameters['ptools_settings']['taxonomic_pruning']) + "\n")

    paramFile.write("\n\nrRNA search/match parameters[s.n")
    paramFile.write( "  min identity" + "\t" + str(parameters['rRNA']['min_identity']) + "\n")
    paramFile.write( "  max evalue" + "\t" + str(parameters['rRNA']['max_evalue']) + "\n")
    paramFile.write( "  rRNA reference dbs" + "\t" + str(parameters['rRNA']['refdbs']) + "\n")

    paramFile.close()


# checks if the necessary files, directories  and executables really exis.or not
def check_config_settings(config_settings, file, globalerrorlogger = None):
   essentialItems= ['MULTISEQ_PATH', 'EXECUTABLES_DIR', 'RESOURCES_DIR']
   missingItems = []

   for key, value in  config_settings.items():
      # these are not files or executables

      if key in ['NUM_CPUS']:
        continue

      # make sure  RiboCensus directory is present
      if key in ['MULTISEQ_PATH' ]:
         if not path.isdir( config_settings[key]) :
            eprintf("ERROR: Path for \"%s\" is NOT set properly (or missing) in configuration file \"%s\"\n", key, file)  
            eprintf("ERROR: 1.Currently it is set to \"%s\"\n",  config_settings[key] )  

            if globalerrorlogger!=None:
               globalerrorlogger.write("ERROR\tPath for \"%s\" is NOT set properly (or missing) in configuration file \"%s\"\n"  %(key, file))  
               globalerrorlogger.write("       Currently it is set to \"%s\"\n" %(config_settings[key] )  )
            missingItems.append(key) 
         continue

      # make sure EXECUTABLES_DIR directories are present
      if key in [ 'EXECUTABLES_DIR']:
         if not path.isdir( config_settings['MULTISEQ_PATH'] + PATHDELIM +  config_settings[key]) :
            eprintf("ERROR: Path for \"%s\" is NOT set properly (or missing) in configuration file \"%s\"\n", key, file)  
            eprintf("ERROR: 3.Currently it is set to \"%s\"\n", config_settings[key] )  
            if globalerrorlogger!=None:
               globalerrorlogger.write("ERROR\tPath for \"%s\" is NOT set properly (or missing) in configuration file \"%s\"\n" %(key, file))  
               globalerrorlogger.write("Currently it is set to \"%s\"\n" %( config_settings[key] )) 
            missingItems.append(key) 
         continue


      # check if the desired file exists. if not, then print a message
      if not path.isfile( config_settings['MULTISEQ_PATH'] + PATHDELIM +  value)\
        and  not path.isfile( config_settings['MULTISEQ_PATH'] + PATHDELIM + config_settings['EXECUTABLES_DIR'] + PATHDELIM + value ) :
           eprintf("ERROR:Path for \"%s\" is NOT set properly (or missing) in configuration file \"%s\"\n", key, file)  
           eprintf("6.Currently it is set to \"%s\"\n", config_settings['MULTISEQ_PATH']+ PATHDELIM + config_settings['EXECUTABLES_DIR'] + PATHDELIM + value ) 
           if globalerrorlogger!=None:
              globalerrorlogger.write("ERROR\tPath for \"%s\" is NOT set properly (or missing) in configuration file \"%s\"\n" %(key, file) )
              globalerrorlogger.write("Currently it is set to \"%s\"\n" %(config_settings['MULTISEQ_PATH'] + value)) 
           missingItems.append(key) 
           continue
     
   stop_execution = False
   for item in missingItems:
      if item in essentialItems:
         eprintf("ERROR\t Essential field in setting %s is missing in configuration file!\n", item)
         if globalerrorlogger!=None:
            globalerrorlogger.write("ERROR\tEssential field in setting %s is missing in configuration file!\n" %(item))
         stop_execution = True

   if stop_execution ==True:
      eprintf("ERROR: Terminating execution due to missing essential  fields in configuration file!\n")
      if globalerrorlogger!=None:
         globalerrorlogger.write("ERROR\tTerminating execution due to missing essential  fields in configuration file!\n")
      exit_process()

   

# This function reads the pipeline configuration file and sets the 
# paths to differenc scripts and executables the pipeline call
def read_pipeline_configuration( file, globalerrorlogger ):
    patternKEYVALUE = re.compile(r'^([^\t\s]+)[\t\s]+\'(.*)\'')
    try:
       configfile = open(file, 'r')
    except IOError:
       eprintf("ERROR :Did not find pipeline config %s!\n", file)
    else:
       lines = configfile.readlines()

    config_settings = {}
    for line in lines:
        if not re.match("#",line) and len(line.strip()) > 0 :
           line = line.strip()
           result = patternKEYVALUE.search(line)
           
           try:
              if len(result.groups()) == 2:
                 fields = result.groups()
              else:
                 eprintf("     The following line in your config settings files is not set up yet\n")
                 eprintf("     Please rerun the pipeline after setting up this line\n")
                 eprintf("     Error in line : %s\n", line)
                 globalerrorlogger(
                      "WARNING\t\n"+\
                      "     The following line in your config settings files is not set up yet\n"+\
                      "     Please rerun the pipeline after setting up this line\n"+\
                      "     Error in line : %s\n" %(line))

                 exit_process()
           except:
                 eprintf("     The following line in your config settings files is not set up yet\n")
                 eprintf("     Please rerun the pipeline after setting up this line\n")
                 eprintf("     Error ine line : %s\n", line)
                 globalerrorlogger(
                      "WARNING\t\n"+\
                      "     The following line in your config settings files is not set up yet\n"+\
                      "     Please rerun the pipeline after setting up this line\n"+\
                      "     Error in line : %s\n" %(line))
                 exit_process()
              
           if PATHDELIM=='\\':
              config_settings[fields[0]] = re.sub(r'/',r'\\',fields[1])   
           else:
              config_settings[fields[0]] = re.sub(r'\\','/',fields[1])   

           
    config_settings['MULTISEQ_PATH'] = config_settings['MULTISEQ_PATH'] + PATHDELIM

    #check_config_settings(config_settings, file, globalerrorlogger);
    config_settings['configuration_file'] = file

    return config_settings

#check for empty values in parameter settings 
def  checkMissingParam_values(params, choices, logger = None):
     reqdCategoryParams = { 
                            'annotation': {'dbs': False}, 
                            'orf_prediction':{}, 
                            'rRNA':{},
                            'multiseq_steps':{}
                         }

     success  = True
     for category in choices:
       for parameter in choices[category]:
         if (not params[category][parameter]) and\
            ( (category in reqdCategoryParams) and\
               (parameter in reqdCategoryParams[category]) and   reqdCategoryParams[category][parameter]) :
            print category, parameter
            print reqdCategoryParams
            print reqdCategoryParams[category]
            eprintf('ERROR: Empty parameter %s of type %s\n'  %(parameter, category))
            eprintf('Please select at least one database for %s\n'  %(category))
            if logger!=None:
               logger.write('ERROR\tEmpty parameter %s of type %s\n'  %(parameter, category))
               logger.write('Please select at least one database for %s\n'  %(category))
            success = False

     return success

# check if all of the multiseq_steps have 
# settings from the valid list [ yes, skip stop, redo]

def  checkParam_values(allcategorychoices, parameters, runlogger = None):
     for category in allcategorychoices:
        for choice in allcategorychoices[category]:
           if choice in parameters: 

             if not parameters[choice] in allcategorychoices[category][choice]:
                 logger.write('ERROR\tIncorrect setting in your parameter file')
                 logger.write('for step %s as %s' %(choice, parameters[choices]))
                 eprintf("ERROR: Incorrect setting in your parameter file" +\
                         "       for step %s as %s", choice, parameters[choices])
                 exit_process()

def checkMetapathsteps(params, runlogger = None):
     choices = { 'multiseq_steps':{}, 'annotation':{}, 'INPUT':{} }

     choices['INPUT']['format']  = ['fasta', 'gbk_unannotated', 'gbk_annotated', 'gff_unannotated', 'gff_annotated']

     choices['annotation']['algorithm'] =  ['last', 'blast'] 

     choices['multiseq_steps']['PREPROCESS_FASTA']   = ['yes', 'skip', 'stop', 'redo']
     choices['multiseq_steps']['ORF_PREDICTION']  = ['yes', 'skip', 'stop', 'redo']
     choices['multiseq_steps']['GFF_TO_AMINO']    = ['yes', 'skip', 'stop', 'redo']
     choices['multiseq_steps']['FILTERED_FASTA']  = ['yes', 'skip', 'stop', 'redo']
     choices['multiseq_steps']['PARSE._BLAST'] = ['yes', 'skip', 'stop', 'redo']
     choices['multiseq_steps']['SCAN_rRNA']   = ['yes', 'skip', 'stop', 'redo']
     choices['multiseq_steps']['STATS_rRNA']  = ['yes', 'skip', 'stop', 'redo']
     choices['multiseq_steps']['ANNOTATE']    = ['yes', 'skip', 'stop', 'redo']

     choices['multiseq_steps']['PATHOLOGIC']  = ['yes', 'skip', 'stop', 'redo']
     choices['multiseq_steps']['GLOBAL_OTUS_PICK']  = ['yes', 'skip', 'stop', 'redo']

     if params['multiseq_steps']:
        checkParam_values(choices, params['multiseq_steps'], runlogger)

     checkparams = {}
     checkparams['annotation'] = []
     checkparams['annotation'].append('dbs') 

     if not checkMissingParam_values(params, checkparams, runlogger):
        exit_process("Missing parameters")


def  copy_fna_faa_gff_orf_prediction( source_files, target_files, config_settings) :

     for source, target in zip(source_files, target_files):  

         sourcefile = open(source, 'r')
         targetfile = open(target, 'w')
         sourcelines = sourcefile.readlines()
         for line in sourcelines:
            fprintf(targetfile, "%s\n", line.strip())

         sourcefile.close()
         targetfile.close()


def run_multiseq(s, globallogger, command_line_params,
                 params, config_settings, status_update_callback):

    # create the job creator object  with params and config
    jobcreator = JobCreator(params, config_settings)

    # jobcreator with create the jobs (as contexts) by looking the information in s
    # and also add them in the context blocks, which is also a variable in s object
    jobcreator.addJobs(s, block_mode=False)


    s.stepslogger.printf("\n\n==============  BEGIN RUN     ==================\n")
    sample_name_banner = "PROCESSING INPUTS " + ' '.join(s.input_files)
    eprintf('#'*len(sample_name_banner) + "\n")
    eprintf( '\n' + sample_name_banner + '\n')

    try:
        # now execute the tasks or contexts in s one by one
        execute_tasks(s, verbose=command_line_params['verbose'], block = 0)
    except:
        pass

    return

