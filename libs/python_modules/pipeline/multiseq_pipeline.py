from __future__ import division




try:
      import traceback, sys, re
      from subprocess import Popen, PIPE, STDOUT
      from os import makedirs, listdir, _exit
      from glob import glob
      from optparse import OptionParser
      from os.path import split, splitext, join, dirname, abspath
      from datetime import datetime

      from libs.python_modules.utils.multiseq_utils import printf, eprintf
      from libs.python_modules.utils.sysutil import getstatusoutput
      import libs.python_scripts  as python_scripts

except:
      print """ Could not load some user defined  module functions"""
      print """ Make sure your typed source RiboCensusrc"""
      print traceback.print_exc(10)
      sys.exit(3)


"""This file contains the metapaths workflow functions which string together 
independent scripts.  """

            
def execute_pipeline_stage(pipeline_command, extra_command = None,  errorlogger = None, runstatslogger = None):
     argv = [ x.strip() for x in pipeline_command.split() ]
     funcname = re.sub(r'.py$','', argv[0])
     funcname = re.sub(r'^.*/','', funcname)
     args = argv[1:] 
     
     if hasattr(python_scripts, funcname):
        methodtocall = getattr(getattr(python_scripts, funcname), funcname)

        if extra_command == None:
           result = methodtocall(args, errorlogger = errorlogger, runstatslogger = runstatslogger)
        else:
           result = methodtocall(args, errorlogger = errorlogger, extra_command = extra_command, runstatslogger = runstatslogger)
     else:
        result = getstatusoutput(pipeline_command)
     return result


def  printList(listName, missingList):
    eprintf("%s:\n", listName)
    for missingItem in missingList:
       eprintf("     %s\n", missingItem)


def execute_tasks(s, verbose = 0, block = 0):
    """Run list of commands, one after another """
    #logger.write("Executing commands.\n\n")
    contextBlocks = s.getContextBlocks()
    contextBlock = contextBlocks[block]

    for c in contextBlock:
        if c.status=='stop':
           print "Stopping!"
           s.stepslogger.write('%s\t%s\n' %(c.name, "STOPPED"))
           return (0,'')

        if verbose >= 0:
             eprintf("\n\n\nEXECUTING STEP : %s [%s]\n", c.name, c.status)
             eprintf("EXECUTING COMMAND : %s\n", ', '.join(c.commands) )

        if verbose >= 1:
             printList('INPUT LIST', c.getInputList())
             printList('OUTPUT LIST', c.getOutputList())


        eprintf("%s" %(c.message))

        if c.status in ['redo']:
            c.removeOutput(s)
            if c.isInputAvailable( errorlogger = s.errorlogger):
               s.stepslogger.write('%s\t%s\n' %(c.name, "RUNNING"))
               result = [ 0, 'Error while executing step ' +  c.name ]
               try:
                  result = execute(s,c)
               except:
                  s.errorlogger.printf("ERROR\t%s\n" ,result[1])
                  result[0] = 1

               if result[0] == 0 :
                  eprintf('..... Redo Success!\n')
                  s.stepslogger.write('%s\t%s\n' %( c.name, "SUCCESS"))
               else:
                  eprintf('..... Failed!\n')
                 # eprintf('%s result \n',  result )
                  s.stepslogger.write('%s\t%s\n' %( c.name, "FAILED"))
            else:
               eprintf('..... Skipping [NO INPUT]!\n')
               if verbose:
                  missingList=c.getMissingList(errorlogger = s.errorlogger)
                  printList('MISSING INPUT LIST', missingList)
                     
               s.stepslogger.write('%s\t%s\n' %( c.name, "MISSING_INPUT"))

        elif c.status in ['yes']:
           if not c.isOutputAvailable():
               if c.isInputAvailable(errorlogger = s.errorlogger):
                  s.stepslogger.write('%s\t%s\n' %(c.name, "RUNNING"))

                  result = [ 0, 'Error while executing  step ' +  c.name ]
                  try:
                     result = execute(s,c)
                  except:
                     s.errorlogger.printf("ERROR\t%s\n" ,result[1])
                     result[0] = 1
   
                  if result[0] == 0 :
                     eprintf('..... Success!\n')
                     s.stepslogger.write('%s\t%s\n' %( c.name, "SUCCESS"))
                  else:
                     eprintf('..... Failed!\n')
                     s.stepslogger.write('%s\t%s\n' %( c.name, "FAILED"))
               else:
                  eprintf('..... Skipping [NO INPUT]!\n')
                  if verbose:
                    missingList=c.getMissingList(errorlogger = s.errorlogger)
                    printList('MISSING INPUT LIST', missingList)

                  s.stepslogger.write('%s\t%s\n' %(c.name, "SKIPPED"))
           else:
               eprintf('..... Already Computed!\n')
               s.stepslogger.write('%s\t%s\n' %( c.name, "ALREADY_COMPUTED"))

        elif c.status in ['skip']:
           eprintf('..... Skipping!\n')
           s.stepslogger.write('%s\t%s\n' %(  c.name, "SKIPPED"))

def execute(s, c):
    result = [ 0, 'Error while executing ' +  c.name ]
    try:
       result=execute_pipeline_stage(c.commands[0], errorlogger= s.errorlogger, runstatslogger = s.runstatslogger)
    except:
       pass

    return result

def print_to_stdout(s):
    print s
    
def no_status_updates(s):
    pass

def get_params_str(params):
    result = []
    for param_id, param_value in params.items():
        result.append('--%s' % (param_id))
        if param_value != None:
            result.append(param_value)
    return ' '.join(result)


## End  workflow and related functions
